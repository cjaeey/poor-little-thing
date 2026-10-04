"""Builds an AM and PM routine from quiz answers."""
from conflicts import conflicts_with_any

# Bayesian average settings: a product needs reviews before its rating is trusted.
PRIOR_REVIEWS = 50    # how many "average" reviews every product starts with
PRIOR_RATING = 4.2    # roughly the average rating on Sephora

AM_STEPS = ["cleanser", "serum", "moisturizer", "sunscreen"]
PM_STEPS = ["cleanser", "serum", "moisturizer"]

# Which actives to look for in the serum step, based on the user's concerns.
PM_SERUM_ACTIVES = {
    "acne": ["bha", "benzoyl_peroxide"],
    "aging": ["retinoid"],
    "dullness": ["aha"],
    "dryness": [],
}
AM_SERUM_ACTIVES = {
    "acne": ["niacinamide"],
    "aging": ["vitamin_c"],
    "dullness": ["vitamin_c"],
    "dryness": [],
}
# Actives that make skin more sun-sensitive: keep them out of the AM routine.
NOT_IN_AM = {"retinoid", "aha"}
HYDRATORS = ["hyaluronic", "ceramide", "squalane", "glycerin"]


def trusted_rating(product, skin_type):
    """Return (score, reason). Prefers ratings from reviewers with the same skin type."""
    by_skin = product.get("skin_type_ratings", {}).get(skin_type)
    if by_skin:
        rating, count = by_skin["avg"], by_skin["n"]
        reason = f"Rated {rating} by {count} reviewers with {skin_type} skin"
    else:
        rating, count = product.get("rating") or 0, product.get("review_count") or 0
        reason = f"Rated {rating} overall ({count} reviews)"
    score = (count * rating + PRIOR_REVIEWS * PRIOR_RATING) / (count + PRIOR_REVIEWS)
    return score, reason


def score_product(product, skin_type, wanted_actives, concerns):
    score, reason = trusted_rating(product, skin_type)
    if wanted_actives and any(a in product["actives"] for a in wanted_actives):
        score += 1.0
    if "dryness" in concerns:
        ingredients = " ".join(product["ingredients"]).lower()
        if any(h in ingredients for h in HYDRATORS):
            score += 0.3
    return score, reason


def wanted_for(step, time_of_day, concerns):
    if step != "serum":
        return []
    table = AM_SERUM_ACTIVES if time_of_day == "am" else PM_SERUM_ACTIVES
    return [a for c in concerns for a in table.get(c, [])]


def build_routine(products, steps, time_of_day, skin_type, concerns, max_price):
    routine = []
    for step in steps:
        wanted = wanted_for(step, time_of_day, concerns)
        candidates = [
            p for p in products
            if p["step"] == step
            and p["price"] <= max_price
            and not p.get("out_of_stock")
            and not (time_of_day == "am" and NOT_IN_AM & set(p["actives"]))
        ]
        scored = sorted(
            ((score_product(p, skin_type, wanted, concerns), p) for p in candidates),
            key=lambda pair: pair[0][0],
            reverse=True,
        )
        for (score, reason), product in scored:
            if not conflicts_with_any(product, routine):
                routine.append({**product, "reason": reason, "score": round(score, 3)})
                break
    return routine


def recommend(products, skin_type, concerns, max_price):
    return {
        "am": build_routine(products, AM_STEPS, "am", skin_type, concerns, max_price),
        "pm": build_routine(products, PM_STEPS, "pm", skin_type, concerns, max_price),
    }