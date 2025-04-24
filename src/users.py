from flask import request, jsonify
from src import crud, schemas, models
from src.database import SessionLocal

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def route_user(app):
    @app.route("/users/", methods=["GET"])
    def get_users():
        return jsonify({"message": "Users endpoint (not implemented yet)"})

    @app.route("/users/<int:user_id>/favorites/", methods=["POST"])
    def add_favorite_route(user_id):
        db = get_db_session()
        try:
            data = schemas.validate_favorite(request.get_json())
            data["user_id"] = user_id
            favorite = crud.add_favorite(db, data["user_id"], data["product_id"])
            return jsonify({
                "id": favorite.id,
                "user_id": favorite.user_id,
                "product_id": favorite.product_id
            }), 201 if not isinstance(favorite, models.Favorite) else 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/users/<int:user_id>/favorites/<int:product_id>", methods=["DELETE"])
    def remove_favorite_route(user_id, product_id):
        db = get_db_session()
        favorite = crud.remove_favorite(db, user_id, product_id)
        if not favorite:
            return jsonify({"error": "Favorite not found"}), 404
        return jsonify({"message": "Favorite removed"})

    @app.route("/users/<int:user_id>/favorites/", methods=["GET"])
    def get_favorites_route(user_id):
        db = get_db_session()
        products = crud.get_favorites(db, user_id)
        return jsonify([{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "category": p.category,
            "average_rating": p.average_rating
        } for p in products])
