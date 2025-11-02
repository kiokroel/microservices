# Microservices - Blog API

Асинхронный REST API для управления блогом, построенный на FastAPI с поддержкой статей, комментариев и аутентификации пользователей.

## Функциональность

- **Управление пользователями**: регистрация, логин, обновление профиля
- **Управление статьями**: создание, чтение, обновление, удаление статей
- **Комментарии**: добавление и удаление комментариев к статьям
- **Аутентификация**: JWT-токены для защиты эндпоинтов
- **Асинхронность**: полная поддержка async/await с использованием asyncio
- **CORS**: включена поддержка кросс-доменных запросов

## Требования

- Docker и Docker Compose

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd microservices
```

### 2. Запуск приложения через Docker Compose

```bash
docker-compose up -d
```

Это запустит:
- PostgreSQL контейнер с БД
- Приложение FastAPI

Приложение будет доступно по адресу: `http://localhost:8000`

### 3. Остановка приложения

```bash
docker-compose down
```

## API Документация

### Интерактивная документация

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

### Основные эндпоинты

#### Здоровье приложения

```
GET /health
```
Проверка статуса приложения.

**Ответ:**
```json
{"status": "ok"}
```

#### Пользователи

**Регистрация**
```
POST /api/users/
```
Создание нового пользователя.

**Параметры:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Логин**
```
POST /api/users/login
```
Получение JWT токена.

**Параметры:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Получить текущего пользователя**
```
GET /api/users/me
```
Требует аутентификацию (JWT токен в заголовке `Authorization: Bearer <token>`).

**Обновить профиль**
```
PUT /api/users/me
```
Обновление информации о текущем пользователе.

#### Статьи

**Создать статью**
```
POST /api/articles/
```
Требует аутентификацию.

**Параметры:**
```json
{
  "title": "Заголовок статьи",
  "description": "Описание",
  "body": "Содержание статьи"
}
```

**Получить все статьи**
```
GET /api/articles/?skip=0&limit=20
```
Публичный эндпоинт. Поддерживает пагинацию.

**Получить статью по slug**
```
GET /api/articles/{slug}
```
Получение конкретной статьи.

**Обновить статью**
```
PUT /api/articles/{slug}
```
Требует аутентификацию. Может обновлять только автор.

**Удалить статью**
```
DELETE /api/articles/{slug}
```
Требует аутентификацию. Может удалять только автор.

#### Комментарии

**Добавить комментарий**
```
POST /api/articles/{slug}/comments
```
Требует аутентификацию.

**Параметры:**
```json
{
  "body": "Текст комментария"
}
```

**Получить комментарии статьи**
```
GET /api/articles/{slug}/comments?skip=0&limit=20
```
Публичный эндпоинт. Поддерживает пагинацию.

**Удалить комментарий**
```
DELETE /api/articles/{slug}/comments/{comment_id}
```
Требует аутентификацию. Может удалять только автор комментария.

## Структура проекта

```
microservices/
├── src/
│   ├── main.py                 # Точка входа приложения
│   ├── controllers/            # Бизнес-логика
│   │   ├── article.py
│   │   ├── comment.py
│   │   └── user.py
│   ├── routes/                 # API маршруты
│   │   ├── articles.py
│   │   ├── comments.py
│   │   └── users.py
│   ├── models/                 # SQLAlchemy модели
│   │   ├── article.py
│   │   ├── comment.py
│   │   └── user.py
│   ├── schemas/                # Pydantic схемы валидации
│   │   ├── article.py
│   │   ├── comment.py
│   │   └── user.py
│   ├── repositories/           # Слой доступа к данным
│   │   ├── base.py
│   │   ├── article.py
│   │   ├── comment.py
│   │   └── user.py
│   ├── core/                   # Конфигурация и утилиты
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   └── dependencies.py         # Зависимости FastAPI
├── alembic/                    # Миграции БД
├── Dockerfile                  # Docker конфигурация
├── docker-compose.yml          # Docker Compose конфигурация
├── pyproject.toml              # Конфигурация Poetry
└── README.md                   # Этот файл
```

## Архитектура

Приложение следует многоуровневой архитектуре:

1. **Routes** - HTTP эндпоинты и валидация запросов
2. **Controllers** - Бизнес-логика приложения
3. **Repositories** - Абстракция доступа к БД
4. **Models** - ORM модели SQLAlchemy
5. **Schemas** - Pydantic модели для валидации

