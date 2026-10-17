# jobs/  (Claude <-> Meta handoff through this repo)

Claude writes work orders. Meta fills them. Claude checks and ships to Shopify.

1. QUEUE: `queue.csv` is the work list. Columns: job_id, status, input_image (path in this repo), prompt, output_name.
   status goes OPEN -> SUBMITTED (Meta output landed in inbox/) -> DONE (checked, coded, moved) or REDO (note says why).
2. META: read an OPEN row, use `input_image` as image 1 with `prompt`, and save the result to `inbox/` named exactly `output_name`.
3. CLAUDE: when a file lands in `inbox/`, I dedupe it, remove the caption, size it to 1296x1616, check backdrop and garment color,
   code it, move it to `mockups/<product>/` and `done/`, then attach it to the Shopify product through its raw.githubusercontent URL.

Division of labor (saves Meta credits):
- Claude alone (no Meta): every color from a white base (recolor.py), flat-print designs on a base (compose.py), uniform sizing, Shopify attach.
- Meta only: new white bases that do not exist yet, and shots that need a person or a dog in them.

Never commit nudity or a third-party model photo. Never commit another company's name or label.
