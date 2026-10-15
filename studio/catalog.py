"""DSS catalog: garment types, tier prices, sizes, and description copy.  One place to edit.
Copy rules (locked): no raw fiber names, no health claims, no fake scarcity, no invented origin/certs."""

SIZES_M = ["S", "M", "L", "XL", "2XL", "3XL"]
SIZES_W = ["XS", "S", "M", "L", "XL", "2XL"]
SIZES_HOODIE = ["XS", "S", "M", "L", "XL", "2XL", "3XL"]

DOG_SIZE_ROWS = [("XXS","10–13","7–9","7–9"),("XS","13–16","9–11","9–11"),("S","16–19","11–13","11–13"),
    ("M","19–22","13–15","13–15"),("L","22–26","15–18","15–17"),("XL","26–30","18–21","17–19"),
    ("2XL","30–35","21–24","19–22"),("3XL","35–40","24–28","22–25")]
def dog_size_table():
    rows = "".join(f"<tr><td>{a}</td><td>{b} in</td><td>{c} in</td><td>{d} in</td></tr>" for a, b, c, d in DOG_SIZE_ROWS)
    return ('<h4>Find your dog\'s size</h4><table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%;text-align:left;">'
            f'<thead><tr><th>Size</th><th>Chest</th><th>Back</th><th>Neck</th></tr></thead><tbody>{rows}</tbody></table>'
            '<p>Size by chest first. See the full <a href="/pages/dog-size-chart">dog size and cut chart</a> for garment measurements and breed notes.</p>')

# garment key -> label, SKU style code, product type, sizes, price per tier, fit line
GARMENTS = {
    "hoodie":      dict(label="Hoodie", style="HOOD", ptype="Hoodies", sizes=SIZES_HOODIE,
                        price={"A": 198, "L": 269, "N": 450}, fit="Relaxed, roomy through the body, with a deep hood."),
    "zip-hoodie":  dict(label="Zip Hoodie", style="ZIP", ptype="Hoodies", sizes=SIZES_HOODIE,
                        price={"A": 198, "L": 299, "N": 450}, fit="Relaxed fit with a full-length zip and a deep hood."),
    "sweatshirt":  dict(label="Crewneck Sweatshirt", style="CREW", ptype="Sweatshirts", sizes=SIZES_M,
                        price={"A": 148, "L": 189, "N": 295}, fit="Relaxed crewneck with ribbed cuffs and hem."),
    "w-sweatshirt": dict(label="Women's Crewneck Sweatshirt", style="WCREW", ptype="Sweatshirts", sizes=SIZES_W,
                        price={"A": 148, "L": 189, "N": 295}, fit="Easy crewneck with ribbed cuffs and hem."),
    "dog-hoodie":  dict(label="Dog Hoodie", style="DHOOD", ptype="Dog Hoodies", sizes=["XS","S","M","L","XL","2XL","3XL"],
                        price={"A": 128, "L": 128, "N": 128}, fit="Cut for dogs, with a roomy hood and ribbed cuffs.", dog=True),
    "dog-tee":     dict(label="Dog Tee", style="DTEE", ptype="Dog Tees", sizes=["XS","S","M","L","XL"],
                        price={"A": 68, "L": 68, "N": 98}, fit="Cut for dogs, with a curved hem.", dog=True),
    "tee":         dict(label="Tee", style="TEE", ptype="Tees", sizes=SIZES_M,
                        price={"A": 88, "L": 148, "N": 225}, fit="Classic crew with a clean, easy drape."),
    "w-tee":       dict(label="Women's Tee", style="WTEE", ptype="Tees", sizes=SIZES_W,
                        price={"A": 88, "L": 148, "N": 225}, fit="Classic crew, slightly fitted, easy drape."),
    "ls-tee":      dict(label="Long Sleeve Tee", style="LS", ptype="Tees", sizes=SIZES_M,
                        price={"A": 98, "L": 158, "N": 235}, fit="Classic crew with full-length sleeves."),
}
TIERS = {
    "A": ("Activé", "A lighter-weight everyday fabric that moves with you."),
    "L": ("La Rue", "A heavier, structured fabric with a premium hand."),
    "N": ("Noir", "Our heaviest, most refined fabric, finished with tonal embroidery."),
}
# Deposit pieces (50% now, balance before shipping) - NOT the default; everything else is paid in full.
DEPOSIT_CATEGORIES = ["cashmere knits", "wool coats", "belts", "shoes"]
FULFILLMENT_WINDOW = "2 to 3 weeks"
COLOR_WORDS = {"BLK": "Black", "WHT": "White"}


def description(title, garment, tier, tagline, colors, extra="", front_mark=False):
    g = GARMENTS[garment]; tname, tfab = TIERS[tier]
    cn = ", ".join(colors)
    bullets = [
        f"{tname} tier. {tfab}",
        g["fit"],
        ("Graphic printed on the back. The front stays clean, with one small tonal crowned Frenchie at the chest."
         if front_mark else "Graphic printed on the back. The front stays clean."),
        f"Available in {cn}.",
        "Made to order for you. Delivered within 2 to 3 weeks, and you get tracking the moment it ships.",
        "Sizes: " + ", ".join(g["sizes"]) + ".",
    ]
    lis = "".join(f"<li>{b}</li>" for b in bullets)
    if g.get("dog"): extra += dog_size_table()
    return (f"<p>{tagline}</p><ul>{lis}</ul>{extra}"
            "<p><em>Doggy Style Society. Los Angeles.</em></p>")
