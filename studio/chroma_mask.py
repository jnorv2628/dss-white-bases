#!/usr/bin/env python3
"""Mask for white garments on the warm backdrop: Lab chroma threshold (shadow-proof).
usage: python studio/chroma_mask.py img/BASE.jpg [...]  -> studio/masks/<name>.png"""
import sys, os, cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def mask(path):
    bgr = cv2.imread(path); lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    ch = np.sqrt((lab[...,1]-128)**2 + (lab[...,2]-128)**2)
    h, w = ch.shape
    bg = np.median(np.concatenate([ch[:40,:40].ravel(), ch[:40,-40:].ravel()]))
    thr = (bg + 1.0) / 2.0 if bg > 2 else 2.2
    L = lab[...,0]; bgL = np.median(L[:40,:40])
    m = (((ch < thr) | (L > bgL + 7)) ).astype(np.uint8)*255   # low chroma OR clearly brighter than backdrop
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k)
    ff = m.copy(); cv2.floodFill(ff, np.zeros((h+2,w+2),np.uint8),(0,0),255)
    m = m | cv2.bitwise_not(ff)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(m)
    big = st[1:,4].max()
    m = np.isin(lbl, [i for i in range(1,n) if st[i,4] > 0.02*big]).astype(np.uint8)*255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(61,61)))
    ff = m.copy(); cv2.floodFill(ff, np.zeros((h+2,w+2),np.uint8),(0,0),255)
    m = m | cv2.bitwise_not(ff)
    m = cv2.medianBlur(m,21); m = cv2.GaussianBlur(m,(0,0),1.1)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    return m
if __name__ == "__main__":
    for p in sys.argv[1:]:
        out = os.path.join(ROOT,"studio","masks",os.path.basename(p)+".png")
        cv2.imwrite(out, mask(p)); print("mask", out)
