#!/usr/bin/env python3
"""Prep a photo for ASCII conversion: cut background, boost local contrast, composite on white.

Run once per photo (needs the heavy libs). Output: source-prepped.png (grayscale).
    python scripts/prep_photo.py source-photo.jpg
"""
import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
OUT = "source-prepped.png"

# 1. isolate the subject — a flat, busy background is what makes ASCII portraits noisy
img = Image.open(SRC).convert("RGBA")
cut = remove(img).convert("RGBA")
arr = np.array(cut)
alpha = arr[:, :, 3]

# 2. composite the subject onto pure white (white -> blank end of the ramp)
rgb = arr[:, :, :3].astype(np.float32)
a = (alpha / 255.0)[:, :, None]
comp = (rgb * a + 255.0 * (1.0 - a)).astype(np.uint8)

# 3. CLAHE gives a flatly-lit face real highlights and shadows
gray = cv2.cvtColor(comp, cv2.COLOR_RGB2GRAY)
clahe = cv2.createCLAHE(clipLimit=2.4, tileGridSize=(8, 8))
enh = clahe.apply(gray)

# 4. force everything outside the subject back to pure white
enh[alpha < 20] = 255

Image.fromarray(enh).save(OUT)
print(f"wrote {OUT}  ({enh.shape[1]}x{enh.shape[0]})  subject px: {(alpha>20).sum()}")
