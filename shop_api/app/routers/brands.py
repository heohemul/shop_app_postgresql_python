from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import require_admin

router = APIRouter()


@router.get("", response_model=List[schemas.BrandOut])
def list_brands(db: Session = Depends(get_db)):
    """List all brands sorted by name."""
    return db.query(models.Brand).order_by(models.Brand.name).all()


@router.get("/{brand_id}", response_model=schemas.BrandOut)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    """Get a brand by ID."""
    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.post("", response_model=schemas.BrandOut, status_code=201)
def create_brand(
    data: schemas.BrandCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Create a new brand (admin only)."""
    brand = models.Brand(**data.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand
