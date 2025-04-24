from flask import request, jsonify
from src import database, models, schemas
from src.crud import create_order
from src.database import SessionLocal


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def route_order(app):
    @app.route("/orders/", methods=["POST"])
    def create_order_route():
        db = get_db_session()
        try:
            data = schemas.validate_order(request.get_json())
            order = create_order(db, data)
            return jsonify({
                "id": order.id,
                "user_id": order.user_id,
                "order_date": order.order_date.isoformat(),
                "status": order.status,
                "items": data["items"]
            }), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400