from fastapi import FastAPI
import random

app = FastAPI(title="E-commerce Mock API")

PRODUCTS = [
    {
        "product_id": 101 + i,
        "name": f"Termék {chr(65+i)}",
        "category": random.choice(["Elektronika", "Ruházat", "Könyv"]),
        "metadata": {
            "is_active": True,
            "tags": ["akciós", "új"] if i % 2 == 0 else ["kifutó"]
        }
    } for i in range(10)
]

@app.get("/api/products")
def get_products():
    """Visszaadja a termékek listáját."""
    return {"status": "success", "data": PRODUCTS}

@app.get("/api/reviews")
def get_reviews(date: str = None):
    """Visszaadja a vásárlói értékeléseket. Beágyazott (nested) JSON struktúra."""
    reviews = []
    for _ in range(20):
        reviews.append({
            "review_id": random.randint(1000, 9999),
            "product_id": random.randint(101, 110),
            "customer_id": random.randint(1, 50),
            "rating": random.randint(1, 5),
            "review_text": "Ez egy teszt értékelés.",
            "context": {
                "verified_purchase": random.choice([True, False]),
                "device": random.choice(["mobile", "desktop"])
            }
        })
    return {"status": "success", "date": date, "data": reviews}

# Futtatás: uvicorn api_server:app --reload --port 8000