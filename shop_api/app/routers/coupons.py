from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, require_admin

router = APIRouter()


@router.get("/validate/{code}")
def validate_coupon(code: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Validate a coupon before placing an order."""
    coupon = db.query(models.Coupon).filter(
        models.Coupon.code == code,
        models.Coupon.is_active == True,
    ).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found or inactive")
    if coupon.used_count >= coupon.max_uses:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    return {
        "code": coupon.code,
        "discount_pct": coupon.discount_pct,
        "discount_fixed": coupon.discount_fixed,
        "min_order": coupon.min_order,
        "expires_at": coupon.expires_at,
    }


@router.get("", response_model=List[schemas.CouponOut])
def list_coupons(db: Session = Depends(get_db), _=Depends(require_admin)):
    """List all coupons (admin only)."""
    return db.query(models.Coupon).all()


@router.post("", response_model=schemas.CouponOut, status_code=201)
def create_coupon(
    data: schemas.CouponCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Create a new coupon (admin only)."""
    coupon = models.Coupon(**data.model_dump())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


@router.delete("/{coupon_id}", status_code=204)
def deactivate_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Deactivate a coupon (admin only)."""
    coupon = db.query(models.Coupon).filter(models.Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    coupon.is_active = False
    db.commit()
