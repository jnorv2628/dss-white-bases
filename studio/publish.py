#!/usr/bin/env python3
"""Build the Shopify productSet input from a mockup manifest.  Prints JSON only; nothing is sent.
Rule: refuses to build a payload unless every image file exists and every color has an image.

  python studio/publish.py --handle dog-days-society-hoodie --title "Dog Days Society Hoodie" \
     --garment hoodie --tier A --capsule DDS --tagline "..." --base-url https://raw.githubusercontent.com/jnorv2628/dss-white-bases/main
"""
import argparse, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "studio"))
from catalog import GARMENTS, TIERS, description
from mockup import COLORS

ap = argparse.ArgumentParser()
ap.add_argument("--handle", required=True); ap.add_argument("--title", required=True)
ap.add_argument("--garment", required=True); ap.add_argument("--tier", default="A")
ap.add_argument("--capsule", required=True); ap.add_argument("--tagline", required=True)
ap.add_argument("--price", type=float); ap.add_argument("--status", default="DRAFT")
ap.add_argument("--base-url", default="https://raw.githubusercontent.com/jnorv2628/dss-white-bases/main")
ap.add_argument("--out")
a = ap.parse_args()

man = json.load(open(os.path.join(ROOT, "mockups", a.handle, "manifest.json")))
g = GARMENTS[a.garment]; price = a.price or g["price"][a.tier]
imgs = man["images"]; missing = [i["file"] for i in imgs if not os.path.exists(os.path.join(ROOT, "mockups", a.handle, i["file"]))]
if not imgs or missing: sys.exit(f"REFUSED: no images or missing files {missing}")
colors = []
for i in imgs:
    if i["color"] not in colors: colors.append(i["color"])
# hero = first back image of first color; then every other image
files = [{"originalSource": f"{a.base_url}/mockups/{a.handle}/{i['file']}", "alt": i["alt"], "contentType": "IMAGE",
          "filename": i["file"]} for i in imgs]
color_file = {i["color"]: f for i, f in zip(imgs, files) if i["view"] == "back"}
if set(colors) - set(color_file): sys.exit("REFUSED: a color has no back image")
names = [COLORS[c][0] for c in colors]
variants = []
for c in colors:
    for s in g["sizes"]:
        variants.append({"optionValues": [{"optionName": "Color", "name": COLORS[c][0]}, {"optionName": "Size", "name": s}],
                         "price": f"{price:.2f}", "sku": f"DSS-{a.capsule}-{g['style']}-{c}-{s}",
                         "inventoryPolicy": "CONTINUE", "file": color_file[c],
                         "inventoryItem": {"tracked": False, "requiresShipping": True}})
payload = {"title": a.title, "handle": a.handle, "vendor": "Doggy Style Society", "productType": g["ptype"],
           "status": a.status, "tags": ["DSS", TIERS[a.tier][0], a.capsule, g["label"]],
           "descriptionHtml": description(a.title, a.garment, a.tier, a.tagline, names, front_mark=any(i["view"] == "front" for i in imgs)),
           "productOptions": [{"name": "Color", "values": [{"name": n} for n in names]},
                              {"name": "Size", "values": [{"name": s} for s in g["sizes"]]}],
           "files": files, "variants": variants}
out = json.dumps({"input": payload}, indent=1)
if a.out: open(a.out, "w").write(out)
print(f"ok: {len(files)} images, {len(variants)} variants, ${price:.2f}", file=sys.stderr)
print(out if not a.out else a.out)
