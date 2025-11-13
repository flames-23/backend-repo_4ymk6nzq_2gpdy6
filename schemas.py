"""
Database Schemas for the Flipkart-style store

Each Pydantic model corresponds to a MongoDB collection with the lowercase class name.
Examples:
- Product -> "product"
- Category -> "category"
- Order -> "order"
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Category(BaseModel):
    name: str = Field(..., description="Display name of the category")
    slug: str = Field(..., description="URL-friendly unique identifier")
    icon: Optional[str] = Field(None, description="Icon name or URL")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in currency units")
    mrp: Optional[float] = Field(None, ge=0, description="Original price (for discount display)")
    brand: Optional[str] = Field(None, description="Brand name")
    category: str = Field(..., description="Category slug this product belongs to")
    rating: float = Field(4.2, ge=0, le=5, description="Average rating 0-5")
    rating_count: int = Field(0, ge=0, description="Number of ratings")
    images: List[str] = Field(default_factory=list, description="List of image URLs")
    specs: Optional[dict] = Field(default_factory=dict, description="Key spec attributes")
    stock: int = Field(100, ge=0, description="Available stock count")

class Banner(BaseModel):
    title: str
    subtitle: Optional[str] = None
    image: str
    cta_text: Optional[str] = None
    cta_link: Optional[str] = None

class OrderItem(BaseModel):
    product_id: str
    title: str
    price: float
    qty: int = Field(1, ge=1)
    image: Optional[str] = None

class Address(BaseModel):
    name: str
    phone: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    zip: str

class Payment(BaseModel):
    method: str = Field(..., description="cod | card | upi")
    status: str = Field("pending", description="pending | paid | failed")
    txn_id: Optional[str] = None

class Order(BaseModel):
    items: List[OrderItem]
    subtotal: float
    shipping: float
    total: float
    address: Address
    payment: Payment
    placed_at: Optional[datetime] = None
