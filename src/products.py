from flask import request, jsonify, g
from src import models, schemas, crud
from src.database import SessionLocal
from src.crud import create_product, update_product, delete_product

def get_db_session():
    db = getattr(g, 'db_session', None) or SessionLocal()
    try:
        yield db
    finally:
        if not hasattr(g, 'db_session'):  # Закрываем только если это не тестовая сессия
            db.close()

def route_product(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"error": str(e)}), 500

    @app.route("/products/", methods=["POST"])
    def create_product_route():
        db = next(get_db_session())
        try:
            data = schemas.validate_product(request.get_json())
            product = create_product(db, data)
            return jsonify({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category": product.category
            }), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/products/", methods=["GET"])
    def read_products_route():
        db = next(get_db_session())
        try:
            skip = int(request.args.get("skip", 0))
            limit = int(request.args.get("limit", 10))
            category = request.args.get("category")
            products = crud.get_products(db, skip=skip, limit=limit, category=category)
            return jsonify([{
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "category": p.category,
                "average_rating": p.average_rating
            } for p in products])
        except Exception as e:
            raise  # Передаем ошибку обработчику

    @app.route("/products/<int:product_id>", methods=["GET"])
    def read_product_route(product_id):
        db = next(get_db_session())
        try:
            product = crud.get_product(db, product_id)
            if not product:
                return jsonify({"error": "Product not found"}), 404
            return jsonify({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category": product.category,
                "average_rating": product.average_rating
            })
        except Exception as e:
            raise

    @app.route("/products/<int:product_id>", methods=["PUT"])
    def update_product_route(product_id):
        db = next(get_db_session())
        try:
            data = schemas.validate_product(request.get_json())
            product = update_product(db, product_id, data)
            if not product:
                return jsonify({"error": "Product not found"}), 404
            return jsonify({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category": product.category
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/products/<int:product_id>", methods=["DELETE"])
    def delete_product_route(product_id):
        db = next(get_db_session())
        try:
            product = delete_product(db, product_id)
            if not product:
                return jsonify({"error": "Product not found"}), 404
            return jsonify({"message": "Product deleted"})
        except Exception as e:
            raise

    @app.route("/products/<int:product_id>/reviews/", methods=["POST"])
    def create_review_route(product_id):
        db = next(get_db_session())
        try:
            data = schemas.validate_review(request.get_json())
            data["product_id"] = product_id
            review = crud.create_review(db, data)
            # Пересчитываем средний рейтинг
            product = db.query(models.Product).filter(models.Product.id == product_id).first()
            reviews = db.query(models.Review).filter(models.Review.product_id == product_id).all()
            product.average_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0.0
            db.commit()
            return jsonify({
                "id": review.id,
                "user_id": review.user_id,
                "product_id": review.product_id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat()
            }), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/products/<int:product_id>/reviews/", methods=["GET"])
    def get_reviews_route(product_id):
        db = next(get_db_session())
        try:
            sort_by = request.args.get("sort_by", "created_at")
            order = request.args.get("order", "desc")
            reviews = crud.get_reviews(db, product_id, sort_by=sort_by, order=order)
            return jsonify([{
                "id": r.id,
                "user_id": r.user_id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat()
            } for r in reviews])
        except Exception as e:
            raise