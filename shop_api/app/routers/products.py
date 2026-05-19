from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, require_admin

router = APIRouter()


@router.get("", response_model=schemas.PaginatedProducts)
def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    featured: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Product catalog with filtering and pagination."""
    q = db.query(models.Product).filter(models.Product.is_active == True)

    if category_id:
        q = q.filter(models.Product.category_id == category_id)
    if brand_id:
        q = q.filter(models.Product.brand_id == brand_id)
    if min_price is not None:
        q = q.filter(models.Product.price >= min_price)
    if max_price is not None:
        q = q.filter(models.Product.price <= max_price)
    if featured is not None:
        q = q.filter(models.Product.is_featured == featured)
    if search:
        q = q.filter(models.Product.name.ilike(f"%{search}%"))

    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()

    return {"total": total, "page": page, "per_page": per_page, "items": items}


@router.get("/featured", response_model=List[schemas.ProductShort])
def featured_products(db: Session = Depends(get_db)):
    """Get featured products."""
    return db.query(models.Product).filter(
        models.Product.is_featured == True,
        models.Product.is_active == True,
    ).all()


@router.get("/{slug}", response_model=schemas.ProductOut)
def get_product(slug: str, db: Session = Depends(get_db)):
    """Get product details by slug."""
    product = db.query(models.Product).filter(models.Product.slug == slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=schemas.ProductOut, status_code=201)
def create_product(
    data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    """Create a product (admin/moderator only)."""
    if db.query(models.Product).filter(models.Product.slug == data.slug).first():
        raise HTTPException(status_code=400, detail="Slug is already taken")
    product = models.Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    data: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    """Update a product (admin/moderator only)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, val in data.model_dump(exclude_none=True).items():
        setattr(product, key, val)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    """Soft delete a product — sets is_active=False (admin/moderator only)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
