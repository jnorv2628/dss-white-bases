#!/usr/bin/env python3
"""DSS recolor: make every color from ONE approved WHITE mockup. No Meta needed for colors.

  python recolor.py --in white-front.jpg --colors BLK,BNE,OLV,PLM --out out/colors
  python recolor.py --in white-front.jpg --colors ALL --out out/colors

How it works: finds the garment (everything that is not the #E9E4D8 backdrop), keeps all of the
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


def garment_mask(rgb, tol=None, ymax=None, grow=0):
    """GrabCut at 1/3 scale (fast), seeded from the backdrop colour, then a brightness rescue so lit white
    fabric at the hood collar / shoulders is not dropped, then upsampled with a soft edge."""
    import cv2
    from scipy import ndimage as ndi
    full = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2BGR)
    FH, FW = full.shape[:2]
    img = cv2.resize(full, (FW // 3, FH // 3), interpolation=cv2.INTER_AREA)
    H, W = img.shape[:2]
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    ring = np.zeros((H, W), bool); ring[:16] = ring[:, :16] = ring[:, -16:] = True
    bgc = np.median(lab[ring], 0)
    dist = np.linalg.norm(lab - bgc, axis=2)
    m = np.full((H, W), cv2.GC_PR_BGD, np.uint8)
    m[dist > 6] = cv2.GC_PR_FGD
    m[ring] = cv2.GC_BGD
    m[ndi.binary_erosion(ndi.binary_fill_holes(dist > 14), iterations=8)] = cv2.GC_FGD
    bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
    cv2.grabCut(img, m, None, bg, fg, 6, cv2.GC_INIT_WITH_MASK)
    k = (m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD)
    k = ndi.binary_fill_holes(k)
    lb, n = ndi.label(k)
    if n == 0:
        raise SystemExit("No garment found.")
    k = lb == (1 + int(np.argmax(ndi.sum(k, lb, range(1, n + 1)))))
    # rescue: bright (lit white fabric) pixels hugging the mask that grabcut dropped
    L = lab[..., 0]
    # backdrop brightness model (quadratic fit on the border ring); fabric lit brighter than the backdrop is garment
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    A = np.stack([np.ones_like(xx), xx / W, yy / H, (xx / W) ** 2, (yy / H) ** 2, (xx / W) * (yy / H)], -1)
    co = np.linalg.lstsq(A[ring], L[ring], rcond=None)[0]
    bgL = A @ co
    B = lab[..., 2]
    cb = np.linalg.lstsq(A[ring], B[ring], rcond=None)[0]
    bgB = A @ cb                      # garment is neutral/cool, backdrop is warm
    near = ndi.binary_dilation(k, iterations=14)
    k = k | (near & ((L > bgL + 4) | (B < bgB - 2.5)))
    k = ndi.binary_closing(k, iterations=3); k = ndi.binary_fill_holes(k)
    k = ndi.binary_opening(k, iterations=2)
    if grow:
        k = ndi.binary_dilation(k, iterations=grow)
    if ymax:                      # floor / label below the garment hem
        k[int(ymax / 3):] = False
        k = ndi.binary_opening(k, iterations=3)
    mu = cv2.resize(k.astype(np.uint8) * 255, (FW, FH), interpolation=cv2.INTER_LINEAR)
    mu = cv2.GaussianBlur(mu, (0, 0), 4.0)
    edge = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    return (mu > 127).astype(np.uint8) * 255, np.median(edge, axis=0)


def garment_mask_edges(rgb, tol=10):
    """Edge-based mask: the smooth backdrop connects to the border; the garment is what its outline encloses.
    Better than grabcut when the fabric is nearly the same colour as the backdrop (e.g. the cream front base)."""
    from scipy import ndimage as ndi
    lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    lum = ndi.gaussian_filter(lum, 1.0)
    gy, gx = np.gradient(lum)
    edges = np.hypot(gx, gy) > (tol / 4.0)
    edges = ndi.binary_dilation(edges, iterations=3)
    lab, n = ndi.label(~edges)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    keep = ~np.isin(lab, border[border > 0])
    keep = ndi.binary_erosion(keep, iterations=3)
    keep = ndi.binary_fill_holes(keep)
    l2, n2 = ndi.label(keep)
    if n2 == 0:
        raise SystemExit("No garment found.")
    keep = l2 == (1 + int(np.argmax(ndi.sum(keep, l2, range(1, n2 + 1)))))
    keep = ndi.binary_dilation(keep, iterations=1)
    return keep.astype(np.uint8) * 255, None


def recolor(img, mask, target, strength=1.0):
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32)[..., None] / 255.0
    lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    g = lum[np.asarray(mask) > 0]
    ref = np.percentile(g, 96)  # brightest lit fabric maps to the exact target color
    ratio = np.clip(lum / ref, 0, 1.08)[..., None]
    tl = float(target @ np.array([0.299, 0.587, 0.114], dtype=np.float32)) / 255.0
    lift = 46.0 * (1.0 - tl) ** 3  # dark garments: keep folds/texture visible
    out_g = target[None, None, :] * ratio + (ratio ** 2.2) * lift
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
    ap.add_argument("--ymax", type=int, help="ignore everything below this row (floor/label under the hem)")
    ap.add_argument("--grow", type=int, default=0, help="expand the cut-out by N small steps if a lit edge is being missed")
    ap.add_argument("--name", help="file stem for outputs (default: input file name)")
    a = ap.parse_args()

    img = Image.open(a.src).convert("RGB")
    rgb = np.asarray(img, dtype=np.float32)
    if a.mask:
        mask = Image.open(a.mask).convert("L").resize(img.size)
    else:
        arr, bg = garment_mask(rgb, a.tol, a.ymax, a.grow)
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
