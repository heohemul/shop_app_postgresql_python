from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.auth import get_current_user

router = APIRouter()


def _get_or_create_cart(user: models.User, db: Session) -> models.Cart:
    cart = db.query(models.Cart).filter(models.Cart.user_id == user.id).first()
    if not cart:
        cart = models.Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _build_cart_out(cart: models.Cart) -> dict:
    total = sum(
        (item.product.sale_price or item.product.price) * item.quantity
        for item in cart.items
        if item.product
    )
    return {"id": cart.id, "items": cart.items, "total": total}


@router.get("", response_model=schemas.CartOut)
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """View current user's cart."""
    cart = _get_or_create_cart(current_user, db)
    return _build_cart_out(cart)


@router.post("/items", response_model=schemas.CartOut)
def add_item(
    data: schemas.CartItemAdd,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Add a product to the cart."""
    product = db.query(models.Product).filter(
        models.Product.id == data.product_id,
        models.Product.is_active == True,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    cart = _get_or_create_cart(current_user, db)

    existing = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.product_id == data.product_id,
    ).first()

    if existing:
        existing.quantity += data.quantity
    else:
        db.add(models.CartItem(
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity,
        ))

    db.commit()
    db.refresh(cart)
    return _build_cart_out(cart)


@router.patch("/items/{item_id}", response_model=schemas.CartOut)
def update_item(
    item_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update quantity of a cart item. Set to 0 to remove."""
    cart = _get_or_create_cart(current_user, db)
    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.cart_id == cart.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if quantity <= 0:
        db.delete(item)
    else:
        item.quantity = quantity

    db.commit()
    db.refresh(cart)
    return _build_cart_out(cart)


@router.delete("/items/{item_id}", status_code=204)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Remove an item from the cart."""
    cart = _get_or_create_cart(current_user, db)
    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.cart_id == cart.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()


@router.delete("", status_code=204)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Clear the entire cart."""
    cart = _get_or_create_cart(current_user, db)
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
    db.commit()
