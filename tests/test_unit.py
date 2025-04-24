import json
from src import models, schemas
import pytest
from datetime import datetime
from src.routes_init import init_routes
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    init_routes(app)
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(mocker):
    session = mocker.MagicMock()
    # Мокаем методы базы данных, которые ты используешь в функции
    session.add = mocker.MagicMock()
    session.commit = mocker.MagicMock()
    session.refresh = mocker.MagicMock()
    return session


@pytest.fixture(autouse=True)
def mock_get_db_session(mocker, db_session):
    # Перехватываем вызов get_db_session и возвращаем саму сессию, а не итератор
    mocker.patch("src.orders.get_db_session", return_value=db_session)

def test_create_product_success(client, mocker):
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 10.99,
        "category": "Test Category"
    }

    mock_product = models.Product(
        id=1,
        name=product_data["name"],
        description=product_data["description"],
        price=product_data["price"],
        category=product_data["category"]
    )

    mocker.patch("src.schemas.validate_product", return_value=product_data)
    mocker.patch("src.products.create_product", return_value=mock_product)

    response = client.post("/products/", data=json.dumps(product_data), content_type="application/json")

    assert response.status_code == 201
    assert response.json == {
        "id": 1,
        "name": "Test Product",
        "description": "A test product",
        "price": 10.99,
        "category": "Test Category"
    }



def test_create_product_invalid_data(client, mocker):
    # Подготовка данных
    invalid_data = {"name": ""}  # Некорректные данные
    mocker.patch("src.schemas.validate_product", side_effect=ValueError("Invalid product data"))

    # Выполняем запрос
    response = client.post("/products/", data=json.dumps(invalid_data), content_type="application/json")

    # Проверяем результат
    assert response.status_code == 400
    assert response.json == {"error": "Invalid product data"}

# Тесты для маршрута получения списка продуктов
def test_read_products_success(client, db_session, mocker):
    # Подготовка данных
    mock_products = [
        models.Product(id=1, name="Product 1", description="Desc 1", price=10.0, category="Cat 1", average_rating=4.5),
        models.Product(id=2, name="Product 2", description="Desc 2", price=20.0, category="Cat 2", average_rating=3.0)
    ]
    mocker.patch("src.crud.get_products", return_value=mock_products)

    # Выполняем запрос
    response = client.get("/products/?skip=0&limit=10&category=Cat 1")

    # Проверяем результат
    assert response.status_code == 200
    assert response.json == [
        {"id": 1, "name": "Product 1", "description": "Desc 1", "price": 10.0, "category": "Cat 1", "average_rating": 4.5},
        {"id": 2, "name": "Product 2", "description": "Desc 2", "price": 20.0, "category": "Cat 2", "average_rating": 3.0}
    ]

# Тесты для маршрута получения одного продукта
def test_read_product_success(client, db_session, mocker):
    # Подготовка данных
    mock_product = models.Product(id=1, name="Product 1", description="Desc 1", price=10.0, category="Cat 1", average_rating=4.5)
    mocker.patch("src.crud.get_product", return_value=mock_product)

    # Выполняем запрос
    response = client.get("/products/1")

    # Проверяем результат
    assert response.status_code == 200
    assert response.json == {
        "id": 1, "name": "Product 1", "description": "Desc 1", "price": 10.0, "category": "Cat 1", "average_rating": 4.5
    }

def test_read_product_not_found(client, db_session, mocker):
    mocker.patch("src.crud.get_product", return_value=None)

    # Выполняем запрос
    response = client.get("/products/999")

    # Проверяем результат
    assert response.status_code == 404
    assert response.json == {"error": "Product not found"}


def test_update_product_success(client, mocker):
    # Подготовка данных
    product_data = {"name": "Updated Product", "price": 15.99}
    mock_product = models.Product(
        id=1,
        name="Updated Product",
        description="Desc",
        price=15.99,
        category="Cat"
    )

    mocker.patch("src.schemas.validate_product", return_value=product_data)
    mocker.patch("src.products.update_product", return_value=mock_product)

    response = client.put("/products/1", data=json.dumps(product_data), content_type="application/json")
    assert response.status_code == 200
    assert response.json == {
        "id": 1,
        "name": "Updated Product",
        "description": "Desc",
        "price": 15.99,
        "category": "Cat"
    }


# Тесты для маршрута удаления продукта
def test_delete_product_success(client, db_session, mocker):
    mock_product = models.Product(id=1, name="Product 1")
    mocker.patch("src.products.delete_product", return_value=mock_product)

    response = client.delete("/products/1")

    assert response.status_code == 200
    assert response.json == {"message": "Product deleted"}

def test_delete_product_not_found(client, db_session, mocker):
    mocker.patch("src.products.delete_product", return_value=None)

    response = client.delete("/products/999")

    assert response.status_code == 404
    assert response.json == {"error": "Product not found"}


def test_create_order_success(client, mocker, db_session):
    # Данные для заказа
    order_data = {
        "user_id": 1,
        "items": [
            {"product_id": 1, "quantity": 2, "price": 20.0},
            {"product_id": 2, "quantity": 1, "price": 15.5}
        ]
    }

    # Мокаем создание заказа
    mock_order = models.Order(
        id=1,
        user_id=order_data["user_id"],
        status="new",
        order_date=datetime.now()
    )

    # Мокаем добавление заказа и товаров
    mocker.patch("src.orders.create_order", return_value=mock_order)

    # Выполняем запрос
    response = client.post("/orders/", data=json.dumps(order_data), content_type="application/json")

    assert response.status_code == 201
    assert response.json == {
        "id": 1,
        "user_id": 1,
        "status": "new",
        "order_date": mock_order.order_date.isoformat(),
        "items": [
            {"product_id": 1, "quantity": 2, "price": 20.0},
            {"product_id": 2, "quantity": 1, "price": 15.5}
        ]
    }
