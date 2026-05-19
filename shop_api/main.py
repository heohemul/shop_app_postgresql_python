from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import products, categories, brands, users, orders, reviews, cart, coupons
from app.database import engine
from app import models

app = FastAPI(
    title="Electronics Shop API",
    description="REST API for an electronics store",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router,    prefix="/api/products",    tags=["Products"])
app.include_router(categories.router,  prefix="/api/categories",  tags=["Categories"])
app.include_router(brands.router,      prefix="/api/brands",      tags=["Brands"])
app.include_router(users.router,       prefix="/api/users",       tags=["Users"])
app.include_router(orders.router,      prefix="/api/orders",      tags=["Orders"])
app.include_router(reviews.router,     prefix="/api/reviews",     tags=["Reviews"])
app.include_router(cart.router,        prefix="/api/cart",        tags=["Cart"])
app.include_router(coupons.router,     prefix="/api/coupons",     tags=["Coupons"])


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Electronics Shop API is running ✓"}
