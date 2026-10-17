# DSS mockup command

One command, same standard every time (warm backdrop #E9E4D8, soft light, graphics on the BACK, front clean with one tonal Frenchie).
No installs needed: Python 3 only.

## Run it anywhere
    python3 mockup.py --item tee --colors BLK,BNE,ESP,OLV,CHR,BLS --mode model --with-dog --tier A
    python3 mockup.py --item hoodie --colors BLK,BNE,CAM --mode recolor --tier N
    python3 mockup.py --item tee --colors BLK --mode pair --tier A
    python3 mockup.py --item tee --colors BLK --mode back --art "FRENCHIE AF drip lettering" --width "~11 in"
    python3 mockup.py --list

Modes: `recolor` (flat lay, the spec's standard), `model` (James Perse model shot: hero, then one swap per color),
`pair` (human + dog flat lay), `back` (graphic on the upper back).
Results print on screen and save to `out/` as .md (read/paste) and .csv (tracking).

## Run it from GitHub (works from the phone app)
Put `mockup.py` in the repo root and `.github/workflows/mockups.yml` in place. Then: Actions tab -> "DSS mockup prompts" ->
Run workflow -> fill in item, colors, mode, tier. The prompts show on the run summary page and download as an artifact.

## Change the look of every prompt
Edit the STANDARD block at the top of `mockup.py` (backdrop, light, mark sizes, colors). Never edit a prompt by hand.
Color codes come from DSS-COLOR-MASTER. The script warns when a color is scoped to a different tier.

## White only in Meta, colors on our side (v3.1)

Meta makes ONLY the white mockups. Every other color is made by `recolor.py` from the approved white image.

1. `python mockup.py --item w-bralette --mode white --art "<back artwork>" --width "~7 in"` writes the white front + back prompts (default mode).
2. Run those in Meta, approve the white images.
3. `python recolor.py --in <approved-white-front.jpg> --colors ALL --out out/colors` makes every color-master color with the same folds, texture and tonal mark. Check the `__MASK-CHECK.jpg` it writes (red = garment) before using the files.

Limits: tonal marks recolor with the fabric. Fixed-color graphics (e.g. white drip lettering on a dark garment) must be placed after recoloring. Enclosed backdrop gaps (inside strap loops) may need `--mask`.
