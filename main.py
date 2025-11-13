import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Category, Banner, Order

app = FastAPI(title="Flipkart+ API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductCreate(Product):
    pass

class CategoryCreate(Category):
    pass

class BannerCreate(Banner):
    pass

class OrderCreate(Order):
    pass


@app.get("/")
def root():
    return {"name": "Flipkart+ Backend", "status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Seed minimal demo data if empty
@app.post("/seed")
def seed():
    created = {"categories": 0, "products": 0, "banners": 0}

    if db["category"].count_documents({}) == 0:
        demo_categories = [
            {"name": "Mobiles", "slug": "mobiles", "icon": "Smartphone"},
            {"name": "Electronics", "slug": "electronics", "icon": "Tv"},
            {"name": "Fashion", "slug": "fashion", "icon": "Shirt"},
            {"name": "Home", "slug": "home", "icon": "Home"},
        ]
        for c in demo_categories:
            create_document("category", c)
            created["categories"] += 1

    if db["banner"].count_documents({}) == 0:
        demo_banners = [
            {"title": "Festival of Deals", "subtitle": "Top offers across categories", "image": "https://images.unsplash.com/photo-1512295767273-ac109ac3acfa", "cta_text": "Shop Now", "cta_link": "/"},
            {"title": "Smartphone Bonanza", "subtitle": "Latest 5G phones", "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9", "cta_text": "Explore", "cta_link": "/"}
        ]
        for b in demo_banners:
            create_document("banner", b)
            created["banners"] += 1

    if db["product"].count_documents({}) == 0:
        demo_products = [
            {
                "title": "Pixel 8 Pro",
                "description": "Google's flagship with AI features",
                "price": 999,
                "mrp": 1099,
                "brand": "Google",
                "category": "mobiles",
                "rating": 4.6,
                "rating_count": 2143,
                "images": ["https://images.unsplash.com/photo-1696446676203-8fd2c6ad38ef"],
                "specs": {"storage": "256GB", "ram": "12GB"},
                "stock": 50
            },
            {
                "title": "Sony WH-1000XM5",
                "description": "Industry-leading noise cancelling",
                "price": 349,
                "mrp": 399,
                "brand": "Sony",
                "category": "electronics",
                "rating": 4.8,
                "rating_count": 9812,
                "images": ["https://images.unsplash.com/photo-1518449007433-6f1ec0bc8e88"],
                "specs": {"type": "Over-ear", "battery": "30h"},
                "stock": 120
            }
        ]
        for p in demo_products:
            create_document("product", p)
            created["products"] += 1

    return {"seeded": created}


# Public catalog APIs
@app.get("/categories")
def list_categories():
    cats = get_documents("category")
    return cats


@app.get("/banners")
def list_banners():
    banners = get_documents("banner")
    return banners


@app.get("/products")
def list_products(q: Optional[str] = None, category: Optional[str] = None, limit: int = 24):
    filter_dict = {}
    if q:
        # Basic text search using regex
        filter_dict["title"] = {"$regex": q, "$options": "i"}
    if category:
        filter_dict["category"] = category
    prods = get_documents("product", filter_dict, limit)
    return prods


@app.get("/products/{product_id}")
def get_product(product_id: str):
    try:
        doc = db["product"].find_one({"_id": ObjectId(product_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Product not found")
        return doc
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")


# Order create (mock payment)
@app.post("/orders")
def create_order(order: Order):
    data = order.model_dump()
    # compute totals server-side as basic safety
    subtotal = sum([item["price"] * item["qty"] for item in data["items"]])
    data["subtotal"] = subtotal
    data["total"] = subtotal + data.get("shipping", 0)
    order_id = create_document("order", data)
    return {"order_id": order_id, "status": "received"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
