#!/usr/bin/env python3
"""Prepare photos uploaded through Pages CMS, and keep _data/image_sizes.yml current.

Run by .github/workflows/site.yml on every push to main (and safe to run locally):

    python3 tools/media/process_uploads.py

For each new or replaced original in uploads/ (jpg, jpeg, png, webp, heic, heif) it:
  1. applies the camera's rotation, then removes ALL metadata (EXIF, GPS location, camera, XMP, comments);
  2. converts the colors to sRGB (embedded ICC profiles such as Display P3 are converted, then dropped);
  3. shrinks it so the longest side is at most 2000 px (never enlarges);
  4. re-saves the original in place (iPhone HEIC/HEIF become .jpg, and every reference to the old
     name in _data/ and _journal/ is updated);
  5. writes a .webp copy next to it, plus -card-480 / -card-960 (.jpg + .webp) thumbnails that the
     page templates use for tiles and cards.
Then it rewrites _data/image_sizes.yml (pixel sizes of every image under assets/images and uploads),
which the templates use for width/height attributes.

uploads/.processed.json remembers what was done (sha256 of each processed original and the files made
from it) so nothing is processed twice, and derived files are removed when their original is deleted.
"""
import hashlib, io, json, os, re, sys
from pathlib import Path
from PIL import Image, ImageCms, ImageOps

try:
    import pillow_heif  # optional: only needed for iPhone HEIC/HEIF uploads
    pillow_heif.register_heif_opener()
except Exception:  # pragma: no cover
    pillow_heif = None

ROOT = Path(__file__).resolve().parents[2]
UPLOADS = ROOT / "uploads"
MANIFEST = UPLOADS / ".processed.json"
SIZES = ROOT / "_data" / "image_sizes.yml"
MAX_SIDE = 2000
CARD_WIDTHS = (480, 960)
ORIGINAL_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
DERIVED_RE = re.compile(r"-card-(480|960)\.(jpg|webp)$")
SRGB = ImageCms.createProfile("sRGB")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def to_srgb(im: Image.Image) -> Image.Image:
    has_alpha = im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info)
    mode = "RGBA" if has_alpha else "RGB"
    icc = im.info.get("icc_profile")
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            inp = im if im.mode in ("RGB", "RGBA", "CMYK", "L") else im.convert(mode)
            return ImageCms.profileToProfile(inp, src, SRGB, outputMode=mode)
        except Exception as e:  # unreadable profile: fall back to a plain conversion
            print(f"  ! could not use the color profile ({e}); converting without it")
    return im.convert(mode)


def clean(im: Image.Image) -> Image.Image:
    """Rotate per EXIF, convert to sRGB, and return a fresh image with no metadata attached."""
    im = to_srgb(ImageOps.exif_transpose(im))
    bare = Image.new(im.mode, im.size)
    bare.paste(im)
    return bare


def flatten(im: Image.Image) -> Image.Image:
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, (244, 239, 230))  # parchment, matches the site background
        bg.paste(im, mask=im.split()[3])
        return bg
    return im.convert("RGB")


def save(im: Image.Image, path: Path):
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        flatten(im).save(path, "JPEG", quality=85, optimize=True, progressive=True)
    elif ext == ".png":
        im.save(path, "PNG", optimize=True)
    elif ext == ".webp":
        im.save(path, "WEBP", quality=82, method=6)
    else:
        raise ValueError(path)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def replace_refs(old: str, new: str):
    for folder in ("_data", "_journal"):
        for f in (ROOT / folder).rglob("*"):
            if f.is_file() and f.suffix in (".yml", ".yaml", ".md"):
                t = f.read_text(encoding="utf-8")
                if old in t:
                    f.write_text(t.replace(old, new), encoding="utf-8")
                    print(f"  updated reference in {rel(f)}")


def process(src: Path, manifest: dict) -> None:
    print(f"- {rel(src)}")
    with Image.open(src) as im0:
        im0.load()
        im = clean(im0)
    if max(im.size) > MAX_SIDE:
        im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    target = src
    if src.suffix.lower() in (".heic", ".heif"):
        target = src.with_suffix(".jpg")
        n = 2
        while target.exists():
            target = src.with_name(f"{src.stem}-{n}.jpg"); n += 1
    save(im, target)
    if target != src:
        src.unlink()
        for prefix in ("/", ""):
            replace_refs(prefix + rel(src), prefix + rel(target))
        manifest["originals"].pop(src.name, None)
    made = []
    if target.suffix.lower() != ".webp":
        w = target.with_suffix(".webp"); save(im, w); made.append(w.name)
    for cw in CARD_WIDTHS:
        c = im.copy()
        if c.width > cw:
            c = c.resize((cw, round(c.height * cw / c.width)), Image.LANCZOS)
        for ext in (".jpg", ".webp"):
            out = target.with_name(f"{target.stem}-card-{cw}{ext}"); save(c, out); made.append(out.name)
    manifest["originals"][target.name] = {"sha256": sha256(target), "derived": made}
    print(f"  saved {target.name} ({im.width}x{im.height}) + {', '.join(made)}")


def run_uploads():
    UPLOADS.mkdir(exist_ok=True)
    manifest = {"originals": {}}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
        manifest.setdefault("originals", {})
    derived_names = {d for v in manifest["originals"].values() for d in v.get("derived", [])}
    changed = False
    for f in sorted(UPLOADS.iterdir()):
        if not f.is_file() or f.name.startswith(".") or f.suffix.lower() not in ORIGINAL_EXT:
            continue
        if f.name in derived_names or DERIVED_RE.search(f.name):
            continue
        rec = manifest["originals"].get(f.name)
        if rec and rec.get("sha256") == sha256(f):
            continue
        try:
            process(f, manifest); changed = True
        except Exception as e:
            print(f"  ! skipped {f.name}: {e}")
    # Remove files made from originals that have since been deleted.
    for name in list(manifest["originals"]):
        if not (UPLOADS / name).exists():
            for d in manifest["originals"][name].get("derived", []):
                p = UPLOADS / d
                if p.exists():
                    p.unlink(); print(f"- removed {d} (its original {name} was deleted)")
            del manifest["originals"][name]; changed = True
    if changed or not MANIFEST.exists():
        MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def write_sizes():
    lines = ["# Generated by tools/media/process_uploads.py. Do not edit by hand.",
             "# Pixel size (width, height) of every image, used for width/height attributes.", ""]
    for folder in (ROOT / "assets" / "images", UPLOADS):
        if not folder.exists():
            continue
        for f in sorted(folder.rglob("*")):
            if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                try:
                    with Image.open(f) as im:
                        lines.append(f'"{rel(f)}": [{im.width}, {im.height}]')
                except Exception:
                    pass
    new = "\n".join(lines) + "\n"
    if not SIZES.exists() or SIZES.read_text() != new:
        SIZES.write_text(new)
        print(f"updated {rel(SIZES)}")


if __name__ == "__main__":
    if "--sizes-only" not in sys.argv:
        run_uploads()
    write_sizes()
