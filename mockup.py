#!/usr/bin/env python3
"""
DSS MOCKUP COMMAND
==================
One command -> consistent mockup prompts for any DSS item, in any color(s).
Same standard every time (DSS-UNIFORMITY-SPEC, v3): neutral gray #E9E9E7 backdrop,
soft light from above, graphics on the BACK, front clean with one tonal Frenchie.

Examples
  python3 mockup.py --item hoodie --colors BLK,BNE,CAM --mode recolor
  python3 mockup.py --item tee --colors BLK,BNE,ESP,OLV,CHR,BLS --mode model --with-dog --tier A
  python3 mockup.py --item tee --colors BLK --mode pair --tier A
  python3 mockup.py --item tee --colors BLK --mode back --art "FRENCHIE AF drip lettering" --width "~11 in"
  python3 mockup.py --list

Modes
  recolor  white-base flat lay recolored to each color (the spec's standard pipeline)
  model    James Perse style model shot: HERO first, then one color-swap prompt per color
  pair     flat lay of the human piece + matching dog piece together, per color
  back     BACK view with a graphic placed on the upper back, per color

To change the look of EVERY prompt, edit the STANDARD block below and re-run.
"""
import argparse, csv, os, sys

# ------------------------------------------------------------------ STANDARD (edit here only)
VER = "v3"
BACKDROP_HEX = "#E9E9E7"
BG_SHORT = f"neutral light-gray {BACKDROP_HEX} background with no color cast"
BACKDROP = (f"plain neutral light-gray seamless studio background, solid {BACKDROP_HEX}, no gradient, "
            "true neutral white balance with no blue cast and no warm or cream cast")
LIGHT = "soft even light from above, soft contact shadow"
TAIL = "No text, no caption, no label, no new logos."
HUMAN_MARK = "about 1.3 inches wide and 2 inches tall"
DOG_MARK = "about 0.9 inch wide and 1.4 inches tall"
MARK_FILE = "MARK-FRENCHIE-SEATED-BLUSH.png"
HERO_COLOR = "WHT"          # the approved white base is the source for every recolor

# code: (name, hex, scope)  -- from DSS-COLOR-MASTER.csv (locked 2026-10-11)
COLORS = {
    "BLK": ("Black", "#141414", "all tiers"), "WHT": ("White", "#F5F5F2", "all tiers"),
    "BNE": ("Bone", "#E4DCCB", "all tiers"), "CRM": ("Cream", "#F1E9D2", "Noir/La Rue"),
    "OAT": ("Oatmeal", "#D3C6AE", "staples only"), "CAM": ("Camel", "#B58A55", "Noir/La Rue/coats"),
    "ESP": ("Espresso", "#3B2A22", "all tiers"), "CHC": ("Chocolate", "#5A3B2B", "shoes and leather goods only"),
    "CHR": ("Charcoal", "#3E4044", "all tiers"), "NVY": ("Navy", "#1B2438", "Noir/La Rue"),
    "FOR": ("Forest", "#1F3A2B", "Noir/La Rue"), "OLV": ("Olive", "#5A5A2E", "Activé"),
    "WIN": ("Wine", "#6E1630", "apparel"), "DWN": ("Deep Wine", "#420819", "coats only"),
    "PLM": ("Plum", "#4B2A4F", "all tiers"), "ROY": ("Royal", "#5B2D8C", "La Rue Limited only"),
    "HOT": ("Hot Pink", "#EE729D", "loud prints and pink garments"),
    "BLS": ("Blush", "#D2A6A7", "embroidery/tonal and blush garments"),
}
TIERS = {"A": "Activé", "L": "La Rue", "N": "Noir", "X": "La Rue Limited"}

# key: (description, kind, base file, sleeve text?, dog partner key)
ITEMS = {
    "hoodie":      ("a pullover hoodie", "human", "BASE-H3-FRONT-v1.jpg", True, "dog-hoodie"),
    "sweatshirt":  ("a crewneck sweatshirt", "human", "BLANK-M-CREW-SWEAT-WHITE-v1.jpg", True, "dog-sweatshirt"),
    "tee":         ("a crew tee", "human", "BLANK-M-TEE-CREW-WHITE-v1.jpg", False, "dog-tee"),
    "polo":        ("a pique polo", "human", f"BASE-POLO-M-FRONT-{VER}.jpg", False, "dog-polo"),
    "knit":        ("a cashmere crew sweater", "human", "BLANK-M-CASH-CREW-WHITE-v1.jpg", False, "dog-knit"),
    "flannel":     ("a flannel shirt", "human", "BLANK-M-FLANNEL-WHITE-v1.jpg", False, "dog-flannel"),
    "w-tee":       ("a women's classic tee", "human", "BLANK-W-TEE-CLASSIC-WHITE-v1.jpg", False, "dog-tee"),
    "w-sweatshirt":("a women's crewneck sweatshirt", "human", "BLANK-W-CREW-SWEAT-WHITE-v1.jpg", True, "dog-sweatshirt"),
    "w-polo":      ("a women's pique polo", "human", f"BASE-POLO-W-FRONT-{VER}.jpg", False, "dog-polo"),
    "w-knit":      ("a women's cashmere crew sweater", "human", "BLANK-W-CASH-CREW-WHITE-v1.jpg", False, "dog-knit"),
    "dog-hoodie":  ("a dog hoodie", "dog", "BASE-D2-FRONT-v1.jpg", False, None),
    "dog-tee":     ("a dog tee", "dog", "BASE-D1-FRONT-v1.jpg", False, None),
    "dog-sweatshirt": ("a dog crewneck sweatshirt", "dog", f"BASE-DOG-CREW-FRONT-{VER}.jpg", False, None),
    "dog-polo":    ("a dog polo", "dog", f"BASE-DOG-POLO-FRONT-{VER}.jpg", False, None),
    "dog-knit":    ("a dog sweater", "dog", f"BASE-DOG-KNIT-FRONT-{VER}.jpg", False, None),
    "dog-flannel": ("a dog flannel", "dog", f"BASE-DOG-FLANNEL-FRONT-{VER}.jpg", False, None),
}
SLEEVE_TEXT = ("On the left upper sleeve add stitched tonal text, DOGGY STYLE SOCIETY on one line and LOS ANGELES "
               "below it, in thread matching the fabric, fully visible with clear margin on both sides, no patch.")
# ------------------------------------------------------------------ END STANDARD


def mark_size(kind):
    return HUMAN_MARK if kind == "human" else DOG_MARK


def code(tier, key, color, view):
    return f"{tier}-{key.upper()}-{color}-{view}-{VER}"


def scope_warning(color, tier):
    name, _, scope = COLORS[color]
    s = scope.lower()
    if s == "all tiers" or TIERS[tier].lower() in s.replace("/", " ").split("/") or TIERS[tier].lower() in s:
        return ""
    if s.startswith("apparel"):
        return ""
    return f"WARNING: {name} is scoped to '{scope}' in DSS-COLOR-MASTER; check it is allowed for {TIERS[tier]}."


def recolor(key, color, tier):
    desc, kind, base, sleeve, _ = ITEMS[key]
    cname, chex, _ = COLORS[color]
    trim = "placket buttons, collar and cuffs" if "polo" in key else "any drawstrings, ribs, collar and lining"
    st = SLEEVE_TEXT if sleeve else "No sleeve text, no patch."
    p = (f"Image 1 is {desc} flat lay (approved white base). Image 2 is the exact embroidered French bulldog. "
         f"Change ONLY the fabric color to {cname} {chex}, including {trim}. Keep the pose, folds, crop and lighting "
         f"identical to image 1, and keep the background as the same {BG_SHORT}. On the left chest add the French bulldog "
         "from image 2 copied EXACTLY, do not redraw or change it: seated, crown, collar, same proportions. Make it tonal "
         f"embroidery in thread the same color as the fabric, {mark_size(kind)}, the size of a polo pony. Ignore any "
         f"background in image 2. {st} Back and everything else unchanged.")
    return code(tier, key, color, "FRONT"), base, MARK_FILE, p


def model_hero(key, color, tier, with_dog, model):
    desc, kind, base, _, dog_key = ITEMS[key]
    cname, chex, _ = COLORS[color]
    who = model or ("a woman in her 30s, slim athletic build" if key.startswith("w-")
                    else "a man in his 30s, athletic build")
    dog = ""
    if with_dog and dog_key:
        ddesc = ITEMS[dog_key][0]
        dog = (f" A French Bulldog sits upright at the model's knee wearing {ddesc} in the same {cname}, with the same "
               f"tonal embroidered Frenchie mark ({DOG_MARK}).")
    p = (f"Ultra-clean e-commerce product photograph in the style of James Perse. {who.capitalize()}, neutral expression, "
         "standing straight on, arms relaxed at sides, full-length crop from mid-thigh up, looking at the camera. "
         f"Wearing {desc} in {cname} {chex}. Front is completely clean except one small tonal embroidered crowned Frenchie "
         f"on the left chest, {HUMAN_MARK}, the size of a polo pony, thread the same color as the fabric. No graphics, no text "
         f"on the front.{dog} Background: {BACKDROP}, {LIGHT}. Shot on 85mm lens, true-to-life color, sharp fabric texture. {TAIL}")
    return code(tier, key, color, "MODEL-HERO"), "(text only)", "", p


def model_swap(key, hero_color, color, tier, with_dog):
    desc, kind, _, _, dog_key = ITEMS[key]
    cname, chex, _ = COLORS[color]
    both = "the human garment and the dog garment" if (with_dog and dog_key) else "the garment"
    p = (f"Image 1 is the approved hero photo. Keep the same model, same face, same pose, same framing, same crop, same "
         f"background ({BG_SHORT}), same lighting, same fabric folds and the same Frenchie mark size and position"
         f"{', same dog' if with_dog and dog_key else ''}. Change ONLY the fabric color of {both} to {cname} {chex}, "
         "including trims. The tonal mark thread matches the new fabric color. Change nothing else. " + TAIL)
    return code(tier, key, color, "MODEL"), code(tier, key, hero_color, "MODEL-HERO") + ".jpg", "", p


def pair(key, color, tier):
    desc, kind, base, _, dog_key = ITEMS[key]
    if not dog_key:
        sys.exit(f"'{key}' is a dog item; pair mode needs a human item.")
    ddesc, _, dbase, _, _ = ITEMS[dog_key]
    cname, chex, _ = COLORS[color]
    p = (f"Image 1 is {desc} flat lay (approved base). Image 2 is {ddesc} flat lay (approved base). Show them together in one "
         f"flat lay, the human piece centered and the dog piece placed to its lower right, both in {cname} {chex}, "
         f"both with the tonal embroidered Frenchie on the left chest (human {HUMAN_MARK}, dog {DOG_MARK}), polo-pony small, "
         f"front otherwise clean, no graphics on the front. Background: {BACKDROP}, {LIGHT}. {TAIL}")
    return code(tier, key + "+" + dog_key, color, "PAIR"), f"{base} | {dbase}", "", p


def back(key, color, tier, art, width):
    desc, kind, base, _, _ = ITEMS[key]
    cname, chex, _ = COLORS[color]
    if not art:
        sys.exit("back mode needs --art \"description of the artwork\" (and a graphic file as image 2)")
    p = (f"Image 1 is the BACK view of {desc} in {cname} {chex}. Image 2 is the artwork: {art}. Put the artwork from image 2 on "
         f"the upper back, centered, {width} wide, about 4 in below the collar or hood seam. Keep the artwork exactly as it is: "
         f"same letters, same texture, same colors, no new text. Keep the same flat lay: same back-view angle, same {BG_SHORT}, "
         "same soft shadow, no caption or label text anywhere. Show only the garment.")
    return code(tier, key, color, "BACK"), f"{desc.replace('a ', '', 1)} BACK view ({cname})", "ARTWORK.png", p


def main():
    ap = argparse.ArgumentParser(description="DSS mockup prompt generator")
    ap.add_argument("--item", help="; ".join(ITEMS))
    ap.add_argument("--colors", default="BLK", help="comma list of color codes, e.g. BLK,BNE,CAM")
    ap.add_argument("--mode", default="recolor", choices=["recolor", "model", "pair", "back"])
    ap.add_argument("--tier", default="A", choices=list(TIERS), help="A Activé, L La Rue, N Noir, X La Rue Limited")
    ap.add_argument("--with-dog", action="store_true", help="model mode: add the matching dog")
    ap.add_argument("--model", help="model mode: override the model description")
    ap.add_argument("--art", help="back mode: artwork description")
    ap.add_argument("--width", default="~11 in", help="back mode: artwork width")
    ap.add_argument("--out", default="out", help="output folder")
    ap.add_argument("--bases", default="img", help="folder of approved base images to check inputs against (default: img)")
    ap.add_argument("--list", action="store_true", help="list items and colors")
    a = ap.parse_args()

    if a.list:
        print("ITEMS:", ", ".join(ITEMS)); print("COLORS:")
        for k, (n, h, s) in COLORS.items(): print(f"  {k}  {n:10s} {h}  ({s})")
        return
    if a.item not in ITEMS:
        sys.exit(f"Unknown --item '{a.item}'. Run --list.")
    colors = [c.strip().upper() for c in a.colors.split(",") if c.strip()]
    bad = [c for c in colors if c not in COLORS]
    if bad: sys.exit(f"Unknown color code(s): {', '.join(bad)}. Run --list.")

    rows, warns = [], []
    for c in colors:
        w = scope_warning(c, a.tier)
        if w: warns.append(w)
    if a.mode == "model":
        hero = colors[0]
        rows.append(model_hero(a.item, hero, a.tier, a.with_dog, a.model))
        for c in colors[1:]:
            rows.append(model_swap(a.item, hero, c, a.tier, a.with_dog))
    else:
        for c in colors:
            if a.mode == "recolor": rows.append(recolor(a.item, c, a.tier))
            elif a.mode == "pair": rows.append(pair(a.item, c, a.tier))
            elif a.mode == "back": rows.append(back(a.item, c, a.tier, a.art, a.width))

    if os.path.isdir(a.bases):
        for cd, in1, in2, _ in rows:
            for fn in [x.strip() for x in (in1 + "|" + in2).split("|") if x.strip().lower().endswith((".jpg", ".png"))]:
                if not os.path.exists(os.path.join(a.bases, fn)) and not fn.startswith(("A-", "L-", "N-", "X-")):
                    warns.append(f"MISSING INPUT in {a.bases}/: {fn} (needed for {cd}); create/approve this base first.")
        warns = list(dict.fromkeys(warns))
    os.makedirs(a.out, exist_ok=True)
    stem = f"mockups-{a.item}-{a.mode}"
    with open(os.path.join(a.out, stem + ".csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["seq", "code", "input1", "input2", "prompt"])
        for i, r in enumerate(rows, 1): w.writerow([f"{i:02d}", *r])
    lines = [f"# DSS mockups: {a.item} / {a.mode} / tier {TIERS[a.tier]}  (standard {VER}, backdrop {BACKDROP_HEX})", ""]
    lines += [f"> {w}" for w in warns] + ([""] if warns else [])
    if a.mode == "model":
        lines += ["Run the HERO first. Approve it. Then attach the approved hero as image 1 for every swap.", ""]
    for i, (cd, in1, in2, pr) in enumerate(rows, 1):
        ins = f"Input 1: {in1}" + (f" | Input 2: {in2}" if in2 else "")
        lines += [f"**{i:02d} {cd}**  {ins}", f"Prompt: \"{pr}\"", ""]
    text = "\n".join(lines)
    with open(os.path.join(a.out, stem + ".md"), "w") as f: f.write(text)
    print(text); print(f"\nWrote {a.out}/{stem}.md and .csv ({len(rows)} prompts)")


if __name__ == "__main__":
    main()
