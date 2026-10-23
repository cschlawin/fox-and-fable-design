#!/usr/bin/env python3
"""Extract the faint fox line sketch (bottom-left accent) from Cody's "Meet the Designer" graphic.

No standalone file of this fox sketch exists in our brand art, so (per Cody) it is copied from the graphic.
The graphic itself is not in the repo; pass its path:  python3 tools/extract-meet-fox.py /path/to/graphic.png
Writes assets/images/about/meet-fox-sketch.{png,webp}: taupe ink on transparency, no metadata.

Method: local background = grey closing (removes the thin sketch lines) + blur; alpha = contrast against it.
Darker strokes (the "Jessica" signature, caption text, photo frame) are masked out, and the photo/caption
areas beside the fox are cleared with hand-measured boxes.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(float)
c = im[880:1380, 0:300]                                  # bottom-left corner of the 1140x1380 graphic
L = c.mean(2)
bg = np.stack([ndimage.gaussian_filter(ndimage.grey_closing(c[..., k], size=15), 4) for k in range(3)], -1)
a = np.clip(((bg - c).sum(2) - 12) / 110, 0, 1)
a[ndimage.binary_dilation(L < 160, iterations=4)] = 0   # signature, caption text, frame
H, W = a.shape; yy, xx = np.mgrid[0:H, 0:W]
kill = (((yy < 100) & (xx > 105)) | ((yy < 170) & (xx > 155)) | ((yy < 140) & (xx >= 124)) | ((yy < 45) & (xx < 40))
        | ((yy < 185) & (xx > 185)) | ((xx > 200) & (yy < 425)) | ((xx > 125) & (yy > 225) & (yy < 425)))
a[kill] = 0
lab, n = ndimage.label(a > 0.08)
sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
a[np.isin(lab, 1 + np.where(sizes < 12)[0])] = 0
ink = np.array([150, 132, 115.0])
img = Image.fromarray(np.dstack([np.broadcast_to(ink, c.shape), a * 255]).astype(np.uint8), "RGBA")
bb = img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
img = img.crop((0, bb[1], bb[2], img.height))
out = ROOT / "assets/images/about/meet-fox-sketch"
img.save(f"{out}.png", optimize=True)
img.save(f"{out}.webp", quality=88, method=6, alpha_quality=90)
print(img.size)
