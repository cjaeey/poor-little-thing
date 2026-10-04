"""Rules for active ingredients that shouldn't be layered in the same routine."""

CONFLICT_RULES = [
    {"pair": {"retinoid", "aha"},
     "message": "Retinoids and AHAs together can over-exfoliate and irritate skin. Use them on different nights."},
    {"pair": {"retinoid", "bha"},
     "message": "Retinoids and BHAs together can be very drying. Alternate nights instead."},
    {"pair": {"retinoid", "benzoyl_peroxide"},
     "message": "Benzoyl peroxide can make some retinoids less effective. Use one in the AM and one in the PM."},
    {"pair": {"vitamin_c", "benzoyl_peroxide"},
     "message": "Benzoyl peroxide can oxidize vitamin C. Use them at different times of day."},
    {"pair": {"aha", "bha"},
     "message": "Two exfoliating acids in one routine can irritate skin. Start with one."},
]

# Strong actives where two products with the same one is too much.
NO_DOUBLING = {
    "retinoid": "a retinoid",
    "aha": "an AHA",
    "bha": "a BHA",
    "benzoyl_peroxide": "benzoyl peroxide",
}


def find_conflicts(products):
    """Return a list of conflicts between products in ONE routine."""
    conflicts = []
    for i, first in enumerate(products):
        for second in products[i + 1:]:
            for rule in CONFLICT_RULES:
                a, b = tuple(rule["pair"])
                if (a in first["actives"] and b in second["actives"]) or \
                   (b in first["actives"] and a in second["actives"]):
                    conflicts.append({
                        "products": [first["name"], second["name"]],
                        "actives": sorted(rule["pair"]),
                        "message": rule["message"],
                    })
            shared = set(first["actives"]) & set(second["actives"]) & set(NO_DOUBLING)
            for active in sorted(shared):
                conflicts.append({
                    "products": [first["name"], second["name"]],
                    "actives": [active],
                    "message": f"Both products contain {NO_DOUBLING[active]}. Doubling up can irritate skin, so use one per routine.",
                })
    return conflicts


def conflicts_with_any(candidate, chosen):
    """True if `candidate` conflicts with any product already in the routine."""
    return any(find_conflicts([candidate, product]) for product in chosen)
