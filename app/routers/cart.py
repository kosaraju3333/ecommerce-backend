from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.utils.dependencies import get_current_user


router = APIRouter(
    prefix="/api/cart",
    tags=["Cart"]
)


@router.post("/items")
def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # 1. Check whether product exists
    product = (
        db.query(Product)
        .filter(Product.id == item.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # 2. Check whether product is active
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not available"
        )

    # 3. Check stock
    if product.stock_quantity < item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )

    # 4. Find customer's cart
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    # 5. Create cart if customer doesn't have one
    if not cart:
        cart = Cart(user_id=current_user.id)

        db.add(cart)
        db.commit()
        db.refresh(cart)

    # 6. Check whether product already exists in cart
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item.product_id
        )
        .first()
    )

    if cart_item:

        new_quantity = cart_item.quantity + item.quantity

        if product.stock_quantity < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )

        cart_item.quantity = new_quantity

    else:

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )

        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Product added to cart",
        "cart_item_id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity
    }

@router.get("/")
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart:
        return {
            "items": [],
            "total": 0
        }

    items = []

    total = 0

    for cart_item in cart.items:

        product = cart_item.product

        subtotal = product.price * cart_item.quantity

        total += subtotal

        items.append({
            "cart_item_id": cart_item.id,
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url,
            "quantity": cart_item.quantity,
            "subtotal": subtotal
        })

    return {
        "cart_id": cart.id,
        "items": items,
        "total": total
    }

@router.put("/items/{cart_item_id}")
def update_cart_item(
    cart_item_id: int,
    item: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Find cart belonging to logged-in user
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    # Find item only inside this user's cart
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    # Get associated product
    product = (
        db.query(Product)
        .filter(Product.id == cart_item.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Check stock
    if item.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )

    # Update quantity
    cart_item.quantity = item.quantity

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Cart item updated",
        "cart_item_id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity
    }

@router.delete("/items/{cart_item_id}")
def delete_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Find logged-in user's cart
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    # Find item only inside this user's cart
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Product removed from cart"
    }