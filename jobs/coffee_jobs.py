#!/usr/bin/env python3
"""THE COFFEE SHOP capsule: Meta job pack (6 launch drinks + dog hoodies).
Writes jobs/coffee_queue.csv, jobs/coffee_map.csv and docs/META-COFFEE-SHOP.md.
Kept OUT of queue.csv / shopify_map.csv on purpose: the Shopify products do not exist yet, so there are no
product ids. When the products are created, fill product_gid (and also_handles gids) in coffee_map.csv, then
merge both CSVs into queue.csv / shopify_map.csv and run attach_plan.py as usual.
Output filename code:  <handle>__<SHOT>__v1.jpg
"""
import csv, os
R = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(R)
REF = "reference/coffee-shop/"
DONE = "jobs/done/"

BROWN, GREEN, CREAM, BACKDROP = "#4D2E1F", "#6B8667", "#EFE8DC", "#E9E4D8"
BG = (f"Plain warm cream-greige seamless studio background, solid {BACKDROP}, no gradient, warm natural light with "
      "no blue or gray cast, soft even light from above, soft contact shadow.")
TAIL = " No other text, no caption, no label, no logos, no brand names, no printing on any cup."
NOCAP = " Ignore any caption or file-name text in the reference images; do not reproduce it."
SIZE = " 4:5 portrait."

# drink key -> (handle, title, color name, hex, human letters (list of lines), dog drink key, human prop, style ref)
DRINKS = [
 ("mocha",   "coffee-shop-mocha-hoodie",   "Mocha Hoodie",        "brown", ["MOCHA"],            "latte",  "a small ceramic mug of mocha dusted with cocoa"),
 ("espresso","coffee-shop-espresso-hoodie","Espresso Hoodie",     "brown", ["ESPRESSO"],         "latte",  "a small white espresso cup of black espresso"),
 ("chai",    "coffee-shop-chai-hoodie",    "Chai Hoodie",         "brown", ["CHAI"],             "latte",  "a plain paper to-go cup of chai with a cinnamon stick"),
 ("coffee",  "coffee-shop-coffee-hoodie",  "Coffee Hoodie",       "brown", ["COFFEE"],           "pupcup", "a ceramic mug of coffee with a milk swirl"),
 ("matcha",  "coffee-shop-matcha-hoodie",  "Matcha Hoodie",       "green", ["MATCHA"],           "latte",  "a ceramic bowl of bright green whisked matcha"),
 ("icedcaramel","coffee-shop-iced-caramel-hoodie","Iced Caramel Hoodie","brown",["ICED","CARAMEL"],"pupcup","a clear plastic cup of iced caramel drink with whipped cream and caramel drizzle"),
]
DOGS = {
 "latte":  ("LATTE",   "a small ceramic cup of latte with simple heart latte art"),
 "pupcup": ("PUP CUP", "a small plain paper cup of whipped cream topped with two bone-shaped dog biscuits"),
}
DOG_HANDLES = {"latte": ("coffee-shop-dog-hoodie-latte", "Dog Hoodie, Latte"),
               "pupcup": ("coffee-shop-dog-hoodie-pup-cup", "Dog Hoodie, Pup Cup")}
COLOR = {"brown": ("Roast brown", BROWN), "green": ("Matcha green", GREEN)}

def color_phrase(c):
    n, h = COLOR[c]
    return f"{n} {h} (matte brushed-back cotton fleece, folds and texture visible)"

def spell(lines):
    return " ".join(lines)

def let_adult(lines):
    word = spell(lines)
    if len(lines) == 1:
        rule = "One word on a single gentle arch across the upper back, about 55 percent of the back width."
    else:
        rule = ("Two lines: the first word on a gentle arch, the second word straight and centered directly below it, "
                "same letter height, about 55 percent of the back width.")
    return (f"Adult hoodie lettering reads {word} in thick cream {CREAM} varsity block capitals, raised twill appliqué with a "
            f"visible stitched edge. {rule} Spell it exactly, do not add, drop or change any letter.")

def let_dog(word):
    return (f"Dog hoodie lettering reads {word} in the same cream {CREAM} raised twill varsity capitals, about half the size, "
            "on one gentle arch across the upper back between the shoulders, fully visible and not hidden by folds. "
            "Spell it exactly.")

CUT = ("Keep the cut from image 1: oversized pullover adult hoodie with dropped shoulders, ribbed cuffs and hem; "
       "dog hoodie with raglan sleeves, hood and ribbed cuffs and rounded hem.")

jobs = []   # dicts
def J(tier, handle, shot, inputs, prompt, order, label, note, also=""):
    jobs.append(dict(tier=tier, handle=handle, shot=shot, inputs=inputs, prompt=prompt, order=order,
                     label=label, note=note, also=also))

alt_label = {"FLAT":"back, with the matching dog hoodie", "MODEL":"worn, with her dog", "FRONT":"front",
             "DETAIL":"lettering detail", "TEXTURE":"fabric close-up", "BACK":"back", "DOGFRONT":"front"}
refs = {"brown": REF + "COFFEE-REF-MOCHA-FLAT-v1.jpg", "green": REF + "COFFEE-REF-MATCHA-FLAT-v1.jpg"}

# ---- P1: FLAT back, hoodie + dog hoodie + two cups
for key, handle, title, col, lines, dk, prop in DRINKS:
    dword, dprop = DOGS[dk]
    p = (f"Image 1 is the style reference: copy its hoodie cut, dog hoodie cut, fabric look and lettering style exactly. "
         f"Make a new flat lay. Adult hoodie, BACK view, {color_phrase(col)}, large and centered in the upper two thirds of the frame, "
         f"hood laid flat behind the neck. {let_adult(lines)} "
         f"Dog hoodie, BACK view, same color, smaller, in the lower right. {let_dog(dword)} "
         f"Two small props below the garments, uncluttered: {prop} at lower left and {dprop} at lower right. "
         f"{BG} Flat lay, centered, 4:5 portrait.{TAIL}{NOCAP}")
    also = ""
    if key in ("mocha", "coffee"):
        also = DOG_HANDLES[dk][0]
    J(1, handle, "FLAT", [refs[col]], p, 1, title, f"{title} | back flat lay with {dword} dog hoodie | color {col}", also)

# ---- P2: MODEL (needs approved FLAT)
for key, handle, title, col, lines, dk, prop in DRINKS:
    dword, _ = DOGS[dk]
    p = (f"Image 1 is the approved flat lay of this exact adult hoodie and dog hoodie: keep the same colors, cut and lettering exactly. "
         f"Photograph a woman standing and seen from directly behind, face not visible, hair in a low ponytail, wearing the adult hoodie from image 1 with black leggings. "
         f"Beside her at her left a French bulldog sits, seen from behind and slightly from the side, wearing the dog hoodie from image 1 with its lettering facing the camera and fully visible. "
         f"The lettering must be sharp, fully legible and spelled exactly: {spell(lines)} on the woman, {dword} on the dog. "
         f"Frame the woman from head to mid-thigh and the whole dog in frame. {BG} No props. 4:5 portrait.{TAIL}")
    also = DOG_HANDLES[dk][0] if key in ("mocha", "coffee") else ""
    J(2, handle, "MODEL", [DONE + f"{handle}__FLAT__v1.jpg"], p, 2, title,
      f"{title} | back view on model with her dog | RUN AFTER {handle} FLAT is approved", also)

# ---- P3: FRONT (plain) and TEXTURE (shared)
for key, handle, title, col, lines, dk, prop in DRINKS:
    p = (f"Image 1 is the approved flat lay: use its exact colors and fabric. Image 2 is the adult hoodie FRONT construction "
         f"(kangaroo pocket, drawstrings, ribbed cuffs and hem). Image 3 is the dog hoodie FRONT construction. "
         f"Make a flat lay of the FRONT of both: adult hoodie large in the upper two thirds, dog hoodie smaller in the lower right, "
         f"both in {color_phrase(col)} like image 1, drawstrings tonal. The fronts are completely plain: no lettering, no print, no logos, no labels. "
         f"{BG} Flat lay, centered, 4:5 portrait.{TAIL}{NOCAP}")
    J(3, handle, "FRONT", [DONE + f"{handle}__FLAT__v1.jpg", REF + "COFFEE-INPUT-HOODIE-FRONT-v1.jpg",
                           REF + "COFFEE-INPUT-DOG-HOODIE-FRONT-v1.jpg"], p, 3, title,
      f"{title} | plain front | RUN AFTER {handle} FLAT is approved")

TEX = [("brown", "coffee-shop-mocha-hoodie",
        ["coffee-shop-espresso-hoodie", "coffee-shop-chai-hoodie", "coffee-shop-coffee-hoodie",
         "coffee-shop-iced-caramel-hoodie", "coffee-shop-dog-hoodie-latte", "coffee-shop-dog-hoodie-pup-cup"], "Mocha Hoodie"),
       ("green", "coffee-shop-matcha-hoodie", [], "Matcha Hoodie")]
for col, handle, also_list, title in TEX:
    p = (f"Image 1 is the approved flat lay: use its exact color. Tight macro close-up of the heavyweight brushed-back cotton fleece in "
         f"{color_phrase(col)}, with a short section of ribbed cuff along one edge of the frame, loops of the fleece and the rib visible, "
         f"soft raking light so the weight of the fabric shows. No lettering, no print. 4:5 portrait.{TAIL}")
    J(3, handle, "TEXTURE", [DONE + f"{handle}__FLAT__v1.jpg"], p, 5, title,
      f"{col} fabric close-up | shared across {1+len(also_list)} pages | RUN AFTER {handle} FLAT is approved", ";".join(also_list))

# ---- P4: DETAIL (lettering macro) + dog-only shots
for key, handle, title, col, lines, dk, prop in DRINKS:
    word = lines[-1] if len(lines) > 1 else lines[0]
    p = (f"Image 1 is the approved flat lay. Tight macro close-up of the raised cream {CREAM} twill appliqué lettering on the back of the adult hoodie, "
         f"framed on two or three of the middle letters of {spell(lines)} (the whole word does not need to show), showing the stitched edge, the slight lift off the fabric "
         f"and the brushed-back {COLOR[col][0].lower()} fleece around it. Same exact color and letter style as image 1, soft raking light, shallow depth of field. "
         f"Every visible letter must be a real letter of the word. 4:5 portrait.{TAIL}")
    J(4, handle, "DETAIL", [DONE + f"{handle}__FLAT__v1.jpg"], p, 4, title,
      f"{title} | lettering close-up | RUN AFTER {handle} FLAT is approved")

for dk, (dh, dt) in DOG_HANDLES.items():
    dword, _ = DOGS[dk]
    p = (f"Image 1 is the style reference: copy the dog hoodie cut, fabric look and lettering style exactly. Make a flat lay of only the dog hoodie, BACK view, "
         f"{color_phrase('brown')}, centered, filling about 65 percent of the frame. {let_dog(dword)} {BG} Flat lay, centered, 4:5 portrait.{TAIL}")
    J(4, dh, "BACK", [refs["brown"]], p, 1, dt, f"{dt} | dog hoodie only, back | color brown (dog color follows the human hoodie)")
    p = (f"Image 1 is the approved dog hoodie flat lay. Tight macro close-up of the raised cream {CREAM} twill appliqué lettering reading {dword} on the back of the dog hoodie, "
         f"framed on two or three middle letters, stitched edge and brushed-back brown fleece visible, soft raking light, shallow depth of field. "
         f"Every visible letter must be a real letter of the word. 4:5 portrait.{TAIL}")
    J(4, dh, "DETAIL", [DONE + f"{dh}__BACK__v1.jpg"], p, 4, dt, f"{dt} | lettering close-up | RUN AFTER {dh} BACK is approved")

p = (f"Image 1 is the dog hoodie FRONT construction. Image 2 is the approved color and fabric reference. Make a flat lay of the dog hoodie FRONT view in "
     f"{color_phrase('brown')}, centered, filling about 65 percent of the frame. Completely plain: no lettering, no print, no logos, no labels. "
     f"{BG} 4:5 portrait.{TAIL}{NOCAP}")
J(4, "coffee-shop-dog-hoodie-latte", "FRONT", [REF + "COFFEE-INPUT-DOG-HOODIE-FRONT-v1.jpg", refs["brown"]], p, 2,
  "Dog Hoodie", "Dog hoodie plain front | shared by both dog hoodie pages", "coffee-shop-dog-hoodie-pup-cup")

# ---- sort + ids
jobs.sort(key=lambda j: (j["tier"], 0))   # stable: keeps DRINKS order within a tier
for i, j in enumerate(jobs, 1):
    j["id"] = f"CS{i:04d}"
    j["out"] = f"{j['handle']}__{j['shot']}__v1.jpg"

# ---- CSVs
with open(os.path.join(R, "coffee_queue.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["job_id", "status", "input_image", "prompt", "output_name", "note", "handle", "product_gid", "shot"])
    for j in jobs:
        w.writerow([j["id"], "OPEN", "|".join(j["inputs"]), j["prompt"], j["out"], j["note"], j["handle"], "", j["shot"]])
with open(os.path.join(R, "coffee_map.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["output_name", "handle", "product_gid", "shot", "gallery_order", "alt", "also_handles"])
    for j in jobs:
        alt = f"{j['label']} — The Coffee Shop — {alt_label.get(j['shot'], j['shot'].lower())}"
        w.writerow([j["out"], j["handle"], "", j["shot"], j["order"], alt,
                    ";".join(f"{h}=" for h in j["also"].split(";") if h)])

# ---- sheet
tiers = {1: "P1 — THE HERO (back flat lay of each drink with its dog hoodie). Do these first.",
         2: "P2 — ON MODEL (each uses its approved P1 result as Image 1)",
         3: "P3 — PLAIN FRONTS and FABRIC (use approved P1 results)",
         4: "P4 — LETTERING CLOSE-UPS and DOG HOODIE PAGES"}
md = []
md.append("# THE COFFEE SHOP — META JOBS (6 launch drinks, lettering locked)\n")
md.append("Launch drinks: Mocha, Espresso, Chai, Coffee, Matcha, Iced Caramel. Dog drinks: Latte, Pup Cup. "
          "Later waves (not in this pack): Cold Brew, Vanilla, White Mocha, Green Tea, Iced Green Tea.\n")
md.append("## THE LOCK (same on every image)\n")
md.append(f"- Hoodie color: **Roast brown {BROWN}** for Mocha, Espresso, Chai, Coffee and Iced Caramel. **Matcha green {GREEN}** for Matcha. "
          f"One brown for all five. Chai must not be lighter than the rest.\n"
          f"- Lettering: **thick cream {CREAM} varsity block capitals, raised twill appliqué with a stitched edge.** Never thin serif embroidery.\n"
          "- One-word names sit on one arch. Two-word names (Iced Caramel) go on two lines: first word arched, second word straight below, same letter height.\n"
          "- Dog hoodie lettering: same style, half the size, one arch across the upper back, fully visible.\n"
          f"- Backdrop: warm cream-greige **{BACKDROP}**, every image. Format: **4:5 portrait**, every image.\n"
          "- No text on cups, no brand names, no logos. Fronts are plain.\n"
          "- Models are seen from behind, face never visible.\n")
md.append("## How to run\n")
md.append("Upload the INPUT file(s) as Image 1 (and Image 2, 3 where listed), paste the PROMPT, save the result with the exact SAVE AS name into `jobs/inbox/`. "
          "Your reference images are in `reference/coffee-shop/`; the two style locks are **COFFEE-REF-MOCHA-FLAT-v1.jpg** (brown) and **COFFEE-REF-MATCHA-FLAT-v1.jpg** (green). "
          "Jobs marked RUN AFTER use an approved result from `jobs/done/`, so approve P1 first.\n")
md.append("**Rerun the job if:** a letter is wrong or missing, the lettering style changes (thin or serif), the color drifts, text appears on a cup, "
          "the dog's lettering is hidden or cut off, or the picture is not 4:5 on the warm backdrop.\n")
md.append("**Your earlier 10 images:** Mocha flat and Matcha flat are the style locks and stay as they are. The Chai flat, both Caramel images and the Mocha and Caramel model shots "
          "are marked REDO in `reference/coffee-shop/` because of lettering style, clipped dog lettering or stacked layout. Espresso and Coffee flats are good but landscape and a different backdrop, "
          "so they are replaced by the 4:5 versions below (they can still go on the page as an extra image).\n")
cur = 0
for j in jobs:
    if j["tier"] != cur:
        cur = j["tier"]; md.append(f"\n## {tiers[cur]}\n")
    ins = " + ".join(f"Image {n}: {x}" for n, x in enumerate(j["inputs"], 1)) if len(j["inputs"]) > 1 else j["inputs"][0]
    md.append(f"### {j['id']}  {j['note']}")
    md.append(f"INPUT: {ins}")
    md.append(f"SAVE AS: {j['out']}")
    md.append("```\n" + j["prompt"] + "\n```\n")
md.append(f"\nTotal: {len(jobs)} jobs. Products do not exist in Shopify yet. When they are created I fill the product ids in `jobs/coffee_map.csv`, "
          "merge into the main queue, and attach the images in the gallery order shown there.\n")
with open(os.path.join(ROOT, "docs", "META-COFFEE-SHOP.md"), "w") as f:
    f.write("\n".join(md))

from collections import Counter
print(len(jobs), "jobs", dict(Counter(j["tier"] for j in jobs)), dict(Counter(j["shot"] for j in jobs)))
