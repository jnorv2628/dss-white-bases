#!/usr/bin/env python3
"""DSS recolor: make every color from ONE approved WHITE mockup. No Meta needed for colors.

  python recolor.py --in white-front.jpg --colors BLK,BNE,OLV,PLM --out out/colors
  python recolor.py --in white-front.jpg --colors ALL --out out/colors

How it works: finds the garment (everything that is not the #E9E9E7 backdrop), keeps all of the
original shading, folds and texture, and tints the garment to the exact color-master hex.
The backdrop and soft floor shadow are left untouched. A mask preview is written next to the
outputs so you can check the cut-out before you use the files.

Tonal marks and graphics print in the fabric color, so they recolor with the garment.
Graphics that must stay a fixed color (e.g. the white drip lettering) are NOT handled here:
use --keep-mask to protect a region, or place those on after recoloring.
"""
import argparse, os, sys
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mockup import COLORS  # single source of truth: DSS-COLOR-MASTER


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def garment_mask(rgb, tol):
    """Garment = everything enclosed by the garment outline. The backdrop and its soft floor shadow are smooth
    (no sharp edges) and connect to the image border, so they are found by flood-filling the low-gradient area
    from the border; the garment is what is left. `tol` is the edge sensitivity (lower = catches fainter outlines)."""
    from scipy import ndimage as ndi
    lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    lum = ndi.gaussian_filter(lum, 1.0)
    gy, gx = np.gradient(lum)
    mag = np.hypot(gx, gy)
    edges = mag > (tol / 4.0)
    edges = ndi.binary_dilation(edges, iterations=3)           # seal small gaps in faint outlines
    lab, n = ndi.label(~edges)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, border[border > 0])
    keep = ~bg
    keep = ndi.binary_erosion(keep, iterations=3)               # undo the dilation
    keep = ndi.binary_fill_holes(keep)
    lab2, n2 = ndi.label(keep)
    if n2 == 0:
        raise SystemExit("No garment found. Try a smaller --tol.")
    sizes = ndi.sum(keep, lab2, range(1, n2 + 1))
    keep = lab2 == (1 + int(np.argmax(sizes)))
    keep = ndi.binary_dilation(keep, iterations=1)
    edge = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    return keep.astype(np.uint8) * 255, np.median(edge, axis=0)


def recolor(img, mask, target, strength=1.0):
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32)[..., None] / 255.0
    lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    g = lum[np.asarray(mask) > 0]
    ref = np.percentile(g, 96)  # brightest lit fabric maps to the exact target color
    ratio = np.clip(lum / ref, 0, 1.08)[..., None]
    out_g = target[None, None, :] * ratio
    out_g = np.clip(out_g, 0, 255)
    out = rgb * (1 - m * strength) + out_g * (m * strength)
    return Image.fromarray(out.astype(np.uint8))


def main():
    ap = argparse.ArgumentParser(description="DSS recolor from an approved white mockup")
    ap.add_argument("--in", dest="src", required=True, help="approved WHITE mockup image")
    ap.add_argument("--colors", default="ALL", help="comma list of color codes, or ALL")
    ap.add_argument("--out", default="out/colors")
    ap.add_argument("--tol", type=int, default=10, help="outline sensitivity (lower = catches fainter outlines, raise if the cut-out leaks into the backdrop)")
    ap.add_argument("--mask", help="optional hand-made mask PNG (white = garment) to use instead of auto")
    ap.add_argument("--name", help="file stem for outputs (default: input file name)")
    a = ap.parse_args()

    img = Image.open(a.src).convert("RGB")
    rgb = np.asarray(img, dtype=np.float32)
    if a.mask:
        mask = Image.open(a.mask).convert("L").resize(img.size)
    else:
        arr, bg = garment_mask(rgb, a.tol)
        mask = Image.fromarray(arr)
    os.makedirs(a.out, exist_ok=True)
    stem = a.name or os.path.splitext(os.path.basename(a.src))[0]
    prev = Image.blend(img, Image.merge("RGB", (mask, Image.new("L", img.size, 0), Image.new("L", img.size, 0))), 0.45)
    prev.save(os.path.join(a.out, f"{stem}__MASK-CHECK.jpg"), quality=90)

    codes = list(COLORS) if a.colors.upper() == "ALL" else [c.strip().upper() for c in a.colors.split(",") if c.strip()]
    bad = [c for c in codes if c not in COLORS]
    if bad:
        sys.exit(f"Unknown color code(s): {', '.join(bad)}")
    for c in codes:
        name, hx, _ = COLORS[c]
        fn = os.path.join(a.out, f"{stem}__{c}.jpg")
        recolor(img, mask, hex_rgb(hx)).save(fn, quality=95)
        print(f"{c:4s} {name:10s} {hx}  -> {fn}")
    print(f"Mask check (red = garment): {os.path.join(a.out, stem + '__MASK-CHECK.jpg')}")


if __name__ == "__main__":
    main()
