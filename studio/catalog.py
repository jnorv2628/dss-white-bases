"""DSS catalog: garment types, tier prices, sizes, and description copy.  One place to edit.
Copy rules (locked): no raw fiber names, no health claims, no fake scarcity, no invented origin/certs."""

SIZES_M = ["S", "M", "L", "XL", "2XL", "3XL"]
SIZES_W = ["XS", "S", "M", "L", "XL", "2XL"]
SIZES_HOODIE = ["XS", "S", "M", "L", "XL", "2XL", "3XL"]

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
    return (f"<p>{tagline}</p><ul>{lis}</ul>{extra}"
            "<p><em>Doggy Style Society. Los Angeles.</em></p>")
