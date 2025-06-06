## **Описание проекта**

Необходимо дополнить проект с прошлой недели. Проект реализует REST API для маркетплейса, позволяющего управлять товарами, заказами и пользователями. Проект использует базу данных PostgreSQL для хранения информации о пользователях, товарах и заказах, а также запускается через Docker Compose.

### Функционал исходного проекта

1. **Управление товарами**
   - Пользователь может добавлять, редактировать и удалять товары.
   - Пользователь может просматривать список товаров с фильтрами (категория, цена).
2. **Создание заказов**
   - Пользователь может создавать заказ с выбранными товарами.
   - Пользователь может видеть статус заказа (новый, в обработке, выполнен).
3. **Управление данными пользователей**
   - Все данные о пользователях, товарах и заказах хранятся в базе данных PostgreSQL.
4. **Структура базы данных**
   - **users** — таблица пользователей (id, name, email, дополнительные поля).
   - **products** — таблица товаров (id, name, description, price, category).
   - **orders** — таблица заказов (id, user_id, order_date, status).
   - **order_items** — таблица товаров в заказе (id, order_id, product_id, quantity, price).
5. **Запуск проекта через Docker Compose**
   - В файле `docker-compose.yml` описаны контейнеры для PostgreSQL и PgAdmin.
6. **CI**
   - Настройка CI через GitLab CI с автоматическим запуском тестов.

## **Новая функциональность**

Для расширения возможностей проекта необходимо добавить несколько новых фич. 

### Рейтинг товаров

- Пользователь может поставить товару оценку (от 1 до 5 звёзд).
- Рейтинг товара пересчитывается после каждой новой оценки.
- Средний рейтинг отображается вместе с информацией о товаре.

### Отзывы пользователей

- Пользователь может оставить текстовый отзыв о товаре.
- Отзывы отображаются на странице товара.
- Отзывы можно сортировать по дате или рейтингу.

### Избранные товары

- Пользователь может добавлять товары в избранное и просматривать их в отдельном разделе.
- Избранные товары сохраняются в профиле пользователя.

### Изменения в структуре базы данных

 Для поддержки новой функциональности будут добавлены новые таблицы и поля.

- **reviews** — таблица отзывов:
  - `id` (SERIAL PRIMARY KEY);
  - `user_id` (INTEGER REFERENCES users(id));
  - `product_id` (INTEGER REFERENCES products(id));
  - `rating` (INTEGER) — оценка от 1 до 5;
  - `comment` (TEXT) — текст отзыва;
  - `created_at` (TIMESTAMP) — дата отзыва.
- **favorites** — таблица избранных товаров:
  - `id` (SERIAL PRIMARY KEY);
  - `user_id` (INTEGER REFERENCES users(id));
  - `product_id` (INTEGER REFERENCES products(id)).
- В таблицу **products** необходимо добавить поле `average_rating` (DECIMAL). В поле будет храниться средний рейтинг, который обновляется при добавлении новой оценки.

## **Интеграционные тесты**

Чтобы базовый функционал и новый функционал (рейтинг товаров, отзывы и избранное) работали корректно, необходимо разработать интеграционные тесты. Они должны покрывать следующие области:

- проверка создания, чтения, обновления и удаления сущностей (CRUD);
- работа API при взаимодействии с реальной базой данных PostgreSQL в изолированной среде (с использованием Testcontainers).

Интеграционные тесты необходимо реализовать для предыдущего функционала и для новых возможностей, чтобы убедиться в стабильной работе всего приложения.

## **Система оценивания** 

### Оценка по критериям 

**1. Реализация функционала «Рейтинг товаров»: 2 балла**

- **2 балла** — реализован полный функционал: пользователь может оставлять оценку (от 1 до 5 звёзд), рейтинг товара корректно пересчитывается после каждой оценки, средний рейтинг отображается в информации о товаре, реализована соответствующая бизнес-логика.
- **1 балл** — функционал реализован частично: отсутствуют некоторые аспекты (например, пересчёт среднего рейтинга или отображение рейтинга) или имеются незначительные недочёты в обработке данных.
- **0 баллов** — функциональность не реализована или реализована с критическими ошибками.

**2. Реализация функционала «Отзывы пользователей»: 2 балла**

- **2 балла** — реализована возможность оставлять текстовые отзывы с оценкой. Отзывы корректно сохраняются, отображаются на странице товара. Имеется сортировка (по дате или рейтингу) и реализована базовая бизнес-логика для управления отзывами.
- **1 балл** — функциональность реализована частично: отсутствует одна или несколько важных возможностей (например, сортировка отзывов или валидация данных) либо имеются незначительные ошибки в сохранении или отображении отзывов.
- **0 баллов** — функциональность не реализована или реализована с критическими ошибками.

**3. Реализация функционала «Избранные товары»: 2 балла**

- **2 балла** — реализована возможность добавления товаров в избранное, удаления из избранного и получения списка избранных товаров. Данные корректно сохраняются в профиле пользователя. API соответствует стандартам REST.
- **1 балл** — функциональность реализована частично: отсутствует один из элементов (например, удаление из избранного или получение списка) либо имеются незначительные ошибки в логике работы.
- **0 баллов** — функциональность не реализована или реализована с критическими ошибками.

**4. Интеграционные тесты для новой функциональности: 2 балла**

- **2 балла** — написаны и успешно выполняются интеграционные тесты, охватывающие все новые фичи (рейтинг товаров, отзывы, избранное) с использованием Testcontainers. Данные в тестовой среде корректно и изолированно создаются и удаляются.
- **1 балл** — интеграционные тесты покрывают часть нового функционала либо имеются недочёты в тестовой среде (например, отсутствие проверки на корректность пересчёта рейтинга или неполное покрытие сценариев).
- **0 баллов** — интеграционные тесты не написаны или покрывают менее 50% нового функционала.

**5. Интеграционные тесты, объединяющие новый и базовый функционал: 2 балла**

- **2 балла** — разработаны тесты, демонстрирующие корректное взаимодействие нового функционала (отзывы, рейтинг, избранное) и существующих возможностей проекта (управление товарами, заказами, пользователями). Тесты полностью подтверждают целостность работы всей системы.
- **1 балл** — тесты частично охватывают взаимодействие нового функционала и базовых операций, имеются незначительные недочёты или сценарии, не охваченные тестами.
- **0 баллов** — тесты для проверки интеграции нового функционала с базовым отсутствуют или выполнены с критическими ошибками.



