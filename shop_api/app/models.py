import uuid
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean,
    ForeignKey, SmallInteger, TIMESTAMP, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(Text, nullable=False, unique=True)
    country    = Column(Text)
    website    = Column(Text)
    logo_url   = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    products   = relationship("Product", back_populates="brand")


class Category(Base):
    __tablename__ = "categories"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(Text, nullable=False)
    slug       = Column(Text, nullable=False, unique=True)
    parent_id  = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    parent     = relationship("Category", remote_side="Category.id", back_populates="children")
    children   = relationship("Category", back_populates="parent")
    products   = relationship("Product", back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False, unique=True)


class Coupon(Base):
    __tablename__ = "coupons"

    id             = Column(Integer, primary_key=True, index=True)
    code           = Column(Text, nullable=False, unique=True)
    discount_pct   = Column(Numeric(5, 2))
    discount_fixed = Column(Numeric(10, 2))
    min_order      = Column(Numeric(10, 2), default=0)
    max_uses       = Column(Integer, default=100)
    used_count     = Column(Integer, default=0)
    expires_at     = Column(TIMESTAMP(timezone=True))
    is_active      = Column(Boolean, default=True)

    orders         = relationship("Order", back_populates="coupon")


class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email         = Column(Text, nullable=False, unique=True)
    username      = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    full_name     = Column(Text)
    phone         = Column(Text)
    role          = Column(Text, default="customer")  # customer | admin | moderator
    is_verified   = Column(Boolean, default=False)
    avatar_url    = Column(Text)
    created_at    = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_login    = Column(TIMESTAMP(timezone=True))

    addresses     = relationship("Address", back_populates="user", cascade="all, delete")
    orders        = relationship("Order", back_populates="user")
    reviews       = relationship("Review", back_populates="user")
    carts         = relationship("Cart", back_populates="user", cascade="all, delete")


class Address(Base):
    __tablename__ = "addresses"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    label       = Column(Text, default="Home")
    country     = Column(Text, default="Ukraine")
    city        = Column(Text)
    street      = Column(Text)
    building    = Column(Text)
    apartment   = Column(Text)
    postal_code = Column(Text)
    is_default  = Column(Boolean, default=False)

    user        = relationship("User", back_populates="addresses")
    orders      = relationship("Order", back_populates="address")


class Product(Base):
    __tablename__ = "products"

    id            = Column(Integer, primary_key=True, index=True)
    brand_id      = Column(Integer, ForeignKey("brands.id"))
    category_id   = Column(Integer, ForeignKey("categories.id"))
    name          = Column(Text, nullable=False)
    slug          = Column(Text, nullable=False, unique=True)
    description   = Column(Text)
    specs         = Column(JSONB, default={})
    price         = Column(Numeric(10, 2), nullable=False)
    sale_price    = Column(Numeric(10, 2))
    stock         = Column(Integer, default=0)
    sku           = Column(Text, unique=True)
    weight_kg     = Column(Numeric(6, 3))
    is_active     = Column(Boolean, default=True)
    is_featured   = Column(Boolean, default=False)
    rating        = Column(Numeric(3, 2), default=0)
    reviews_count = Column(Integer, default=0)
    created_at    = Column(TIMESTAMP(timezone=True), server_default=func.now())

    brand         = relationship("Brand", back_populates="products")
    category      = relationship("Category", back_populates="products")
    images        = relationship("ProductImage", back_populates="product", cascade="all, delete")
    reviews       = relationship("Review", back_populates="product", cascade="all, delete")
    order_items   = relationship("OrderItem", back_populates="product")
    cart_items    = relationship("CartItem", back_populates="product")
    tags          = relationship("Tag", secondary="product_tags")


class ProductImage(Base):
    __tablename__ = "product_images"

    id         = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    url        = Column(Text, nullable=False)
    alt        = Column(Text)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    product    = relationship("Product", back_populates="images")


class ProductTag(Base):
    __tablename__ = "product_tags"

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    tag_id     = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Cart(Base):
    __tablename__ = "carts"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    session_id = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user       = relationship("User", back_populates="carts")
    items      = relationship("CartItem", back_populates="cart", cascade="all, delete")


class CartItem(Base):
    __tablename__ = "cart_items"

    id         = Column(Integer, primary_key=True, index=True)
    cart_id    = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity   = Column(Integer, default=1)
    added_at   = Column(TIMESTAMP(timezone=True), server_default=func.now())

    cart       = relationship("Cart", back_populates="items")
    product    = relationship("Product", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    address_id      = Column(Integer, ForeignKey("addresses.id"))
    coupon_id       = Column(Integer, ForeignKey("coupons.id"))
    status          = Column(Text, default="pending")
    total           = Column(Numeric(10, 2), nullable=False)
    discount        = Column(Numeric(10, 2), default=0)
    shipping_cost   = Column(Numeric(10, 2), default=0)
    payment_method  = Column(Text, default="card")
    payment_status  = Column(Text, default="unpaid")
    tracking_number = Column(Text)
    notes           = Column(Text)
    created_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user            = relationship("User", back_populates="orders")
    address         = relationship("Address", back_populates="orders")
    coupon          = relationship("Coupon", back_populates="orders")
    items           = relationship("OrderItem", back_populates="order", cascade="all, delete")


class OrderItem(Base):
    __tablename__ = "order_items"

    id          = Column(Integer, primary_key=True, index=True)
    order_id    = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id  = Column(Integer, ForeignKey("products.id"))
    quantity    = Column(Integer, nullable=False)
    unit_price  = Column(Numeric(10, 2), nullable=False)

    order       = relationship("Order", back_populates="items")
    product     = relationship("Product", back_populates="order_items")

    @property
    def total_price(self):
        return self.quantity * self.unit_price


class Review(Base):
    __tablename__ = "reviews"

    id          = Column(Integer, primary_key=True, index=True)
    product_id  = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rating      = Column(SmallInteger)
    title       = Column(Text)
    body        = Column(Text)
    is_verified = Column(Boolean, default=False)
    helpful     = Column(Integer, default=0)
    created_at  = Column(TIMESTAMP(timezone=True), server_default=func.now())

    product     = relationship("Product", back_populates="reviews")
    user        = relationship("User", back_populates="reviews")
