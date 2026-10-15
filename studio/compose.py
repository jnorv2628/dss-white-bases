#!/usr/bin/env python3
"""DSS studio: drop a graphic, get every flat mockup.  No AI, fully repeatable.

  python studio/compose.py --design DDS --handle dog-days-society-hoodie \
      --views back,front --colors BLK,WHT --ink auto

Inputs  : art/<DESIGN>/back.png   (transparent PNG, the back graphic)      -- local/private, never committed
          art/<DESIGN>/front.png  (optional small front mark, transparent)
Outputs : mockups/<handle>/NN-<view>-<COLOR>.jpg  +  mockups/<handle>/manifest.json (order, alt text, color map)
--ink   : auto  = light ink on dark garments, dark ink on light garments (monochrome graphics)
          fixed = use the graphic's own colors as drawn
          tonal = garment colour shifted slightly, for embossed/tonal looks
"""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from recolor import garment_mask, recolor, hex_rgb
from mockup import COLORS

BASES = {  # garment -> {view: base file}
    "hoodie": {"front": "BLANK-M-HOODIE-WHITE-v1.jpg", "back": "BLANK-M-HOODIE-WHITE-BACK-v1.jpg"},
    "dog-hoodie-v2": {"front": "BASE-D2-FRONT-v2.jpg", "back": "BASE-D2-BACK-v2.jpg"},
    "hoodie-v2": {"front": "BLANK-M-HOODIE-WHITE-v2.jpg", "back": "BLANK-M-HOODIE-WHITE-BACK-v2.jpg"},
    "zip-hoodie": {"front": "BLANK-M-ZIP-HOODIE-WHITE-v1.jpg", "back": "BLANK-M-ZIP-HOODIE-WHITE-BACK-v1.jpg"},
    "tee": {"front": "BLANK-M-TEE-CREW-WHITE-v2.jpg", "back": "BLANK-M-TEE-CREW-WHITE-BACK-v2.jpg"},
    "w-tee": {"front": "BLANK-W-TEE-CLASSIC-WHITE-v1.jpg", "back": "BLANK-W-TEE-CLASSIC-WHITE-BACK-v1.jpg"},
    "ls-tee": {"front": "BLANK-M-LS-CREW-WHITE-v1.jpg", "back": "BLANK-M-LS-CREW-WHITE-BACK-v1.jpg"},
    "dog-tee": {"front": "BASE-D1-FRONT-v1.jpg", "back": "BASE-D1-BACK-v1.jpg"},
    "dog-hoodie": {"front": "BASE-D2-FRONT-v1.jpg", "back": "BASE-D2-BACK-v1.jpg"},
    "sweatshirt": {"front": "BLANK-M-CREW-SWEAT-WHITE-v1.jpg", "back": "BLANK-M-CREW-SWEAT-WHITE-BACK-v1.jpg"},
    "w-sweatshirt": {"front": "BLANK-W-CREW-SWEAT-WHITE-v1.jpg", "back": "BLANK-W-CREW-SWEAT-WHITE-BACK-v1.jpg"},
}
LIGHT_INK, DARK_INK = (238, 236, 230), (22, 22, 22)


def lum(hexv):
    r, g, b = hex_rgb(hexv)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def get_mask(base_path, cfg):
    cache = os.path.join(ROOT, "studio", "masks", os.path.basename(base_path) + ".png")
    if os.path.exists(cache):                       # hand-fixed or previously approved mask wins
        return Image.open(cache).convert("L")
    img = Image.open(base_path).convert("RGB")
    arr, _ = garment_mask(np.asarray(img, dtype=np.float32), None, cfg.get("ymax"), cfg.get("grow", 0))
    m = Image.fromarray(arr); m.save(cache)
    return m


def place(im, art, box, color_hex, ink, shade):
    a = art.convert("RGBA")
    w = box["w"]; h = int(a.height * w / a.width)
    a = a.resize((w, h), Image.LANCZOS)
    arr = np.asarray(a, dtype=np.float32)
    rgb, alpha = arr[..., :3], arr[..., 3:] / 255.0
    L = lum(color_hex)
    if ink == "auto":                               # monochrome: recolor ink for contrast
        ink_rgb = np.array(LIGHT_INK if L < 0.5 else DARK_INK, dtype=np.float32)
        rgb = np.broadcast_to(ink_rgb, rgb.shape).copy()
    elif ink == "gold":                             # embroidered-gold look: true gold on dark, deeper bronze on light
        if L >= 0.5: rgb = rgb * np.array([0.60, 0.50, 0.38], dtype=np.float32) / 0.82
    elif ink == "tonal":
        t = np.array(hex_rgb(color_hex), dtype=np.float32)
        rgb = np.broadcast_to(np.clip(t * (1.28 if L < 0.5 else 0.86) + (10 if L < 0.5 else 0), 0, 255), rgb.shape).copy()
    x0 = int(box["cx"] - w / 2); y0 = int(box["top"])
    base = np.asarray(im.convert("RGB"), dtype=np.float32)
    H, W = base.shape[:2]
    ys, xs = slice(max(y0, 0), min(y0 + h, H)), slice(max(x0, 0), min(x0 + w, W))
    sy, sx = slice(ys.start - y0, ys.stop - y0), slice(xs.start - x0, xs.stop - x0)
    sh = shade[ys, xs][..., None]                   # let fabric folds show through the print
    ink_px = rgb[sy, sx] * (0.90 + 0.10 * sh)
    al = alpha[sy, sx] * (0.96 if ink != "tonal" else 0.9)
    base[ys, xs] = base[ys, xs] * (1 - al) + ink_px * al
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


def build(design, handle, views, colors, ink, garment="hoodie", out_root="mockups"):
    placements = json.load(open(os.path.join(ROOT, "studio", "placements.json")))
    out = os.path.join(ROOT, out_root, handle); os.makedirs(out, exist_ok=True)
    manifest = {"handle": handle, "design": design, "garment": garment, "images": []}
    n = 0
    for c in colors:
        name, hx, _ = COLORS[c]
        for v in views:
            art_path = os.path.join(ROOT, "art", design, f"{v}.png")
            if not os.path.exists(art_path):
                print(f"skip {v}: no {art_path}"); continue
            base_file = BASES[garment][v]; cfg = dict(placements[base_file])
            ov_path = os.path.join(ROOT, "art", design, "placement.json")   # per-design print box wins
            if os.path.exists(ov_path):
                ov = json.load(open(ov_path))
                if v in ov: cfg[v] = ov[v]
            base_path = os.path.join(ROOT, "img", base_file)
            img = Image.open(base_path).convert("RGB")
            mask = get_mask(base_path, cfg)
            col = recolor(img, mask, hex_rgb(hx))
            g = np.asarray(img.convert("L"), dtype=np.float32)
            shade = np.clip(g / max(np.percentile(g[np.asarray(mask) > 0], 96), 1), 0, 1.05)
            shade = np.asarray(Image.fromarray((shade * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0)), dtype=np.float32) / 255.0
            col = place(col, Image.open(art_path), cfg[v], hx, ink, shade)
            col = col.crop(tuple(cfg["crop"]))
            n += 1
            fn = f"{n:02d}-{v}-{c}.jpg"; col.save(os.path.join(out, fn), quality=95)
            manifest["images"].append({"file": fn, "view": v, "color": c, "color_name": name,
                                       "alt": f"{design} {garment}, {name.lower()}, {v} view"})
            print("wrote", fn)
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=2)
    return manifest


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True); ap.add_argument("--handle", required=True)
    ap.add_argument("--views", default="back,front"); ap.add_argument("--colors", default="BLK,WHT")
    ap.add_argument("--ink", default="auto", choices=["auto", "fixed", "tonal", "gold"])
    ap.add_argument("--garment", default="hoodie")
    a = ap.parse_args()
    build(a.design, a.handle, a.views.split(","), a.colors.split(","), a.ink, a.garment)
