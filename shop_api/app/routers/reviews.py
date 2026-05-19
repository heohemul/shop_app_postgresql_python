from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter()


@router.get("/product/{product_id}", response_model=List[schemas.ReviewOut])
def product_reviews(product_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a specific product."""
    return db.query(models.Review).filter(
        models.Review.product_id == product_id
    ).order_by(models.Review.helpful.desc()).all()


@router.post("/product/{product_id}", response_model=schemas.ReviewOut, status_code=201)
def add_review(
    product_id: int,
    data: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Leave a review (one review per user per product)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(models.Review).filter(
        models.Review.product_id == product_id,
        models.Review.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")

    # Check if user has a verified (delivered) purchase of this product
    has_order = db.query(models.OrderItem).join(models.Order).filter(
        models.OrderItem.product_id == product_id,
        models.Order.user_id == current_user.id,
        models.Order.status == "delivered",
    ).first()

    review = models.Review(
        product_id=product_id,
        user_id=current_user.id,
        rating=data.rating,
        title=data.title,
        body=data.body,
        is_verified=bool(has_order),
    )
    db.add(review)
    db.flush()

    # Recalculate product rating
    stats = db.query(
        func.avg(models.Review.rating).label("avg"),
        func.count(models.Review.id).label("cnt"),
    ).filter(models.Review.product_id == product_id).one()

    product.rating = round(float(stats.avg or 0), 2)
    product.reviews_count = stats.cnt

    db.commit()
    db.refresh(review)
    return review


@router.post("/{review_id}/helpful", status_code=200)
def mark_helpful(review_id: int, db: Session = Depends(get_db)):
    """Mark a review as helpful."""
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.helpful += 1
    db.commit()
    return {"helpful": review.helpful}


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a review (owner or admin/moderator only)."""
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != current_user.id and current_user.role not in ("admin", "moderator"):
        raise HTTPException(status_code=403, detail="Access denied")
    db.delete(review)
    db.commit()
