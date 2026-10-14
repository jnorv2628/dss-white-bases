#!/usr/bin/env python3
"""Dog Days Society hoodie: recolor the approved WHITE base photos and print the arched wordmark on the back.
  python society.py --out mockups/dog-days-society-hoodie --colors BLK,WHT"""
import argparse, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recolor import garment_mask, recolor, hex_rgb
from mockup import COLORS

F = "/usr/share/fonts/truetype/dejavu/"

def wordmark(size, ink, y0=850, r=1700, x0=None, line2="S  O  C  I  E  T  Y"):
    W, H = size; x0 = x0 or W // 2 - 10
    f1 = ImageFont.truetype(F + "DejaVuSerif-Bold.ttf", 104)
    f2 = ImageFont.truetype(F + "DejaVuSerifCondensed.ttf", 40)
    f3 = ImageFont.truetype(F + "DejaVuSerifCondensed.ttf", 24)
    lay = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    col = ink + (255,)
    ws = [d.textlength(c, font=f1) * 1.1 for c in "DOG DAYS"]; ang = -sum(ws) / r / 2
    for c, w in zip("DOG DAYS", ws):
        ang += w / r / 2
        t = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); ImageDraw.Draw(t).text((110, 110), c, font=f1, fill=col, anchor="mm")
        t = t.rotate(-math.degrees(ang), resample=Image.BICUBIC)
        lay.alpha_composite(t, (int(x0 + r * math.sin(ang) - 110), int(y0 - r * math.cos(ang) + r - 110)))
        ang += w / r / 2
    d.text((x0, y0 + 135), line2, font=f2, fill=col, anchor="mm")
    d.line([(x0 - 130, y0 + 180), (x0 + 130, y0 + 180)], fill=col, width=2)
    d.text((x0, y0 + 212), "LOS ANGELES", font=f3, fill=col, anchor="mm")
    return lay

def build(base, color, out, text=False, ymax=None):
    img = Image.open(base).convert("RGB")
    arr, _ = garment_mask(np.asarray(img, dtype=np.float32), None, ymax)
    mask = Image.fromarray(arr)
    name, hx, _ = COLORS[color]
    im = recolor(img, mask, hex_rgb(hx))   # WHT too, so front and back share one white
    W, H = im.size
    im = im.crop((0, 0, W, 1690))                      # drop the baked-in file label
    if text:
        ink = (22, 22, 22) if color in ("WHT", "BNE", "OAT") else (238, 236, 230)
        lay = wordmark((W, 1690), ink)
        im = im.convert("RGBA"); im.alpha_composite(lay); im = im.convert("RGB")
    im.save(out, quality=95)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--colors", default="BLK,WHT")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    for c in a.colors.split(","):
        build("img/BLANK-M-HOODIE-WHITE-v1.jpg", c, f"{a.out}/01-front-{c}.jpg", ymax=1565)
        build("img/BLANK-M-HOODIE-WHITE-BACK-v1.jpg", c, f"{a.out}/02-back-{c}.jpg", text=True)
        print(c, "ok")
