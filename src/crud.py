from sqlalchemy.orm import Session
from src import models


def create_product(db: Session, product: dict):
    db_product = models.Product(**product)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 10, category: str = None):
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    return query.offset(skip).limit(limit).all()

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product(db: Session, product_id: int, product: dict):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    for key, value in product.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

def create_order(db: Session, order: dict):
    db_order = models.Order(user_id=order["user_id"])
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order["items"]:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"]
        )
        db.add(db_item)

    db.commit()
    return db_order


def create_review(db: Session, review: dict):
    user = db.query(models.User).filter(models.User.id == review["user_id"]).first()
    if not user:
        raise ValueError(f"User with id {review['user_id']} not found.")

    product = db.query(models.Product).filter(models.Product.id == review["product_id"]).first()
    if not product:
        raise ValueError(f"Product with id {review['product_id']} not found.")

    db_review = models.Review(**review)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    update_product_rating(db, review["product_id"])
    return db_review


def get_reviews(db: Session, product_id: int, sort_by: str = "created_at", order: str = "desc"):
    query = db.query(models.Review).filter(models.Review.product_id == product_id)
    if sort_by == "rating":
        query = query.order_by(models.Review.rating.desc() if order == "desc" else models.Review.rating.asc())
    else:
        query = query.order_by(models.Review.created_at.desc() if order == "desc" else models.Review.created_at.asc())
    return query.all()

def update_product_rating(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        print(f"[ERROR] Product with id {product_id} not found.")
        return
    reviews = db.query(models.Review).filter(models.Review.product_id == product_id).all()
    if reviews:
        average_rating = sum(r.rating for r in reviews) / len(reviews)
        product.average_rating = average_rating
        db.commit()
        print(f"[DEBUG] Updated average rating for product {product_id}: {average_rating}")
    else:
        print(f"[INFO] No reviews found for product {product_id}, skipping rating update.")


def add_favorite(db: Session, user_id: int, product_id: int):
    existing = db.query(models.Favorite).filter_by(user_id=user_id, product_id=product_id).first()
    if not existing:
        db_favorite = models.Favorite(user_id=user_id, product_id=product_id)
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        return db_favorite
    return existing

def remove_favorite(db: Session, user_id: int, product_id: int):
    favorite = db.query(models.Favorite).filter_by(user_id=user_id, product_id=product_id).first()
    if favorite:
        db.delete(favorite)
        db.commit()
    return favorite

def get_favorites(db: Session, user_id: int):
    return db.query(models.Product).join(models.Favorite).filter(models.Favorite.user_id == user_id).all()
