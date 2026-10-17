#!/usr/bin/env python3
"""Yoga set (Sponsor Set + Butta line) -> Meta jobs, Shopify map rows, and a copy-paste prompt sheet.
Black colorway first (white print). Other colors: Claude recolors from the approved black/white bases.
Run: python jobs/yoga_jobs.py   (idempotent: replaces YG rows in queue.csv / shopify_map.csv)"""
import csv, os, glob
R = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(R)
def find(n):
    for d in ("blanks/white", "img", "reference", "concepts", "flats/white-base"):
        p = os.path.join(ROOT, d, n)
        if os.path.exists(p): return d + "/" + n
    raise SystemExit("missing base " + n)
STD = ("Plain warm cream-greige seamless studio background, solid #E9E4D8, no gradient, warm natural light with no blue or gray cast, "
       "soft even light from above, soft contact shadow. Flat lay, centered, product fills about 70 percent of the frame, 4:5 portrait. "
       "No other text, no caption, no label, no new logos.")
BLK = "solid black #141414 (matte, true black, folds and texture still visible)"
PRINT_COLOR = "white #F5F5F2"
GID = lambda i: "gid://shopify/Product/" + str(i)
P = {
 "tank":   ("advertise-here-tank-womens", 15400095776920, "Advertise Here Tank — Women's"),
 "legg":   ("advertise-here-leggings-womens", 15400091156632, "Advertise Here Leggings — Women's"),
 "capri":  ("advertise-here-capris-womens", 15400091910296, "Advertise Here Capris — Women's"),
 "short":  ("advertise-here-shorts-womens", 15400092500120, "Advertise Here Shorts — Women's"),
 "dog":    ("and-here-dog-suit", 15399879278744, "And Here... — Dog Suit"),
 "contour":("butta-leggings-contour-womens", 8032961462314, "Butta Leggings — Contour — Women's"),
 "sundown":("butta-leggings-sundown-womens", 8032961658922, "Butta Leggings — Sundown — Women's"),
 "flare":  ("butta-leggings-flare-womens", 8032961789994, "Butta Leggings — Flare — Women's"),
 "zip":    ("butta-bodysuit-zip-front-womens", 15396996055192, "Butta Bodysuit — Zip-Front — Women's"),
 "cross":  ("butta-bodysuit-cross-back-womens", 15396996153496, "Butta Bodysuit — Cross-Back — Women's"),
 "sheer":  ("butta-bodysuit-sheer-womens", 15399890813080, "Butta Bodysuit — Sheer — Women's"),
}
jobs = []   # dict(tier, key, shot, inputs[], prompt, order, label, shared_with)
def J(tier, key, shot, inputs, prompt, order, label, shared=None, note=""):
    jobs.append(dict(tier=tier, key=key, shot=shot, inputs=inputs, prompt=prompt + " " + STD, order=order, label=label, shared=shared or [], note=note))

# ---------- SPONSOR SET (the ad) ----------
TB, TF = find("BLANK-W-TANK-WHITE-BACK-v1.jpg"), find("BLANK-W-TANK-WHITE-v1.jpg")
LB, LF = find("BLANK-W-LEGGING-WHITE-BACK-v1.jpg"), find("BLANK-W-LEGGING-WHITE-v1.jpg")
SB, SF = find("BLANK-W-SHORT-BIKE-WHITE-v1.jpg"), find("BLANK-W-BOOTY-SHORT-WHITE-BACK-v1.jpg")
DG = find("BLANK-DOG-TOP-WHITE-v1.jpg")
# P1 ad-critical
J(1,"tank","BACK",[TB],f"Image 1 is the tank. Make the same tank in {BLK}, BACK view. Keep the ribbed knit, scoop back and straps exactly as image 1. Printed across the upper back in {PRINT_COLOR}: the words ADVERTISE HERE in arched varsity block capitals, about 9 inches wide, centered 4 inches below the neckline. Nothing else on the garment.",2,"back view")
J(1,"legg","BACK",[LB],f"Image 1 is the leggings. Make the same leggings in {BLK}, BACK view, laid straight and flat, full length. The fold-over waistband carries {PRINT_COLOR} small block capitals reading ADVERTISE HERE across its center back, about 6 inches wide. Nothing else printed.",2,"back view with waistband print")
J(1,"dog","SIDEPRINT",[DG],f"Image 1 is the dog top. Make the same dog top in {BLK}. {PRINT_COLOR} lettering reading AND HERE... printed small on the side body panel, running along the length of the panel, about 4 inches long. Keep the collar, sleeves and hem exactly as image 1. Nothing else printed.",2,"side-panel print")
J(1,"tank","SETFLAT",["jobs/done/advertise-here-tank-womens__BACK__v1.jpg","jobs/done/advertise-here-leggings-womens__BACK__v1.jpg","jobs/done/and-here-dog-suit__SIDEPRINT__v1.jpg"],
  "Image 1 is the black tank, image 2 the black leggings, image 3 the black dog top. Arrange all three as one neat flat-lay set: tank on top, leggings folded in thirds below it, dog top beside them, small even gaps, same prints as the images, nothing added, nothing changed.",6,"the set, flat lay",shared=["legg","capri","short","dog"],note="RUN AFTER jobs for tank BACK, legg BACK, dog SIDEPRINT are approved")
J(1,"tank","MODELDOG",["jobs/done/advertise-here-tank-womens__BACK__v1.jpg","jobs/done/advertise-here-leggings-womens__BACK__v1.jpg","jobs/done/and-here-dog-suit__SIDEPRINT__v1.jpg"],
  "Image 1 is the black tank, image 2 the black leggings, image 3 the black dog top. Studio fashion photograph shot from behind, mid-thigh to head: an athletic woman in her 30s, hair up, wearing the tank from image 1 and the leggings from image 2, standing relaxed. A French Bulldog sits at her feet, also seen from behind, wearing the dog top from image 3. Keep every print exactly as shown, readable, nothing added. 85mm lens, editorial e-commerce look.",7,"model with her dog, matching",shared=["legg","capri","short","dog"],note="RUN AFTER the three P1 jobs are approved")
# P2 per product
J(2,"tank","FRONT",[TF],f"Image 1 is the tank. Make the same tank in {BLK}, FRONT view, clean with no print, keep the ribbed knit and scoop neck from image 1.",1,"front view")
J(2,"tank","TEXTURE",[TB],f"Image 1 is the tank. Tight macro close-up of the fine ribbed knit of this tank in {BLK}, filling the frame, rib and stitching visible, soft raking light.",3,"rib knit close-up")
J(2,"tank","PRINT",["jobs/done/advertise-here-tank-womens__BACK__v1.jpg"],f"Image 1 is the finished tank back. Close-up of the {PRINT_COLOR} ADVERTISE HERE print on the black knit, sharp focus, shallow depth of field, the print exactly as in image 1.",4,"print close-up")
J(2,"legg","FRONT",[LB,LF],f"Image 1 is the BACK of the leggings, image 2 shows the same leggings folded. Make the FRONT view in {BLK}, laid straight and flat, full length, waistband at the top, clean with no print.",1,"front view")
J(2,"legg","TEXTURE",[LB],f"Image 1 is the leggings. Tight macro close-up of the smooth stretch knit of these leggings in {BLK}, filling the frame, soft raking light, matte surface.",3,"fabric close-up")
J(2,"legg","PRINT",["jobs/done/advertise-here-leggings-womens__BACK__v1.jpg"],f"Image 1 is the finished leggings back. Close-up of the fold-over waistband with the {PRINT_COLOR} ADVERTISE HERE print, sharp focus, shallow depth of field, the print exactly as in image 1.",4,"waistband print close-up")
J(2,"capri","BACK",[LB],f"Image 1 is the leggings. Make the same style as CAPRIS cropped at mid-calf, in {BLK}, BACK view, laid flat. The fold-over waistband carries {PRINT_COLOR} small block capitals ADVERTISE HERE across its center back, about 6 inches wide.",2,"back view with waistband print")
J(2,"capri","FRONT",[LB,LF],f"Image 1 is the BACK of the leggings, image 2 shows them folded. Make the same style as CAPRIS cropped at mid-calf, in {BLK}, FRONT view, laid flat, clean with no print.",1,"front view")
J(2,"capri","TEXTURE",[LB],f"Image 1 is the leggings. Tight macro close-up of the smooth stretch knit in {BLK}, filling the frame, soft raking light, matte surface.",3,"fabric close-up")
J(2,"capri","PRINT",["jobs/done/advertise-here-capris-womens__BACK__v1.jpg"],f"Image 1 is the finished capris back. Close-up of the waistband and the {PRINT_COLOR} ADVERTISE HERE print, sharp focus, shallow depth of field, exactly as image 1.",4,"waistband print close-up")
J(2,"short","BACK",[SF],f"Image 1 is the shorts. Make the same shorts in {BLK}, BACK view, laid flat. The waistband carries {PRINT_COLOR} small block capitals ADVERTISE HERE across its center back, about 5 inches wide. Nothing else printed.",2,"back view with waistband print")
J(2,"short","FRONT",[SB],f"Image 1 is the shorts. Make the same shorts in {BLK}, FRONT view, laid flat, clean with no print.",1,"front view")
J(2,"short","TEXTURE",[SB],f"Image 1 is the shorts. Tight macro close-up of the smooth stretch knit in {BLK}, filling the frame, soft raking light, matte surface.",3,"fabric close-up")
J(2,"short","PRINT",["jobs/done/advertise-here-shorts-womens__BACK__v1.jpg"],f"Image 1 is the finished shorts back. Close-up of the waistband and the {PRINT_COLOR} ADVERTISE HERE print, sharp focus, shallow depth of field, exactly as image 1.",4,"waistband print close-up")
J(2,"dog","FRONT",[DG],f"Image 1 is the dog top. Make the same dog top in {BLK}, top-down flat lay, clean with no print.",1,"flat lay")
J(2,"dog","TEXTURE",[DG],f"Image 1 is the dog top. Tight macro close-up of the soft stretch knit and the ribbed cuff of this dog top in {BLK}, soft raking light.",3,"fabric and cuff close-up")
J(2,"dog","PRINT",["jobs/done/and-here-dog-suit__SIDEPRINT__v1.jpg"],f"Image 1 is the finished dog top. Close-up of the {PRINT_COLOR} AND HERE... print on the side panel, sharp focus, shallow depth of field, exactly as image 1.",4,"print close-up")
J(2,"dog","BACK",[DG],f"Image 1 is the dog top. Make the same dog top in {BLK}, seen from the back and laid flat, with the leash opening at the center, clean with no print.",5,"back view")
# ---------- BUTTA LINE (P3) ----------
B = {
 "contour":(find("BLANK-W-YOGA-CONTOUR-WHITE-v1.jpg"),"high-rise full-length leggings with sculpting seams","leggings"),
 "sundown":(find("BLANK-W-LEGGING-WHITE-BACK-v1.jpg"),"low-rise leggings cropped at the ankle","leggings"),
 "flare":  (find("BLANK-W-YOGA-FLARE-WHITE-v1.jpg"),"high-rise leggings with a flared hem","leggings"),
 "zip":    (find("BLANK-W-BODYSUIT-FLAGSHIP-WHITE-v1.jpg"),"zip-front bodysuit","bodysuit"),
 "cross":  (find("BLANK-W-BODYSUIT-MESH-WHITE-v1.jpg"),"cross-back bodysuit","bodysuit"),
 "sheer":  (find("BLANK-W-BODYSUIT-SHEER-WHITE-v1.jpg"),"sheer bodysuit","bodysuit"),
}
for k,(base,desc,kind) in B.items():
    fab = "soft matte stretch knit"
    J(3,k,"FRONT",[base],f"Image 1 is the product. Make the same {desc} in {BLK}, FRONT view, laid flat, clean with no print or logo, keep every seam and the shape from image 1.",1,"front view")
    J(3,k,"BACK",[base],f"Image 1 is the product. Show the same {desc} in {BLK} from the BACK, laid flat, clean with no print or logo, same fabric and seams as image 1.",2,"back view")
    J(3,k,"TEXTURE",[base],f"Image 1 is the product. Tight macro close-up of the {fab} of this {kind} in {BLK}, filling the frame, soft raking light, matte surface.",3,"fabric close-up")
    J(3,k,"DETAIL",[base],f"Image 1 is the product. Close-up of the seam and waistband or neckline construction of this {kind} in {BLK}, sharp focus, shallow depth of field.",4,"construction detail")
# ---------- write ----------
rows = []; maprows = []; n = 0
jobs.sort(key=lambda j: (j["tier"], list(P).index(j["key"]), j["order"]))
for j in jobs:
    n += 1; h, pid, title = P[j["key"]]
    out = f"{h}__{j['shot']}__v1.jpg"
    rows.append(dict(job_id=f"YG{n:04d}", status="OPEN", input_image="|".join(j["inputs"]), prompt=j["prompt"], output_name=out,
        note=f"P{j['tier']} | {title} | {j['label']}" + (f" | {j['note']}" if j["note"] else ""), handle=h, product_gid=GID(pid), shot=j["shot"]))
    maprows.append(dict(output_name=out, handle=h, product_gid=GID(pid), shot=j["shot"], gallery_order=j["order"], alt=f"{title} — {j['label']}",
        also_handles=";".join(f"{P[s][0]}={GID(P[s][1])}" for s in j["shared"])))
# queue.csv
qp = os.path.join(R, "queue.csv"); q = list(csv.DictReader(open(qp, encoding="utf-8"))); hdr = list(q[0].keys())
q = [r for r in q if not r["job_id"].startswith("YG")] + rows
with open(qp, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=hdr); w.writeheader(); w.writerows(q)
# shopify_map.csv (+ also_handles column)
mp = os.path.join(R, "shopify_map.csv"); m = list(csv.DictReader(open(mp, encoding="utf-8")))
mh = ["output_name","handle","product_gid","shot","gallery_order","alt","also_handles"]
yg_names = {r["output_name"] for r in rows}
m = [dict(r, also_handles=r.get("also_handles","")) for r in m if r["output_name"] not in yg_names] + maprows
with open(mp, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=mh); w.writeheader(); w.writerows(m)
# prompt sheet
L = ["# DSS YOGA SET — META JOBS (black, white print, warm backdrop #E9E4D8)", "",
 "How to run: open the job, upload the INPUT file(s) from the repo `jobs/inbox` as Image 1 (and Image 2, 3 where listed), paste the PROMPT, save the result with the exact SAVE AS name into `jobs/inbox/`. Tell me when a batch is in and I size it, check it, and attach it to the product.",
 "Order matters: P1 first (these are the ad). The SET and MODEL jobs use the approved P1 results as inputs.",
 "Rule: if Meta changes the lettering, adds text or changes the cut, rerun. Do not send a result with wrong letters.", ""]
for t,name in ((1,"P1 — THE AD (do these first)"),(2,"P2 — rest of the Sponsor Set pages"),(3,"P3 — Butta leggings and bodysuits")):
    L += [f"## {name}", ""]
    for r in rows:
        if r["note"].startswith(f"P{t}"):
            L += [f"### {r['job_id']}  {r['note'].split('|',1)[1].strip()}", f"INPUT: {r['input_image'].replace('|',' + ')}", f"SAVE AS: {r['output_name']}", "```", r["prompt"], "```", ""]
open(os.path.join(ROOT, "docs", "META-YOGA-SET.md"), "w", encoding="utf-8").write("\n".join(L))
print(len(rows), "jobs:", {t: sum(1 for r in rows if r['note'].startswith(f'P{t}')) for t in (1,2,3)})
