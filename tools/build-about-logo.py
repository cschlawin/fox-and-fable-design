#!/usr/bin/env python3
"""Build the About-page "Meet the Designer" logo assets from the original artwork.

Reuses the keying helpers in build-logo-assets.py but writes only the files below, so the
hand-edited header/footer logos and og-image are left alone.

  assets/logo/lockup-descriptor-{400,800}.{png,webp}  full lockup incl. "DESIGN + CONSTRUCTION", transparent
  assets/logo/monogram-watermark-560.webp             FF + fox monogram, transparent (faded via CSS)

Run from the site root:  python3 tools/build-about-logo.py
"""
import importlib.util
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bla", ROOT / "tools/build-logo-assets.py")
bla = importlib.util.module_from_spec(spec); spec.loader.exec_module(bla)

A = np.asarray(Image.open(bla.REF / "fox-and-fable-logo-original.png").convert("RGB")).astype(float)
bg = np.array(bla.PAPER, float)

la, li = bla.key(bla.crop(A, bla.A_LOCKUP), bg)
for w, boost, g in ((400, 0.3, 0.9), (800, 0, 1.0)):
    bla.save(bla.rgba(*bla.resize(la, li, w, boost), g), f"lockup-descriptor-{w}")

ma, mi = bla.key(bla.crop(A, bla.A_MONO), bg)
img = bla.rgba(*bla.resize(ma, mi, round(ma.shape[1] * 560 / ma.shape[0])), 1.0)
img.save(bla.OUT / "monogram-watermark-560.webp", lossless=True, method=6)
print("monogram-watermark-560", img.size)
