import pytest
from flask import Flask, g
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from src.models import Base, User
from src.routes_init import init_routes
from src.database import SessionLocal


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def postgres_engine():
    try:
        with PostgresContainer("postgres:16") as postgres:
            connection_url = postgres.get_connection_url()
            engine = create_engine(connection_url)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                print("Подключение к базе успешно!")
            yield engine
            engine.dispose()
    except Exception as e:
        print(f"Ошибка запуска контейнера Postgres: {e}")
        raise

@pytest.fixture(scope="function")
def db_session(postgres_engine):
    Base.metadata.create_all(postgres_engine)
    Session = sessionmaker(bind=postgres_engine, expire_on_commit=False)
    session = Session()
    try:
        yield session
        session.commit()
        print("Сессия успешно закоммичена")
    except Exception as e:
        print(f"Ошибка в сессии: {e}")
        session.rollback()
        raise
    finally:
        session.close()
    Base.metadata.drop_all(postgres_engine)

@pytest.fixture
def app_with_db(db_session):
    app = Flask(__name__)
    init_routes(app)

    @app.before_request
    def set_test_db_session():
        g.db_session = db_session

    return app

@pytest.fixture
def test_app(app_with_db):
    with app_with_db.test_client() as client:
        yield client


def test_create_product(test_app, db_session):
    response = test_app.post(
        "/products/",
        json={
            "name": "Test Product",
            "price": 10.0,
            "category": "Test",
            "description": "Test Product"
        }
    )
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.get_data(as_text=True)}")
    assert response.status_code == 201, f"Ожидали 201, получили {response.status_code}"
    data = response.get_json() or {}
    assert "error" not in data, f"Ошибка в ответе: {data.get('error', 'Нет данных об ошибке')}"
    assert data["name"] == "Test Product"
    assert data["price"] == 10.0
    assert data["category"] == "Test"
    assert "id" in data

# Тест получения списка продуктов
def test_get_products(test_app, db_session):
    # Создаем продукт для теста
    response = test_app.post(
        "/products/",
        json={
            "name": "Test Product",
            "price": 10.0,
            "category": "Test",
            "description": "Test Product"
        }
    )
    assert response.status_code == 201

    response = test_app.get("/products/?skip=0&limit=10&category=Test")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    product = data[0]
    assert product["name"] == "Test Product"
    assert product["price"] == 10.0
    assert product["category"] == "Test"
    assert product["average_rating"] == 0.0
    assert "id" in product

def test_get_product(test_app, db_session):
    # Создаем продукт
    create_response = test_app.post(
        "/products/",
        json={
            "name": "Single Product",
            "price": 15.0,
            "category": "Test",
            "description": "Single Test Product"
        }
    )
    assert create_response.status_code == 201
    product_id = create_response.get_json()["id"]

    # Получаем продукт
    response = test_app.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Single Product"
    assert data["price"] == 15.0
    assert data["category"] == "Test"
    assert data["description"] == "Single Test Product"
    assert data["average_rating"] == 0.0
    assert data["id"] == product_id

def test_update_product(test_app, db_session):
    # Создаем продукт
    create_response = test_app.post(
        "/products/",
        json={
            "name": "Old Product",
            "price": 20.0,
            "category": "Test",
            "description": "Old Description"
        }
    )
    assert create_response.status_code == 201
    product_id = create_response.get_json()["id"]

    # Обновляем продукт
    response = test_app.put(
        f"/products/{product_id}",
        json={
            "name": "New Product",
            "price": 25.0,
            "category": "Test",
            "description": "New Description"
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "New Product"
    assert data["price"] == 25.0
    assert data["category"] == "Test"
    assert data["description"] == "New Description"
    assert data["id"] == product_id

def test_delete_product(test_app, db_session):
    # Создаем продукт
    create_response = test_app.post(
        "/products/",
        json={
            "name": "Delete Product",
            "price": 30.0,
            "category": "Test",
            "description": "To Delete"
        }
    )
    assert create_response.status_code == 201
    product_id = create_response.get_json()["id"]

    # Удаляем продукт
    response = test_app.delete(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Product deleted"

    check_response = test_app.get(f"/products/{product_id}")
    assert check_response.status_code == 404
    assert "error" in check_response.get_json()
    
def test_create_review(test_app, db_session):
    # Создаем продукт
    create_product_response = test_app.post(
        "/products/",
        json={
            "name": "Review Product",
            "price": 40.0,
            "category": "Test",
            "description": "For Review"
        }
    )
    assert create_product_response.status_code == 201
    product_id = create_product_response.get_json()["id"]

    # Создаем пользователя
    from src.models import User
    user = User(name="testuser", email="test@example.com")  # Уточни поля по модели User
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    # Создаем отзыв
    response = test_app.post(
        f"/products/{product_id}/reviews/",
        json={
            "user_id": user_id,  # Используем ID созданного пользователя
            "rating": 4,
            "comment": "Good product!",
            "product_id": product_id  # Требуется валидатором
        }
    )
    print(f"Статус создания отзыва: {response.status_code}")
    print(f"Ответ создания отзыва: {response.get_data(as_text=True)}")
    assert response.status_code == 201, f"Ожидали 201, получили {response.status_code}"
    data = response.get_json() or {}
    assert data["product_id"] == product_id
    assert data["rating"] == 4
    assert data["comment"] == "Good product!"
    assert "id" in data

    # Проверяем обновленный рейтинг
    product_response = test_app.get(f"/products/{product_id}")
    assert product_response.status_code == 200
    product_data = product_response.get_json()
    assert product_data["average_rating"] == 4.0

def test_get_reviews(test_app, db_session):
    # Создаем продукт
    create_product_response = test_app.post(
        "/products/",
        json={
            "name": "Reviews Product",
            "price": 50.0,
            "category": "Test",
            "description": "For Reviews"
        }
    )
    assert create_product_response.status_code == 201
    product_id = create_product_response.get_json()["id"]

    user = User(name="testuser", email="test@example.com")  # Уточни поля по своей модели
    db_session.add(user)
    db_session.commit()
    user_id = user.id

    # Добавляем отзыв
    review_response = test_app.post(
        f"/products/{product_id}/reviews/",
        json={
            "user_id": user_id,
            "rating": 5,
            "comment": "Great product!",
            "product_id": product_id
        }
    )
    assert review_response.status_code == 201, f"Ожидали 201, получили {review_response.status_code}"

    response = test_app.get(f"/products/{product_id}/reviews/?sort_by=rating&order=desc")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    review = data[0]
    assert review["rating"] == 5
    assert review["comment"] == "Great product!"
    assert review["user_id"] == user_id
    assert "id" in review
