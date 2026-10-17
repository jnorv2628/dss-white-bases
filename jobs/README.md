# jobs/  (Claude <-> Meta handoff through this repo)

Claude writes work orders. Meta fills them. Claude checks and ships to Shopify.

1. QUEUE: `queue.csv` is the work list. Columns: job_id, status, input_image (path in this repo), prompt, output_name.
   status goes OPEN -> SUBMITTED (Meta output landed in inbox/) -> DONE (checked, coded, moved) or REDO (note says why).
2. META: read an OPEN row, use `input_image` as image 1 with `prompt`, and save the result to `inbox/` named exactly `output_name`.
3. CLAUDE: when a file lands in `inbox/`, I dedupe it, remove the caption, size it to 1296x1616, check backdrop and garment color,
   code it, move it to `mockups/<product>/` and `done/`, then attach it to the Shopify product through its raw.githubusercontent URL.

Division of labor (updated 2026-10-17):
- META: graphic placement on the back (flat-design jobs), flatlays, and every close-up / material / hardware shot in queue.csv.
- CLAUDE: colors that are tonal-only (recolor.py), QA, uniform 1296x1616 sizing, coding, Shopify attach, descriptions.

Close-up system (closeups.py):
- `python3 closeups.py` regenerates the CU#### rows from `shopify_products.csv` (the live catalog). Rows with a known color are OPEN;
  rows marked HOLD_COLOR wait until the garment color is confirmed from the product hero photo.
- Output file name is the code: `<shopify-handle>__<SHOT>__v1.jpg`. `shopify_map.csv` maps each name to product id, gallery order and alt text.
- Finished, checked files go to `done/`. `python3 attach_plan.py` builds `attach_plan.json` (raw.githubusercontent URLs in gallery order) and
  Claude pushes it to Shopify with productCreateMedia. No manual matching.
- `needs_base.csv` lists products with no white base yet (bucket hat, leg warmers, pair set).

Never commit nudity or a third-party model photo. Never commit another company's name or label.
