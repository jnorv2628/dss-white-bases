# DSS mockup command

One command, same standard every time (backdrop #E9E9E7, soft light, graphics on the BACK, front clean with one tonal Frenchie).
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
