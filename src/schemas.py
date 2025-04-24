def validate_product(data):
    required_fields = ["name", "price", "category"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Field '{field}' is required")
    if not isinstance(data["price"], (int, float)) or data["price"] < 0:
        raise ValueError("Price must be a positive number")
    return data

def validate_order(data):
    if "user_id" not in data or not isinstance(data["user_id"], int):
        raise ValueError("Valid 'user_id' is required")
    if "items" not in data or not isinstance(data["items"], list) or not data["items"]:
        raise ValueError("Order must contain at least one item")
    for item in data["items"]:
        if not all(k in item for k in ["product_id", "quantity", "price"]):
            raise ValueError("Each item must have 'product_id', 'quantity', and 'price'")
    return data


def validate_review(data):
    required_fields = ["user_id", "product_id", "rating"]
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f"Field '{field}' is required")

    if not isinstance(data["rating"], int) or not (1 <= data["rating"] <= 5):
        raise ValueError("Rating must be an integer between 1 and 5")

    return data


def validate_favorite(data):
    required_fields = ["user_id", "product_id"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Field '{field}' is required")
    return data
