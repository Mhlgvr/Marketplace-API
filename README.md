# Marketplace API
  
Проект разработан командой из трех человек:  
  
- Разработчик 1 - Михаил Гаврилов _(@m.gavrilov)_  
  
- Разработчик 2 - Константин Попов _(@k.popov)_  
  
- Разработчик 3 - Василий Белов _(@v.belov)_  
  
---
Marketplace API — это RESTful веб-приложение, разработанное на Flask, для управления товарами и заказами в маркетплейсе. Приложение использует PostgreSQL для хранения данных и предоставляет интерактивную документацию API через Swagger UI.

## Возможности приложения

1. **Управление товарами**:
   - Создание нового товара (`POST /products/`).
   - Просмотр списка товаров с фильтрацией по категории (`GET /products/`).
   - Получение информации о товаре по ID (`GET /products/{id}`).
   - Обновление товара (`PUT /products/{id}`).
   - Удаление товара (`DELETE /products/{id}`).

2. **Создание заказов**:
   - Оформление заказа с указанием пользователя и списка товаров (`POST /orders/`).

3. **Хранение данных**:
   - Данные о пользователях, товарах и заказах хранятся в базе данных PostgreSQL.

4. **Документация API**:
   - Интерактивная документация доступна через Swagger UI по адресу `/swagger`.

## Требования

- Docker и Docker Compose (для запуска в контейнерах).
- Git (для клонирования репозитория).
- Python 3.11 (если запускаете локально без Docker).

## Инструкции по запуску

### 1. Клонирование репозитория
Склонируйте репозиторий на свою машину:
````git clone [https://github.com/yourusername/marketplace-api.git](https://github.com/yourusername/marketplace-api.git) cd marketplace-api````

### 2. Запуск с помощью Docker Compose
1. Убедитесь, что Docker и Docker Compose установлены:
````docker --version docker-compose --version````
Если их нет, установите их согласно [официальной документации](https://docs.docker.com/get-docker/).

2. Запустите приложение:
````docker-compose up --build````
- Это соберет образ приложения и запустит два контейнера: `app` (Flask) и `postgres` (база данных).
- Приложение будет доступно на `http://localhost:8000`.

3. Остановка приложения:
````docker-compose down````

### 3. Локальный запуск (без Docker)
1. Установите PostgreSQL и создайте базу данных:
```
psql -U postgres 
CREATE DATABASE mydatabase;
CREATE USER myuser WITH PASSWORD 'mypassword'; 
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO myuser;
````

2. Установите зависимости:
````
pip install -r requirements.txt
````

3. Настройте переменную окружения для подключения к базе данных:
````
export DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/mydatabase"
````

4. Запустите приложение:
````
python app/main.py
````
- Приложение будет доступно на `http://localhost:8000`.

## Использование API

### Доступ к API
- Базовый URL: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/swagger`

### Примеры запросов

1. **Создание товара**:
````
curl -X POST "[http://localhost:8000/products/](http://localhost:8000/products/)"  
-H "Content-Type: application/json"  
-d '{"name": "Phone", "price": 299.99, "category": "Electronics"}'
````
Ответ:
````
{"id": 1, "name": "Phone", "description": null, "price": 299.99, "category": "Electronics"}
````

2. **Получение списка товаров**:
````
curl "[http://localhost:8000/products/?category=Electronics](http://localhost:8000/products/?category=Electronics)"
````
Ответ:
````
[{"id": 1, "name": "Phone", "description": null, "price": 299.99, "category": "Electronics"}]
````

3. **Создание заказа**:
````
curl -X POST "[http://localhost:8000/orders/](http://localhost:8000/orders/)"  
-H "Content-Type: application/json"  
-d '{"user_id": 1, "items": [{"product_id": 1, "quantity": 2, "price": 299.99}]}'
````
Ответ:
````
{ 
"id": 1, 
"user_id": 1, 
"order_date": "2025-04-02T12:00:00Z", 
"status": "new", 
"items": [{"product_id": 1, "quantity": 2, "price": 299.99}] 
}
````

### Документация
Полное описание всех эндпоинтов доступно в Swagger UI по адресу `http://localhost:8000/swagger`. Вы можете тестировать запросы прямо из интерфейса.

## Тестирование
Для запуска тестов:
````
pytest app/tests/
````
Тесты проверяют базовую функциональность API (создание и получение товаров).

## Примечания
- Файлы конфигурации IDE (например, `.idea/`) рекомендуется добавить в `.gitignore`.
- Для нормализации окончаний строк создайте `.gitattributes` с настройкой `eol=lf`.