#!/usr/bin/env python3
"""Build the Fox & Fable web logo assets from the original artwork.

Sources (docs/brand-reference/):
  fox-and-fable-logo-original.png  primary lockup: FF monogram with an engraved fox, wordmark,
                                   descriptor, on textured cream paper (median #F0ECE5)
  fox-and-fable-brand-sheet.png    brand sheet; the horizontal light-on-olive lockup is used for the footer

Method: backgrounds are keyed out with a local "un-multiply". Each pixel's alpha is its
contrast against the background relative to the strongest stroke nearby, and its colour is solved
from  pixel = alpha * ink + (1 - alpha) * background.  The paper grain (contrast < ~20) drops out,
fine engraving lines survive. The brand-sheet panel has a vignette, so its background is estimated
locally (grey opening + blur) and the light strokes are keyed against that.
The hero lockup and the og:image keep the original paper (no keying) and sit on the matching cream.

Needs: pip install pillow numpy scipy      Run from the site root:  python3 tools/build-logo-assets.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "docs/brand-reference"
OUT = ROOT / "assets/logo"
PAPER = (240, 236, 229)                     # median of the artwork's paper = hero card / og / icon background
BURN = np.array([77, 52, 32], float)        # "burned into oak" brown for the stamp

# Crop boxes in source pixels (x0, y0, x1, y1), measured from the artwork.
A_LOCKUP = (100, 262, 1170, 1000)           # monogram + wordmark + descriptor
A_MONO = (430, 272, 828, 764)               # FF + fox monogram
B_FOOTER = (80, 690, 815, 876)              # horizontal light lockup on olive (brand sheet)


def key(rgb, bg, sign=1, noise=20.0, floor=140.0):
    """sign=1: dark ink on light bg; sign=-1: light ink on dark bg."""
    d = sign * (bg - rgb).sum(2)
    core = np.maximum(ndimage.maximum_filter(d, size=11), floor)
    a = np.clip((d - noise) / (core - noise), 0, 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        ink = bg - (bg - rgb) / np.maximum(a, 1e-3)[..., None]
    ink = np.clip(np.nan_to_num(ink), 0, 255)
    w = ndimage.gaussian_filter(a, 3) + 1e-6
    fill = np.stack([ndimage.gaussian_filter(a * ink[..., c], 3) / w for c in range(3)], -1)
    return a, np.where(a[..., None] > 0.05, ink, fill)


def resize(a, ink, width, boost=0.0):
    if boost > 0:
        a = np.maximum(a, ndimage.grey_dilation(a, size=(3, 3)) * boost)
    h = round(a.shape[0] * width / a.shape[1])
    r = lambda ch: np.asarray(Image.fromarray(ch.astype(np.float32), "F").resize((width, h), Image.LANCZOS))
    A = np.clip(r(a), 0, 1)
    C = np.stack([r(a * ink[..., c]) / np.maximum(A, 1e-4) for c in range(3)], -1)
    return A, np.clip(C, 0, 255)


def rgba(A, C, gamma=1.0):
    return Image.fromarray(np.dstack([C, np.clip(A, 0, 1) ** gamma * 255]).round().astype(np.uint8), "RGBA")


def save(img, name):
    img.save(OUT / f"{name}.png", optimize=True)
    img.save(OUT / f"{name}.webp", **({"lossless": True, "method": 6} if img.mode == "RGBA" else {"quality": 90, "method": 6}))
    print(name, img.size)


def crop(arr, box):
    x0, y0, x1, y1 = box
    return arr[y0:y1, x0:x1]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    A_img = Image.open(REF / "fox-and-fable-logo-original.png").convert("RGB")
    A = np.asarray(A_img).astype(float)

    # Hero: the original lockup on its own paper (opaque; the card uses the same cream).
    lock = A_img.crop(A_LOCKUP)
    for w in (520, 1040):
        save(lock.resize((w, round(lock.height * w / lock.width)), Image.LANCZOS), f"lockup-{w}")

    # Monogram, keyed to transparency.
    ma, mi = key(crop(A, A_MONO), np.array(PAPER, float))
    mw, mh = ma.shape[1], ma.shape[0]
    for hpx, boost, g in ((52, 0.6, 0.8), (104, 0.3, 0.9), (156, 0, 1.0)):
        save(rgba(*resize(ma, mi, round(mw * hpx / mh), boost), g), f"monogram-{hpx}")
    burn = np.broadcast_to(BURN, mi.shape)
    for w in (110, 220):
        save(rgba(*resize(ma, burn, w, 0.4), 0.85), f"monogram-burn-{w}")

    # Footer: horizontal light lockup from the brand sheet, keyed off its olive vignette.
    B = np.asarray(Image.open(REF / "fox-and-fable-brand-sheet.png").convert("RGB")).astype(float)
    pad = 40
    x0, y0, x1, y1 = B_FOOTER
    reg = B[y0 - pad:y1 + pad, x0 - pad:x1 + pad]
    # Background = the panel with strokes (and their soft drop shadows) masked out, filled by normalized blur.
    rough = np.stack([ndimage.gaussian_filter(ndimage.grey_opening(reg[..., c], size=31), 12) for c in range(3)], -1)
    stroke = ndimage.binary_dilation(np.abs((reg - rough).sum(2)) > 18, iterations=9)
    keep = (~stroke).astype(float); wk = ndimage.gaussian_filter(keep, 20) + 1e-6
    bg = np.stack([ndimage.gaussian_filter(reg[..., c] * keep, 20) / wk for c in range(3)], -1)
    fa, fi = key(reg, bg, sign=-1, noise=28.0, floor=200.0)
    fa, fi = fa[pad:-pad, pad:-pad], fi[pad:-pad, pad:-pad]
    for w, boost, g in ((360, 0.3, 0.9), (720, 0, 1.0)):
        save(rgba(*resize(fa, fi, w, boost), g), f"horizontal-light-{w}")

    # Favicons: keyed monogram on a cream tile; tiny sizes get bolder strokes.
    def mono(h, boost, g):
        return rgba(*resize(ma, mi, round(mw * h / mh), boost), g)
    def tile(size, rounded=True, fill=0.84, boost=0.8, g=0.7):
        t = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=round(size * (0.2 if rounded else 0)), fill=255)
        t.paste(Image.new("RGBA", (size, size), PAPER + (255,)), (0, 0), m)
        f = mono(round(size * fill), boost, g)
        t.alpha_composite(f, ((size - f.width) // 2, (size - f.height) // 2))
        return t
    ico = [tile(s, fill=0.9, boost=1.0, g=0.6) for s in (16, 32, 48)]
    ico[1].save(ROOT / "assets/favicon-32.png", optimize=True)
    ico[2].save(ROOT / "assets/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:2])
    tile(180, rounded=False, fill=0.76, boost=0.3, g=0.9).convert("RGB").save(ROOT / "assets/apple-touch-icon.png", optimize=True)
    for s in (192, 512):
        tile(s, rounded=False, fill=0.72, boost=0.2 if s < 300 else 0, g=0.95).convert("RGB").save(ROOT / f"assets/icon-{s}.png", optimize=True)

    # Open Graph 1200x630: the original lockup on its own paper, canvas extended in the same cream.
    og = Image.new("RGB", (1200, 630), PAPER)
    h = 560; l2 = lock.resize((round(lock.width * h / lock.height), h), Image.LANCZOS)
    og.paste(l2, ((1200 - l2.width) // 2, (630 - h) // 2))
    og.save(ROOT / "assets/og-image.png", optimize=True)
    print("og", og.size, l2.size)


if __name__ == "__main__":
    main()
