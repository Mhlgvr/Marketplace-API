from src.products import route_product
from src.users import route_user
from src.orders import route_order

def init_routes(app):
    route_product(app)
    route_user(app)
    route_order(app)
