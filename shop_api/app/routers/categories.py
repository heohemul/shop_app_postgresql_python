from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import require_admin

router = APIRouter()


@router.get("", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """Get category tree (root categories with their children)."""
    return db.query(models.Category).filter(models.Category.parent_id == None).all()


@router.get("/{slug}", response_model=schemas.CategoryOut)
def get_category(slug: str, db: Session = Depends(get_db)):
    """Get a category by slug."""
    cat = db.query(models.Category).filter(models.Category.slug == slug).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.post("", response_model=schemas.CategoryOut, status_code=201)
def create_category(
    data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Create a new category (admin only)."""
    cat = models.Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat
