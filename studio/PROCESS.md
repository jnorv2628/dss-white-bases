# DSS mockup process: graphic in, Shopify-ready images out

One graphic + one placement decision -> every image a product needs, named and ordered.

## The six steps
1. **Art in.** Drop a transparent PNG at `art/<DESIGN>/back.png` (and optional `front.png` mark). Raw art stays in the PRIVATE studio repo, never the public one.
2. **Placement.** Set the print box once per base photo in `studio/placements.json` (center x, top, width). Every design on that garment reuses it.
3. **Flat mockups, automatic.** `python studio/compose.py --design DDS --handle dog-days-society-hoodie --colors BLK,WHT`
   Front + back for every color, ink flips light/dark for contrast, fabric folds show through. Writes `mockups/<handle>/NN-view-COLOR.jpg` + `manifest.json`.
4. **Model / mannequin / dog-pair photos (Meta, manual hop).** Meta AI has no API, so this is the one step that needs a human: take the flat mockup, run the prompt for the shot type (`mockup.py` already writes the model / pair / back prompts), save the result into `intake/<handle>/` as `model-front.jpg`, `model-back.jpg`, `mannequin.jpg`, `pair-dog.jpg`.
5. **Ingest.** Intake files are renamed to the SKU-ordered convention, added to `manifest.json`, and pushed to the public repo `mockups/<handle>/`.
6. **Shopify, automatic.** The product is created or updated from the manifest (images attached on create, color variants linked to their color image). Rule: a product is never created or activated unless every image is attached and READY.

## Image order on every product
01 front (hero color) · 02 back · 03 side (Meta) · 04 mannequin (Meta) · 05 model front · 06 model back · 07 dog pair · then per-color front/back.

## What is automatic vs manual
| Automatic (no AI) | Needs Meta |
|---|---|
| flat front/back, all colors | 3D mannequin |
| naming, ordering, alt text | model wearing it |
| push to public repo | model + matching dog |
| create/update Shopify product with images | side view |

## Known limits
- Cut-out masks are cached in `studio/masks/`; if a base's edges look rough, fix that mask once and every design benefits.
- Only the hoodie bases are registered. Tee, zip hoodie and long sleeve need their own base photos and print boxes.
