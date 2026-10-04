import json
import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from conflicts import find_conflicts
from recommender import recommend

DATA_FILE = Path(__file__).parent / "products.json"
if not DATA_FILE.exists():
    raise RuntimeError("products.json not found. Run data/clean.py first.")

PRODUCTS = json.loads(DATA_FILE.read_text())
PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}

app = FastAPI(title="Poor Little Thing API")

# Which websites are allowed to call this API.
allowed_origins = ["http://localhost:5173"]
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Quiz(BaseModel):
    skin_type: Literal["dry", "oily", "combination", "normal"]
    concerns: list[Literal["acne", "aging", "dullness", "dryness"]] = Field(max_length=4)
    max_price: float = Field(gt=0)


class ConflictCheck(BaseModel):
    product_ids: list[str] = Field(min_length=2, max_length=20)


def summary(product):
    """The fields the front end needs (skips the long ingredient list)."""
    keys = ["id", "name", "brand", "price", "rating", "review_count",
            "step", "actives", "reason"]
    return {k: product.get(k) for k in keys}


@app.get("/health")
def health():
    return {"status": "ok", "products": len(PRODUCTS)}


@app.get("/products")
def search_products(q: str = "", step: str | None = None, limit: int = 20):
    q = q.lower()
    results = [
        p for p in PRODUCTS
        if (q in p["name"].lower() or q in p["brand"].lower())
        and (step is None or p["step"] == step)
    ]
    return [summary(p) for p in results[:min(limit, 50)]]


@app.get("/products/{product_id}")
def get_product(product_id: str):
    product = PRODUCTS_BY_ID.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/recommend")
def get_recommendation(quiz: Quiz):
    result = recommend(PRODUCTS, quiz.skin_type, quiz.concerns, quiz.max_price)
    return {
        "am": [summary(p) for p in result["am"]],
        "pm": [summary(p) for p in result["pm"]],
    }

@app.post("/check-conflicts")
def check_conflicts(body: ConflictCheck):
    products = []
    for pid in body.product_ids:
        product = PRODUCTS_BY_ID.get(pid)
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product {pid} not found")
        products.append(product)
    return {"conflicts": find_conflicts(products)}
