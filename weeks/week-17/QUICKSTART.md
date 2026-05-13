# Быстрый старт - Tickets System

## Что готово

- 4 микросервиса (Tickets, Users, Notification, Analytics)
- Docker Compose конфигурация
- PostgreSQL + Redis
- Nginx API Gateway
- Prometheus + Grafana
- Полная документация

## Запуск системы

### 1. Убедитесь, что Docker установлен

```bash
docker --version
docker compose version
```

### 2. Запустите все сервисы

```bash
# Из директории week-17
cd /home/someotb/Code/Network-Software/weeks/week-17

sudo docker compose up -d

# Или используйте Makefile
make up
```

### 3. Проверьте статус

```bash
sudo docker compose ps

# Должны быть запущены:
# - tickets-svc-s15
# - users-svc-s15
# - notification-svc-s15
# - analytics-svc-s15
# - postgres-tickets
# - postgres-users
# - redis-tickets
# - nginx-gateway
# - prometheus
# - grafana
```

### 4. Проверьте работу API

```bash
# Health check
curl http://localhost/health

# Список тикетов (уже есть тестовые данные)
curl http://localhost/api/tickets

# Список пользователей
curl http://localhost/api/users

# Статистика
curl http://localhost/api/analytics/tickets/stats
```

## Тестовые данные

### Пользователи (пароль для всех: password123)
- admin / admin@example.com (роль: admin)
- agent1 / agent1@example.com (роль: agent)
- user1 / user1@example.com (роль: user)

### Тикеты
В базе уже есть 5 тестовых тикетов с разными статусами.

## Полезные команды

```bash
# Логи всех сервисов
sudo docker compose logs -f

# Логи конкретного сервиса
sudo docker compose logs -f tickets-service

# Остановить все
sudo docker compose down

# Остановить и удалить данные
sudo docker compose down -v

# Пересобрать образы
sudo docker compose build
```

## Доступ к сервисам

- **API Gateway**: http://localhost
- **Tickets API**: http://localhost:8124 (прямой доступ)
- **Users API**: http://localhost:8125 (прямой доступ)
- **Analytics API**: http://localhost:8126 (прямой доступ)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Swagger UI для тестирования

- **Tickets Service**: http://localhost:8124/docs
- **Users Service**: http://localhost:8125/docs
- **Analytics Service**: http://localhost:8126/docs

## Troubleshooting

### Порты заняты
Измените порты в `docker-compose.yml` если 80, 8124, 8125, 8126, 5432, 6379 уже используются.

### Сервисы не стартуют
```bash
# Проверьте логи
sudo docker compose logs

# Пересоздайте контейнеры
sudo docker compose down -v
sudo docker compose up -d
```

### База данных не инициализируется
```bash
# Подождите 10-15 секунд после запуска
sudo docker compose logs postgres-tickets
sudo docker compose logs postgres-users
```

## Что дальше?

Читайте полную документацию:
- `README.md` - подробное руководство с примерами
- `ARCHITECTURE.md` - архитектура системы
- `PROJECT_READY.md` - итоговый отчет
