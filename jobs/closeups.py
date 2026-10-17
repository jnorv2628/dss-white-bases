#!/usr/bin/env python3
"""Generate close-up / material / hardware Meta jobs for every live Shopify product.
Reads shopify_products.csv. Writes queue.csv (merge, keeps existing rows) and shopify_map.csv.
Output filename code:  <handle>__<SHOT>__v1.jpg   -> attach script parses handle + shot, so no manual matching.
"""
import csv, os, sys
R = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(R)
B = "blanks/white/"
STD = ("Same exact product, same color, plain neutral light-gray seamless studio background, solid #E9E9E7, no gradient, "
       "true neutral white balance with no blue cast and no warm or cream cast, soft even light from above, soft contact shadow. "
       "No text, no caption, no label, no new logos.")

# shot code -> (alt-text label, prompt body with {c} color and {m} material), gallery order
SHOTS = {
 "TEXTURE": ("fabric close-up", "Tight macro close-up of the {m} on this exact garment, filling the frame, weave or knit and stitching visible, soft raking light so the hand and weight of the fabric show.", 1),
 "NECK":    ("neckline detail", "Close-up of the neckline and collar construction on this exact garment: ribbing, seams and stitching, shallow depth of field.", 2),
 "HOOD":    ("hood detail", "Close-up of the hood opening, eyelets and stitched edge on this exact garment, shallow depth of field.", 2),
 "CUFF":    ("cuff detail", "Close-up of the ribbed cuff and sleeve seam on this exact garment, lying flat, soft light.", 3),
 "HEM":     ("hem detail", "Close-up of the bottom hem: stitching and ribbing or hem finish on this exact garment, lying flat, soft light.", 4),
 "SLEEVE":  ("sleeve detail", "Close-up of the sleeve hem and shoulder seam on this exact garment, lying flat, soft light.", 3),
 "WAIST":   ("waistband detail", "Close-up of the waistband, stitching and any drawcord or elastic on this exact garment, shallow depth of field.", 2),
 "SEAM":    ("seam and stretch", "Close-up of the flatlock seam and stretch of the fabric on this exact garment, soft light.", 3),
 "DRAWSTRING": ("drawstring hardware", "Sharp close-up of the drawstring end and metal eyelet (matte tonal metal, no shiny gold) on this exact garment, shallow depth of field.", 5),
 "ZIPPER":  ("zipper hardware", "Sharp close-up of the zipper pull and teeth (matte tonal metal, no shiny gold) on this exact garment, shallow depth of field.", 5),
 "BUTTON":  ("button hardware", "Sharp close-up of the button (shape only, no text, antiqued matte metal, not shiny gold) and buttonhole stitching on this exact garment, shallow depth of field.", 5),
 "SNAP":    ("snap hardware", "Sharp close-up of the snap closure on the placket (matte tonal metal) on this exact garment, shallow depth of field.", 5),
 "LAPEL":   ("lapel detail", "Close-up of the notch lapel and stitched edge on this exact garment, soft light.", 2),
 "DETAIL":  ("stitching and leather", "Close-up of the stitching at the toe and the leather grain of this exact shoe.", 1),
 "HARDWARE":("hardware", "Close-up of the buckle, ring, eyelets or heel counter of this exact product, antiqued matte metal if any, no shiny gold.", 5),
 "SOLE":    ("sole", "Show this exact shoe in view of the sole, bottom up.", 6),
 "SIDE":    ("side profile", "Show this exact shoe in pure side profile.", 4),
 "LEATHER": ("leather grain", "Tight macro close-up of the leather grain and edge stitching on this exact product, soft natural light.", 1),
 "CLOSURE": ("closure detail", "Close-up of the closure and ribbed edge on this exact garment, lying flat, soft light.", 3),
}
FAMS = {  # family -> (base image, shots, material phrase)
 "hoodie":   (B+"BLANK-M-HOODIE-WHITE-v1.jpg", ["TEXTURE","HOOD","CUFF","HEM","DRAWSTRING"], "heavyweight brushed-back cotton fleece"),
 "zip":      (B+"BLANK-M-ZIP-HOODIE-WHITE-v1.jpg", ["TEXTURE","ZIPPER","CUFF","HEM"], "heavyweight brushed-back cotton fleece"),
 "sweat":    (B+"BLANK-M-CREW-SWEAT-WHITE-v1.jpg", ["TEXTURE","NECK","CUFF","HEM"], "heavyweight brushed-back cotton fleece"),
 "tee":      (B+"BLANK-M-TEE-CREW-WHITE-v1.jpg", ["TEXTURE","NECK","SLEEVE","HEM"], "dense combed cotton jersey"),
 "tee_w":    (B+"BLANK-W-TEE-CLASSIC-WHITE-v1.jpg", ["TEXTURE","NECK","SLEEVE","HEM"], "dense combed cotton jersey"),
 "tank":     (B+"BLANK-W-TANK-WHITE-v1.jpg", ["TEXTURE","NECK","HEM"], "four-way stretch performance knit"),
 "bottom":   (B+"BLANK-W-LEGGING-WHITE-v1.jpg", ["TEXTURE","WAIST","SEAM"], "four-way stretch performance knit"),
 "body":     (B+"BLANK-W-BODYSUIT-MESH-WHITE-v1.jpg", ["TEXTURE","SEAM","NECK"], "four-way stretch performance knit"),
 "bodyzip":  (B+"BLANK-W-BODYSUIT-MESH-WHITE-v1.jpg", ["TEXTURE","SEAM","ZIPPER"], "four-way stretch performance knit"),
 "jogger":   (B+"BLANK-M-JOGGER-WHITE-v1.jpg", ["TEXTURE","WAIST","CUFF"], "heavyweight brushed-back cotton fleece"),
 "dogtop":   ("img/BASE-D1-FRONT-v1.jpg", ["TEXTURE","NECK","HEM"], "dense combed cotton jersey"),
 "doghood":  ("img/BASE-D2-FRONT-v1.jpg", ["TEXTURE","HOOD","HEM","DRAWSTRING"], "heavyweight brushed-back cotton fleece"),
 "dogwrap":  (B+"BLANK-DOG-TOP-WHITE-v1.jpg", ["TEXTURE","NECK","CLOSURE"], "knit"),
 "coat":     ("img/BASE-O3-FRONT-v1.jpg", ["TEXTURE","LAPEL","BUTTON","CUFF"], "wool-cashmere double-faced weave"),
 "varsity":  ("img/BASE-O2-FRONT-v1.jpg", ["TEXTURE","SNAP","CUFF"], "heavy wool melton"),
 "loafer":   (B+"BLANK-M-LOAFERSOFT-WHITE-v1.jpg", ["DETAIL","HARDWARE","SOLE","SIDE"], "leather"),
 "slipper":  ("concepts/CONCEPT-SLIPPER-SHERPA-PUPPY-TOP-v1.jpg", ["TEXTURE","SOLE"], "sherpa fleece"),
 "slide":    ("concepts/CONCEPT-SLIDE-WHITE-EMBOSS-ANGLE-v1.jpg", ["TEXTURE","SOLE"], "molded footbed"),
 "harness":  (B+"BLANK-HARNESS-WHITE-ANGLE-v1.jpg", ["HARDWARE","LEATHER"], "leather"),
}
def fam(title, handle):
    t = title.lower()
    dog = "dog" in t
    if "leg warmers" in t or "bucket hat" in t or "matching hoodies" in t: return None
    if "peacoat" in t: return "coat"
    if "varsity" in t: return "varsity"
    if "loafer" in t: return "loafer"
    if "slipper" in t: return "slipper"
    if "slide" in t: return "slide"
    if "harness" in t: return "harness"
    if "wrap" in t and dog: return "dogwrap"
    if dog: return "doghood" if "hoodie" in t else "dogtop"
    if "zip" in t and ("hoodie" in t or "sweatshirt" in t): return "zip"
    if "off-shoulder" in t: return "sweat"
    if "hoodie" in t or "sweatshirt" in t: return "hoodie"
    if "bodysuit" in t: return "bodyzip" if "zip" in t else "body"
    if "sweatpants" in t: return "jogger"
    if any(k in t for k in ("leggings","capris","shorts")): return "bottom"
    if any(k in t for k in ("tank","muscle","halter","bra")): return "tank"
    if "tee" in t or "jersey" in t: return "tee_w" if ("women" in t or "wife" in t) else "tee"
    return None
def color(title):
    t = title.lower()
    if "noir" in t: return "Black #141414"
    if "pink" in t: return "Pink"
    return "Charcoal #3E4044"   # core colorways are CHR / BLK / WHT / BNE; close-ups are shot once in Charcoal, color versions come from recolor.py
def material(title, default):
    t = title.lower()
    if "cashmere" in t: return "cashmere knit"
    if "merino" in t: return "merino wool knit"
    if "faux-fur" in t or "faux fur" in t: return "faux-fur pile"
    return default

rows = list(csv.DictReader(open(os.path.join(R, "shopify_products.csv"), encoding="utf-8")))
jobs, mp, hold = [], [], []
n = 0
for p in rows:
    f = fam(p["title"], p["handle"])
    if not f:
        hold.append((p["handle"], "NEEDS-BASE (no white base in repo yet)")); continue
    base, shots, mat = FAMS[f]
    if not os.path.exists(os.path.join(ROOT, base)): hold.append((p["handle"], "missing base " + base)); continue
    c = color(p["title"]); m = material(p["title"], mat)
    status = "OPEN"
    for s in shots:
        n += 1
        out = f'{p["handle"]}__{s}__v1.jpg'
        label, body, order = SHOTS[s]
        col = f" Garment color: {c}." if c else " Garment color: match the product's hero photo (COLOR TO CONFIRM)."
        if f in ("loafer","slipper","slide","harness"): col = ""
        prompt = f"Image 1 is the product.{col} " + body.format(m=m, c=c or "") + " " + STD
        jobs.append(dict(job_id=f"CU{n:04d}", status=status, input_image=base, prompt=prompt, output_name=out,
                         note=f'{p["title"]} | {label} | family={f} | colorways=CHR,BLK,WHT,BNE (Claude recolors fronts/backs)', handle=p["handle"], product_gid="gid://shopify/Product/"+p["product_id"], shot=s))
        mp.append(dict(output_name=out, handle=p["handle"], product_gid="gid://shopify/Product/"+p["product_id"], shot=s,
                       gallery_order=order, alt=f'{p["title"]} — {label}'))
H = ["job_id","status","input_image","prompt","output_name","note","handle","product_gid","shot"]
old = []
qp = os.path.join(R, "queue.csv")
if os.path.exists(qp):
    old = [r for r in csv.DictReader(open(qp, encoding="utf-8")) if not r["job_id"].startswith("CU")]
with open(qp, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, H, extrasaction="ignore"); w.writeheader(); [w.writerow({k: r.get(k, "") for k in H}) for r in old + jobs]
with open(os.path.join(R, "shopify_map.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, ["output_name","handle","product_gid","shot","gallery_order","alt"]); w.writeheader(); w.writerows(mp)
with open(os.path.join(R, "needs_base.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["handle","reason"]); w.writerows(hold)
from collections import Counter
print(len(jobs), "jobs", Counter(j["status"] for j in jobs), "| hold:", hold)
