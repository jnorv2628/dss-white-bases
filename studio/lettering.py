#!/usr/bin/env python3
"""Arched distressed lettering art (white ink, transparent PNG) in the ASDMS style.
  python studio/lettering.py --out art/RBFS --text "RESTING BITCH FACE SOCIETY" --sub "LOS ANGELES"
"""
import argparse, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf"

def arched(text, sub, out, society=None, size=170, radius=2700, distress=0.10, seed=3, stretch=1.55):
    font = ImageFont.truetype(BOLD, size); fsub = ImageFont.truetype(BOLD, int(size * (0.36 if society else 0.52))); fsoc = ImageFont.truetype(BOLD, int(size * 0.62))
    widths = [font.getlength(c) * 0.93 + size * 0.0 for c in text]; total = sum(widths)
    span = total / radius; W = int(total * 1.15 + 200); H = int(size * 3.4 + radius * (1 - math.cos(span / 2)))
    cv = Image.new("L", (W, H), 0); cx = W / 2; cy = size * 1.3 + radius
    a = -span / 2
    for c, w in zip(text, widths):
        mid = a + (w / radius) / 2; a += w / radius
        if c == " ": continue
        g = Image.new("L", (int(size * 1.6), int(size * 1.6)), 0)
        ImageDraw.Draw(g).text((g.width / 2, g.height / 2), c, font=font, fill=255, anchor="mm")
        g = g.resize((g.width, int(g.height * stretch)), Image.BICUBIC).crop((0, int(g.height * stretch / 2 - g.height / 2), g.width, int(g.height * stretch / 2 + g.height / 2)))
        g = g.rotate(-math.degrees(mid), resample=Image.BICUBIC, expand=False)
        x = cx + radius * math.sin(mid) - g.width / 2; y = cy - radius * math.cos(mid) - g.height / 2 + size * 0.0
        cv.paste(Image.new("L", g.size, 255), (int(x), int(y)), g)
    d = ImageDraw.Draw(cv)
    if society:                                   # SOCIETY under the arch, spaced; LOS ANGELES smaller under it
        ty = size * 1.3 + size * 1.05
        spaced = " ".join(society)
        d.text((cx, ty), spaced, font=fsoc, fill=255, anchor="mm")
        if sub: d.text((cx, ty + size * 0.62), sub, font=fsub, fill=255, anchor="mm")
    elif sub:
        d.text((cx, size * 1.3 + size * 1.0 + radius * (1 - math.cos(span / 2)) * 0.5), sub, font=fsub, fill=255, anchor="mm")
    arr = np.asarray(cv, dtype=np.float32) / 255.0
    rs = np.random.RandomState(seed)
    n = np.asarray(Image.fromarray((rs.rand(H, W) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)), dtype=np.float32) / 255.0
    n2 = np.asarray(Image.fromarray((rs.rand(H // 6 + 1, W // 6 + 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2)), dtype=np.float32) / 255.0
    wear = (n > 0.60) | ((n2 > 0.62) & (n > 0.52))
    arr[wear] *= 0.0
    al = (arr * 255).astype(np.uint8)
    ys, xs = np.where(al > 40); al = al[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    rgba = np.zeros(al.shape + (4,), np.uint8); rgba[..., :3] = 240; rgba[..., 3] = al
    os.makedirs(os.path.dirname(out), exist_ok=True); Image.fromarray(rgba).save(out); return rgba.shape

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--text", required=True)
    ap.add_argument("--sub", default="LOS ANGELES"); ap.add_argument("--society", default=None); a = ap.parse_args()
    print(arched(a.text, a.sub, os.path.join(a.out, "back.png"), a.society))
