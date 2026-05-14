# Tickets System

Микросервисная система для управления тикетами с 3 сервисами.

**Студент:** Любимов Кирилл Алексеевич | **Группа:** ИА-331

---

## Архитектура системы

Система состоит из **3 микросервисов**:

1. **Tickets Service** (REST API) - управление тикетами
2. **Users Service** (REST API) - управление пользователями
3. **Notification Service** (gRPC) - отправка уведомлений

**Инфраструктура:**
- PostgreSQL - единая база данных
- Redis - кэш и очередь уведомлений
- Nginx - API Gateway

---

## Быстрый старт

### Требования
- Docker 20.10+
- Docker Compose 2.0+

### Запуск системы

```bash
# Запустить все сервисы
docker compose up -d

# Проверить статус
docker compose ps

# Посмотреть логи
docker compose logs -f
```

---

## Тестирование API

### Swagger UI

- **Tickets Service**: http://localhost:8124/docs
- **Users Service**: http://localhost:8125/docs

### Примеры запросов

**Создать пользователя:**
```bash
curl -X POST http://localhost/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }'
```

**Создать тикет:**
```bash
curl -X POST http://localhost/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bug in system",
    "description": "Description here",
    "status": "new",
    "priority": 3,
    "reporter_id": 1
  }'
```

**Получить все тикеты:**
```bash
curl http://localhost/api/tickets
```

---

## Технологии

- **Backend**: Python 3.11, FastAPI
- **Протоколы**: REST API, gRPC
- **БД**: PostgreSQL 15, Redis 7
- **Инфраструктура**: Docker, Docker Compose, Nginx

---

## Остановка системы

```bash
# Остановить все сервисы
docker compose down

# Остановить и удалить данные
docker compose down -v
```
