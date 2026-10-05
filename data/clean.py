"""

clean.py turns the Kaggle Sephora dataset into products.json
for poor little thing.

Dataset Credits:
https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews?resource=download

"""

import ast
import glob
import json
import os

import pandas as pd

RAW_DIR = "raw"
OUT_FILE = os.path.join("..", "backend", "products.json")
MIN_REVIEWS_PER_SKIN_TYPE = 20 # ignore skin-type ratings with too few reviews

# Map Sephora's category breadcrumbs to steps in a routine
# Run once and check the printed category counts, then adjust these keywords.

STEP_KEYWORDS = {
    "eye": ["eye"],  # first, so "Eye Creams & Treatments" isn't labeled a serum
    "cleanser": ["cleanser", "face wash", "makeup remover", "exfoliator"],
    "toner": ["toner", "mist", "essence"],
    "serum": ["serum", "treatment", "face oil", "facial peel", "blemish"],
    "moisturizer": ["moisturizer", "night cream"],
    "sunscreen": ["sunscreen", "spf"],
    "mask": ["mask"],
}
SKIP_SECONDARY = {"Value & Gift Sets", "Mini Size", "High Tech Tools", "Self Tanners", "Wellness"}

# Active ingredients the conflict checker cares about.
ACTIVES = {
    "retinoid": ["retinol", "retinal", "retinyl", "hydroxypinacolone retinoate"],
    "aha": ["glycolic acid", "lactic acid", "mandelic acid"],
    "bha": ["salicylic acid"],
    "benzoyl_peroxide": ["benzoyl peroxide"],
    "vitamin_c": ["ascorbic acid"],
    "niacinamide": ["niacinamide"],
}

def parse_list(value):
    """The CSV stores lists as strings like "['Vegan', 'Matte Finish']"."""
    if pd.isna(value):
        return []
    try:
        parsed = ast.literal_eval(value)
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except (ValueError, SyntaxError):
        return [str(value)]
    
def main_formula(raw_ingredients):
    """Pick the main ingredient list out of the messy ingredients field.

    Entries can be headers ("Product variation 1:"), marketing notes
    ("-Niacinamide: Brightens."), or the actual comma-separated list.
    We take the first entry that looks like a real list.
    """
    for entry in parse_list(raw_ingredients):
        entry = entry.strip()
        if entry.endswith(":") or entry.startswith("-"):
            continue
        if entry.count(",") >= 3:
            return [i.strip().rstrip(".") for i in entry.split(",") if i.strip()]
    return []

def detect_actives(ingredients):
    text = " ".join(ingredients).lower()
    return [name for name, words in ACTIVES.items() if any(w in text for w in words)]


def routine_step(secondary, tertiary):
    # Check the more specific tertiary category first ("Toners" lives under
    # "Cleansers"), then fall back to the secondary category.
    for text in (tertiary, secondary):
        text = (text or "").lower()
        for step, words in STEP_KEYWORDS.items():
            if any(w in text for w in words):
                return step
    return None


def skin_type_ratings(product_ids):
    """Average rating per product per reviewer skin type, e.g.
    {"oily": {"avg": 4.4, "n": 312}, "dry": {...}}"""
    files = sorted(glob.glob(os.path.join(RAW_DIR, "reviews_*.csv")))
    if not files:
        print("No review files found, skipping skin-type ratings.")
        return {}

    # Only load the 3 columns we need; the full review files are ~500 MB.
    cols = ["product_id", "rating", "skin_type"]
    reviews = pd.concat(
        (pd.read_csv(f, usecols=cols, low_memory=False) for f in files),
        ignore_index=True,
    )
    reviews = reviews[reviews["product_id"].isin(product_ids)].dropna()

    stats = (reviews.groupby(["product_id", "skin_type"])["rating"]
             .agg(avg="mean", n="count").reset_index())
    stats = stats[stats["n"] >= MIN_REVIEWS_PER_SKIN_TYPE]

    result = {}
    for row in stats.itertuples():
        result.setdefault(row.product_id, {})[row.skin_type] = {
            "avg": round(row.avg, 2), "n": int(row.n)}
    print(f"Loaded {len(reviews):,} reviews -> skin-type ratings for {len(result):,} products")
    return result


def main():
    df = pd.read_csv(os.path.join(RAW_DIR, "product_info.csv"))
    print(f"Loaded {len(df):,} products")

    df = df[df["primary_category"] == "Skincare"]
    df = df[~df["secondary_category"].isin(SKIP_SECONDARY)]
    print(f"Skincare products (no sets/minis/tools): {len(df):,}")

    print("\nCategory counts (use these to tune STEP_KEYWORDS):")
    print(df.groupby(["secondary_category", "tertiary_category"], dropna=False)
          .size().sort_values(ascending=False).to_string())

    ratings_by_skin = skin_type_ratings(set(df["product_id"]))

    products = []
    for row in df.itertuples():
        step = routine_step(None if pd.isna(row.secondary_category) else row.secondary_category,
                            None if pd.isna(row.tertiary_category) else row.tertiary_category)
        ingredients = main_formula(row.ingredients)
        if step is None or not ingredients or pd.isna(row.price_usd):
            continue
        products.append({
            "id": row.product_id,
            "name": row.product_name,
            "brand": row.brand_name,
            "price": float(row.price_usd),
            "rating": None if pd.isna(row.rating) else round(float(row.rating), 2),
            "review_count": None if pd.isna(row.reviews) else int(row.reviews),
            "loves": int(row.loves_count),
            "step": step,
            "highlights": parse_list(row.highlights),
            "ingredients": ingredients,
            "actives": detect_actives(ingredients),
            "skin_type_ratings": ratings_by_skin.get(row.product_id, {}),
            "out_of_stock": bool(row.out_of_stock),
        })

    with open(OUT_FILE, "w") as f:
        json.dump(products, f)

    steps = pd.Series([p["step"] for p in products]).value_counts()
    print(f"\nWrote {len(products):,} products to {OUT_FILE}")
    print(steps.to_string())


if __name__ == "__main__":
    main()