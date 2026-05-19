from __future__ import annotations
from typing import Optional, List, Any
from decimal import Decimal
from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr, field_validator


# ─────────────────────────── Brand ───────────────────────────

class BrandBase(BaseModel):
    name: str
    country: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None

class BrandCreate(BrandBase):
    pass

class BrandOut(BrandBase):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ─────────────────────────── Category ────────────────────────

class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None
    sort_order: int = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    children: List["CategoryOut"] = []
    model_config = {"from_attributes": True}


# ─────────────────────────── Tag ─────────────────────────────

class TagOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


# ─────────────────────────── Coupon ──────────────────────────

class CouponBase(BaseModel):
    code: str
    discount_pct: Optional[Decimal] = None
    discount_fixed: Optional[Decimal] = None
    min_order: Decimal = Decimal("0")
    max_uses: int = 100
    expires_at: Optional[datetime] = None
    is_active: bool = True

class CouponCreate(CouponBase):
    pass

class CouponOut(CouponBase):
    id: int
    used_count: int
    model_config = {"from_attributes": True}


# ─────────────────────────── ProductImage ────────────────────

class ProductImageOut(BaseModel):
    id: int
    url: str
    alt: Optional[str]
    is_primary: bool
    sort_order: int
    model_config = {"from_attributes": True}


# ─────────────────────────── Product ─────────────────────────

class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    specs: Optional[dict] = {}
    price: Decimal
    sale_price: Optional[Decimal] = None
    stock: int = 0
    sku: Optional[str] = None
    weight_kg: Optional[Decimal] = None
    is_active: bool = True
    is_featured: bool = False
    brand_id: Optional[int] = None
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    specs: Optional[dict] = None
    price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

class ProductOut(ProductBase):
    id: int
    rating: Decimal
    reviews_count: int
    created_at: datetime
    brand: Optional[BrandOut] = None
    category: Optional[CategoryOut] = None
    images: List[ProductImageOut] = []
    tags: List[TagOut] = []
    model_config = {"from_attributes": True}

class ProductShort(BaseModel):
    id: int
    name: str
    slug: str
    price: Decimal
    sale_price: Optional[Decimal]
    rating: Decimal
    reviews_count: int
    is_featured: bool
    brand: Optional[BrandOut] = None
    images: List[ProductImageOut] = []
    model_config = {"from_attributes": True}


# ─────────────────────────── User ────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: Optional[str]
    phone: Optional[str]
    role: str
    is_verified: bool
    avatar_url: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


# ─────────────────────────── Address ─────────────────────────

class AddressBase(BaseModel):
    label: str = "Home"
    country: str = "Ukraine"
    city: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressOut(AddressBase):
    id: int
    model_config = {"from_attributes": True}


# ─────────────────────────── Auth ────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str


# ─────────────────────────── Review ──────────────────────────

class ReviewCreate(BaseModel):
    rating: int
    title: Optional[str] = None
    body: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def check_rating(cls, v):
        if not (1 <= v <= 5):
            raise ValueError("Rating must be between 1 and 5")
        return v

class ReviewOut(BaseModel):
    id: int
    product_id: int
    user_id: uuid.UUID
    rating: int
    title: Optional[str]
    body: Optional[str]
    is_verified: bool
    helpful: int
    created_at: datetime
    user: Optional[UserOut] = None
    model_config = {"from_attributes": True}


# ─────────────────────────── Cart ────────────────────────────

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    added_at: datetime
    product: Optional[ProductShort] = None
    model_config = {"from_attributes": True}

class CartOut(BaseModel):
    id: int
    items: List[CartItemOut] = []
    total: Decimal = Decimal("0")
    model_config = {"from_attributes": True}


# ─────────────────────────── Order ───────────────────────────

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    address_id: int
    coupon_code: Optional[str] = None
    payment_method: str = "card"
    notes: Optional[str] = None
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    product: Optional[ProductShort] = None
    model_config = {"from_attributes": True}

class OrderOut(BaseModel):
    id: int
    status: str
    total: Decimal
    discount: Decimal
    shipping_cost: Decimal
    payment_method: str
    payment_status: str
    tracking_number: Optional[str]
    notes: Optional[str]
    created_at: datetime
    items: List[OrderItemOut] = []
    address: Optional[AddressOut] = None
    model_config = {"from_attributes": True}

class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def check_status(cls, v):
        allowed = {"pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded"}
        if v not in allowed:
            raise ValueError(f"Status must be one of: {allowed}")
        return v


# ─────────────────────────── Pagination ──────────────────────

class PaginatedProducts(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[ProductShort]
