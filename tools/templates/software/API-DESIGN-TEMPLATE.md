# API Design Document
*Уровень абстракции: α=-1 (спецификация интерфейса)*
*Статус: ⇓ ВНИЗ (детализация архитектуры → конкретный API)*
*CYCLE: 1*

---

## Обзор API

### Назначение
[Кратко опишите назначение вашего API]

### Версия
**Текущая версия:** v1.0
**Стратегия версионирования:** [URL-based / Header-based / Content Negotiation]

### Base URL
```
Production:  https://api.example.com/v1
Staging:     https://staging-api.example.com/v1
Development: http://localhost:8000/v1
```

---

## Аутентификация

### Метод
**Выбрано:** [API Key / JWT / OAuth 2.0 / Basic Auth]

### Примеры

**API Key (Header-based):**
```http
GET /users HTTP/1.1
Host: api.example.com
X-API-Key: your-api-key-here
```

**JWT Token:**
```http
GET /users HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**OAuth 2.0:**
```http
POST /oauth/token HTTP/1.1
Host: api.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_SECRET
```

---

## Общие соглашения

### HTTP Methods

| Method | Usage | Идемпотентность |
|--------|-------|-----------------|
| GET | Получение ресурса | Да |
| POST | Создание ресурса | Нет |
| PUT | Полное обновление | Да |
| PATCH | Частичное обновление | Нет |
| DELETE | Удаление ресурса | Да |

### Status Codes

| Code | Meaning | Когда использовать |
|------|---------|-------------------|
| 200 OK | Успех | GET, PUT, PATCH успешны |
| 201 Created | Создан | POST успешен |
| 204 No Content | Нет контента | DELETE успешен |
| 400 Bad Request | Неверный запрос | Валидация не прошла |
| 401 Unauthorized | Не авторизован | Нет/неверный токен |
| 403 Forbidden | Запрещено | Нет прав доступа |
| 404 Not Found | Не найден | Ресурс не существует |
| 429 Too Many Requests | Слишком много запросов | Rate limit exceeded |
| 500 Internal Server Error | Ошибка сервера | Внутренняя ошибка |

### Response Format

**Success Response:**
```json
{
  "data": {
    "id": "123",
    "type": "user",
    "attributes": {
      "email": "user@example.com",
      "name": "John Doe"
    }
  },
  "meta": {
    "timestamp": "2026-01-24T12:00:00Z"
  }
}
```

**Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  },
  "meta": {
    "timestamp": "2026-01-24T12:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### Pagination

**Query Parameters:**
- `page` - Номер страницы (начиная с 1)
- `page_size` - Размер страницы (default: 20, max: 100)

**Example Request:**
```http
GET /users?page=2&page_size=50
```

**Example Response:**
```json
{
  "data": [...],
  "meta": {
    "page": 2,
    "page_size": 50,
    "total_pages": 10,
    "total_count": 475
  },
  "links": {
    "self": "/users?page=2&page_size=50",
    "first": "/users?page=1&page_size=50",
    "prev": "/users?page=1&page_size=50",
    "next": "/users?page=3&page_size=50",
    "last": "/users?page=10&page_size=50"
  }
}
```

### Filtering

**Example:**
```http
GET /users?status=active&role=admin&created_after=2026-01-01
```

### Sorting

**Example:**
```http
GET /users?sort=-created_at,name
```
- `-` prefix = descending order
- No prefix = ascending order

---

## Endpoints

### Users

#### List Users
```http
GET /users
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 20) |
| status | string | No | Filter by status (active, inactive) |
| search | string | No | Search by name or email |

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "user_123",
      "type": "user",
      "attributes": {
        "email": "john@example.com",
        "name": "John Doe",
        "status": "active",
        "created_at": "2026-01-24T12:00:00Z"
      }
    }
  ],
  "meta": {
    "page": 1,
    "total_count": 150
  }
}
```

---

#### Get User
```http
GET /users/{user_id}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | User ID |

**Response:** `200 OK`
```json
{
  "data": {
    "id": "user_123",
    "type": "user",
    "attributes": {
      "email": "john@example.com",
      "name": "John Doe",
      "status": "active",
      "role": "admin",
      "created_at": "2026-01-24T12:00:00Z",
      "updated_at": "2026-01-24T14:30:00Z"
    }
  }
}
```

**Errors:**
- `404 Not Found` - User not found

---

#### Create User
```http
POST /users
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "name": "New User",
  "password": "securePassword123!",
  "role": "user"
}
```

**Field Validation:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| email | string | Yes | Valid email, unique |
| name | string | Yes | 2-100 characters |
| password | string | Yes | Min 8 characters, must include uppercase, lowercase, number, special char |
| role | string | No | One of: user, admin (default: user) |

**Response:** `201 Created`
```json
{
  "data": {
    "id": "user_456",
    "type": "user",
    "attributes": {
      "email": "newuser@example.com",
      "name": "New User",
      "status": "active",
      "role": "user",
      "created_at": "2026-01-24T15:00:00Z"
    }
  }
}
```

**Errors:**
- `400 Bad Request` - Validation failed
- `409 Conflict` - Email already exists

---

#### Update User
```http
PUT /users/{user_id}
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "role": "admin"
}
```

**Response:** `200 OK`

**Errors:**
- `400 Bad Request` - Validation failed
- `404 Not Found` - User not found
- `403 Forbidden` - Insufficient permissions

---

#### Delete User
```http
DELETE /users/{user_id}
```

**Response:** `204 No Content`

**Errors:**
- `404 Not Found` - User not found
- `403 Forbidden` - Cannot delete own account or insufficient permissions

---

### Authentication

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `429 Too Many Requests` - Too many failed login attempts

---

#### Refresh Token
```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

---

#### Logout
```http
POST /auth/logout
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** `204 No Content`

---

## Rate Limiting

**Limits:**
- Authenticated users: 1000 requests/hour
- Unauthenticated: 100 requests/hour

**Response Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642857600
```

**Error Response when limit exceeded:**
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "retry_after": 3600
  }
}
```

---

## Webhooks

### Overview
[Опишите систему webhooks, если есть]

### Events
- `user.created` - Новый пользователь создан
- `user.updated` - Пользователь обновлён
- `user.deleted` - Пользователь удалён

### Payload Example
```json
{
  "event": "user.created",
  "timestamp": "2026-01-24T12:00:00Z",
  "data": {
    "id": "user_123",
    "email": "newuser@example.com"
  }
}
```

---

## OpenAPI Specification

**Location:** `/docs/openapi.yaml`

**Swagger UI:** `https://api.example.com/docs`

**ReDoc:** `https://api.example.com/redoc`

---

## SDK и Client Libraries

### Official SDKs
- **Python:** `pip install example-api-client`
- **JavaScript:** `npm install @example/api-client`
- **Go:** `go get github.com/example/api-client-go`

### Example Usage (Python)
```python
from example_api import Client

client = Client(api_key="your-api-key")

# Get user
user = client.users.get("user_123")
print(user.email)

# Create user
new_user = client.users.create(
    email="new@example.com",
    name="New User",
    password="securePass123!"
)

# List users
users = client.users.list(page=1, page_size=20, status="active")
for user in users:
    print(user.name)
```

---

## Changelog

### v1.0.0 (2026-01-24)
- Initial API release
- User management endpoints
- Authentication endpoints

---

## Связь с методологией ⇑⇓↔

**Вертикальные связи:**
- ⬆️ ВВЕРХ (α=0): [ARCHITECTURE.md] - Архитектура системы
- ⬇️ ВНИЗ (α=-2): [API-IMPLEMENTATION.md] - Реализация API endpoints

**Горизонтальные связи:**
- ↔️ СТАНДАРТЫ: REST API Best Practices, JSON:API Specification

---

**Создано с помощью методологии ⇑⇓↔**
**Версия:** 1.0
**Последнее обновление:** [дата]
