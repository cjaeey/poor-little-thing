from recommender import recommend, trusted_rating


def product(pid, step, price=30, rating=4.5, reviews=200, actives=None, skin=None):
    return {
        "id": pid, "name": pid, "brand": "Test", "step": step, "price": price,
        "rating": rating, "review_count": reviews, "actives": actives or [],
        "ingredients": ["Water", "Glycerin"], "skin_type_ratings": skin or {},
        "out_of_stock": False,
    }


CATALOG = [
    product("cleanser", "cleanser"),
    product("moisturizer", "moisturizer"),
    product("sunscreen", "sunscreen"),
    product("retinol", "serum", actives=["retinoid"]),
    product("vitc", "serum", actives=["vitamin_c"]),
    product("pricey", "serum", price=200, rating=5.0, reviews=5000),
]


def test_retinol_only_goes_in_pm():
    result = recommend(CATALOG, "oily", ["aging"], max_price=100)
    am_ids = [p["id"] for p in result["am"]]
    pm_ids = [p["id"] for p in result["pm"]]
    assert "retinol" not in am_ids
    assert "retinol" in pm_ids
    assert "vitc" in am_ids


def test_budget_is_respected():
    result = recommend(CATALOG, "dry", [], max_price=50)
    all_products = result["am"] + result["pm"]
    assert all(p["price"] <= 50 for p in all_products)


def test_few_reviews_are_trusted_less():
    loved_by_few = product("a", "serum", rating=5.0, reviews=3)
    solid = product("b", "serum", rating=4.6, reviews=2000)
    assert trusted_rating(solid, "oily")[0] > trusted_rating(loved_by_few, "oily")[0]


def test_uses_skin_type_rating_when_available():
    p = product("x", "serum", skin={"oily": {"avg": 4.8, "n": 300}})
    score, reason = trusted_rating(p, "oily")
    assert "oily skin" in reason


def test_same_skin_reviews_beat_overall_fallback():
    has_oily = product("a", "serum", skin={"oily": {"avg": 4.6, "n": 200}})
    no_oily = product("b", "serum", rating=4.9, reviews=300)
    assert trusted_rating(has_oily, "oily")[0] > trusted_rating(no_oily, "oily")[0]
