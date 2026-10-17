#!/usr/bin/env python3
"""Build the Shopify attach plan from finished files in jobs/done/.
File name = <handle>__<SHOT>__v1.jpg, looked up in shopify_map.csv. Output: attach_plan.json
(list of {product_gid, handle, originalSource (raw.githubusercontent URL), alt, order}) ready for productCreateMedia.
"""
import csv, json, os
R = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/jnorv2628/dss-white-bases/main/jobs/done/"
m = {r["output_name"]: r for r in csv.DictReader(open(os.path.join(R, "shopify_map.csv"), encoding="utf-8"))}
plan, unknown = {}, []
for f in sorted(os.listdir(os.path.join(R, "done"))):
    if f.startswith("."): continue
    r = m.get(f)
    if not r: unknown.append(f); continue
    plan.setdefault(r["product_gid"], []).append(dict(handle=r["handle"], originalSource=RAW+f, alt=r["alt"], order=int(r["gallery_order"]), mediaContentType="IMAGE"))
    for pair in filter(None, (r.get("also_handles") or "").split(";")):   # shared image (set flat-lay, model+dog): attach to every listed product
        h2, g2 = pair.split("=", 1)
        plan.setdefault(g2, []).append(dict(handle=h2, originalSource=RAW+f, alt=r["alt"], order=int(r["gallery_order"]), mediaContentType="IMAGE"))
for g in plan: plan[g].sort(key=lambda x: x["order"])
json.dump(plan, open(os.path.join(R, "attach_plan.json"), "w"), indent=1, ensure_ascii=False)
print(sum(len(v) for v in plan.values()), "images for", len(plan), "products; unmatched:", unknown)
