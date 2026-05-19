from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user, require_admin

router = APIRouter()


@router.get("", response_model=List[schemas.OrderOut])
def my_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get current user's orders."""
    return db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).order_by(models.Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get order details."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and current_user.role not in ("admin", "moderator"):
        raise HTTPException(status_code=403, detail="Access denied")
    return order


@router.post("", response_model=schemas.OrderOut, status_code=201)
def create_order(
    data: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new order."""
    # Validate delivery address
    address = db.query(models.Address).filter(
        models.Address.id == data.address_id,
        models.Address.user_id == current_user.id,
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    # Validate coupon
    coupon = None
    discount = Decimal("0")
    if data.coupon_code:
        coupon = db.query(models.Coupon).filter(
            models.Coupon.code == data.coupon_code,
            models.Coupon.is_active == True,
        ).first()
        if not coupon:
            raise HTTPException(status_code=400, detail="Coupon is invalid or expired")

    # Calculate order total
    total = Decimal("0")
    order_items_data = []
    for item in data.items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id,
            models.Product.is_active == True,
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for: {product.name}")

        unit_price = product.sale_price or product.price
        total += unit_price * item.quantity
        order_items_data.append((product, item.quantity, unit_price))

    # Apply coupon discount
    if coupon:
        if total < (coupon.min_order or 0):
            raise HTTPException(status_code=400, detail=f"Minimum order amount for this coupon: {coupon.min_order}")
        if coupon.discount_pct:
            discount = total * coupon.discount_pct / 100
        elif coupon.discount_fixed:
            discount = min(coupon.discount_fixed, total)

    # Free shipping on orders over 2000
    shipping = Decimal("99") if total - discount < 2000 else Decimal("0")
    final_total = total - discount + shipping

    # Create the order
    order = models.Order(
        user_id=current_user.id,
        address_id=address.id,
        coupon_id=coupon.id if coupon else None,
        total=final_total,
        discount=discount,
        shipping_cost=shipping,
        payment_method=data.payment_method,
        notes=data.notes,
    )
    db.add(order)
    db.flush()

    for product, quantity, unit_price in order_items_data:
        db.add(models.OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
        ))
        # Deduct stock
        product.stock -= quantity

    if coupon:
        coupon.used_count += 1

    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=schemas.OrderOut)
def update_order_status(
    order_id: int,
    data: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    """Update order status (admin/moderator only)."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = data.status
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/cancel", response_model=schemas.OrderOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Cancel an order (only if not yet shipped)."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if order.status in ("shipped", "delivered"):
        raise HTTPException(status_code=400, detail="Cannot cancel an order that has already been shipped")

    order.status = "cancelled"

    # Restore stock for each item
    for item in order.items:
        item.product.stock += item.quantity

    db.commit()
    db.refresh(order)
    return order
