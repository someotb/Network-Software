# Tickets System - Система управления тикетами

Микросервисная система для управления тикетами с REST API, gRPC, Docker и мониторингом.

**Студент:** s15 | **Группа:** 331 | **Проект:** tickets-s15

---

## Быстрый старт

### Требования
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM

### Запуск системы

```bash
# Перейти в директорию проекта
cd /home/someotb/Code/Network-Software/weeks/week-17

# Запустить все сервисы
sudo docker compose up -d

# Проверить статус (все должны быть "Up" и "healthy")
sudo docker compose ps

# Посмотреть логи (опционально)
sudo docker compose logs -f
```

**Подожди 10-15 секунд** после запуска, чтобы все сервисы полностью инициализировались.

---

## Тестирование системы

### 1. Swagger UI (Интерактивная документация API)

Swagger UI - это веб-интерфейс для тестирования API прямо в браузере.

**Открой в браузере:**

- **Tickets Service**: http://localhost:8124/docs
- **Users Service**: http://localhost:8125/docs  
- **Analytics Service**: http://localhost:8126/docs

#### Как использовать Swagger:

1. Открой любой endpoint (например, `GET /api/tickets`)
2. Нажми **"Try it out"**
3. Заполни параметры (если нужно)
4. Нажми **"Execute"**
5. Увидишь результат внизу

---

### 2. Примеры запросов через curl

#### Tickets Service (Управление тикетами)

**Получить все тикеты:**
```bash
curl http://localhost/api/tickets
```

**Получить тикет по ID:**
```bash
curl http://localhost/api/tickets/1
```

**Создать новый тикет:**
```bash
curl -X POST http://localhost/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новый баг",
    "description": "Описание проблемы",
    "status": "new",
    "priority": 5,
    "reporter_id": 1,
    "assignee_id": 2
  }'
```

**Обновить тикет:**
```bash
curl -X PUT http://localhost/api/tickets/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": 4
  }'
```

**Изменить статус тикета:**
```bash
curl -X PATCH "http://localhost/api/tickets/1/status?status=resolved"
```

**Удалить тикет:**
```bash
curl -X DELETE http://localhost/api/tickets/1
```

**Фильтрация тикетов:**
```bash
# По статусу
curl "http://localhost/api/tickets?status=new"

# По исполнителю
curl "http://localhost/api/tickets?assignee_id=2"

# С пагинацией
curl "http://localhost/api/tickets?skip=0&limit=10"
```

---

#### Users Service (Пользователи и аутентификация)

**Получить всех пользователей:**
```bash
curl http://localhost/api/users
```

**Получить пользователя по ID:**
```bash
curl http://localhost/api/users/1
```

**Зарегистрировать нового пользователя:**
```bash
curl -X POST http://localhost/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123",
    "role": "user"
  }'
```

**Войти в систему (получить JWT токен):**
```bash
curl -X POST http://localhost/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

**Тестовые пользователи** (пароль для всех: `password123`):
- `admin` / admin@example.com (роль: admin)
- `agent1` / agent1@example.com (роль: agent)
- `user1` / user1@example.com (роль: user)

---

#### Analytics Service (Статистика)

**Статистика по тикетам:**
```bash
curl http://localhost/api/analytics/tickets/stats
```

**Активность пользователя:**
```bash
curl "http://localhost/api/analytics/users/activity?user_id=1"
```

**Метрики производительности:**
```bash
curl http://localhost/api/analytics/performance
```

---

### 3. Мониторинг

#### Prometheus (Метрики)
**URL:** http://localhost:9090

Примеры запросов в Prometheus:
- `up` - статус всех сервисов
- `process_cpu_seconds_total` - использование CPU

#### Grafana (Визуализация)
**URL:** http://localhost:3000  
**Логин:** admin  
**Пароль:** admin

---

## Структура проекта

```
week-17/
├── services/
│   ├── tickets-service/       # REST API для тикетов
│   ├── users-service/          # REST API + JWT auth
│   ├── notification-service/   # gRPC сервис
│   └── analytics-service/      # REST API + Redis cache
├── init-scripts/               # SQL инициализация БД
├── nginx/                      # API Gateway конфиг
├── monitoring/                 # Prometheus конфиг
├── docker-compose.yml          # Оркестрация всех сервисов
└── README.md                   # Этот файл
```

---

## Управление системой

### Остановить все сервисы
```bash
sudo docker compose down
```

### Остановить и удалить данные (БД будут очищены)
```bash
sudo docker compose down -v
```

### Перезапустить конкретный сервис
```bash
sudo docker compose restart tickets-service
```

### Посмотреть логи
```bash
# Все сервисы
sudo docker compose logs -f

# Конкретный сервис
sudo docker compose logs -f tickets-service

# Последние 50 строк
sudo docker compose logs --tail=50 tickets-service
```

### Пересобрать образы (после изменения кода)
```bash
# Все сервисы
sudo docker compose build

# Конкретный сервис
sudo docker compose build tickets-service

# Пересобрать и перезапустить
sudo docker compose up -d --build
```

---

## Сценарии тестирования

### Сценарий 1: Создание и обработка тикета

1. **Создай нового пользователя** через Swagger UI (http://localhost:8125/docs)
2. **Создай тикет** через Swagger UI (http://localhost:8124/docs)
3. **Назначь тикет исполнителю** через PUT `/api/tickets/{id}`
4. **Измени статус** через PATCH `/api/tickets/{id}/status`
5. **Посмотри статистику** через GET `/api/analytics/tickets/stats`

### Сценарий 2: Работа с пользователями

1. **Зарегистрируй пользователя** через POST `/api/users/register`
2. **Войди в систему** через POST `/api/users/login`
3. **Посмотри активность** через GET `/api/analytics/users/activity?user_id=1`

---

## Health Checks

```bash
# Tickets Service
curl http://localhost:8124/health
curl http://localhost:8124/ready

# Users Service
curl http://localhost:8125/health
curl http://localhost:8125/ready

# Analytics Service
curl http://localhost:8126/health
curl http://localhost:8126/ready

# Nginx Gateway
curl http://localhost/health
```

---

## Troubleshooting

### Порты заняты
```bash
sudo lsof -i :8124
# Изменить порты в docker-compose.yml
```

### Сервис не запускается
```bash
sudo docker compose logs <service-name>
sudo docker compose restart <service-name>
```

### База данных не отвечает
```bash
sudo docker compose ps postgres-tickets
sudo docker compose exec postgres-tickets psql -U tickets_user -d tickets_db
```

### Очистить всё и начать заново
```bash
sudo docker compose down -v
sudo docker compose up -d
```

---

## Дополнительная документация

- **ARCHITECTURE.md** - детальная архитектура системы
- **QUICKSTART.md** - краткое руководство
- **PROJECT_READY.md** - итоговый отчет

---

## Технологии

**Backend:**
- Python 3.11
- FastAPI (REST API)
- gRPC + Protobuf
- SQLAlchemy ORM
- JWT Authentication

**Databases:**
- PostgreSQL 15
- Redis 7

**Infrastructure:**
- Docker & Docker Compose
- Nginx (API Gateway)
- Prometheus + Grafana

---

## Чеклист для проверки

- [ ] Все контейнеры запущены
- [ ] Swagger UI открывается
- [ ] API возвращает тикеты
- [ ] Можно создать тикет через Swagger
- [ ] Можно зарегистрировать пользователя
- [ ] Статистика работает
- [ ] Prometheus доступен
- [ ] Grafana доступна

---

**Студент:** s15  
**Группа:** 331  
**Проект:** tickets-s15
