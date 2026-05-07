# Архитектура проекта tickets-s15

## Обзор проекта

**Название**: tickets-s15  
**Описание**: Микросервисная система управления тикетами (Service Desk / Issue Tracking System)  
**Цель**: Демонстрация знаний REST, gRPC, Docker, Kubernetes, CI/CD

## Бизнес-требования

Система позволяет:
- Создавать, просматривать, обновлять и удалять тикеты
- Назначать тикеты исполнителям
- Отслеживать статус тикетов (new, in_progress, resolved, closed)
- Получать уведомления об изменениях
- Просматривать статистику и метрики

## Архитектура системы

### High-Level Architecture

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────────┐
│         API Gateway (Nginx)             │
│         Port: 80/443                    │
└──────┬──────────────────────────────────┘
       │
       ├──────────────┬──────────────┬─────────────┐
       │              │              │             │
       ▼              ▼              ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────┐
│   Tickets    │ │    Users     │ │  Notif.  │ │ Analytics│
│   Service    │ │   Service    │ │ Service  │ │ Service  │
│   (REST)     │ │   (REST)     │ │ (gRPC)   │ │  (REST)  │
│   :8124      │ │   :8125      │ │  :50051  │ │  :8126   │
└──────┬───────┘ └──────┬───────┘ └────┬─────┘ └────┬─────┘
       │                │               │            │
       │                │               │            │
       ▼                ▼               ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────┐
│  PostgreSQL  │ │  PostgreSQL  │ │  Redis   │ │  Redis   │
│  (tickets)   │ │   (users)    │ │ (queue)  │ │ (cache)  │
└──────────────┘ └──────────────┘ └──────────┘ └──────────┘
```

## Микросервисы

### 1. Tickets Service (tickets-svc-s15)
**Технологии**: Python 3.11, FastAPI  
**Порт**: 8124  
**Протокол**: REST API  
**База данных**: PostgreSQL

**Endpoints**:
- `GET /api/tickets` - список тикетов
- `GET /api/tickets/{id}` - получить тикет
- `POST /api/tickets` - создать тикет
- `PUT /api/tickets/{id}` - обновить тикет
- `DELETE /api/tickets/{id}` - удалить тикет
- `PATCH /api/tickets/{id}/status` - изменить статус

**Модель данных**:
```python
class Ticket:
    id: int
    title: str
    description: str
    status: str  # new, in_progress, resolved, closed
    priority: int  # 1-5
    assignee_id: int
    reporter_id: int
    created_at: datetime
    updated_at: datetime
```

**Зависимости**:
- Users Service (для валидации пользователей)
- Notification Service (для отправки уведомлений)
- Analytics Service (для логирования событий)

### 2. Users Service
**Технологии**: Python 3.11, FastAPI  
**Порт**: 8125  
**Протокол**: REST API  
**База данных**: PostgreSQL

**Endpoints**:
- `POST /api/users/register` - регистрация
- `POST /api/users/login` - аутентификация
- `GET /api/users/{id}` - профиль пользователя
- `GET /api/users` - список пользователей

**Модель данных**:
```python
class User:
    id: int
    username: str
    email: str
    password_hash: str
    role: str  # admin, agent, user
    created_at: datetime
```

**Функции**:
- JWT аутентификация
- Управление ролями и правами
- Хеширование паролей (bcrypt)

### 3. Notification Service
**Технологии**: Python 3.11, gRPC  
**Порт**: 50051  
**Протокол**: gRPC  
**Очередь**: Redis

**gRPC Methods**:
```protobuf
service NotificationService {
  rpc SendNotification(NotificationRequest) returns (NotificationResponse);
  rpc GetNotifications(GetNotificationsRequest) returns (stream Notification);
}

message NotificationRequest {
  int32 user_id = 1;
  string type = 2;  // email, push, in_app
  string title = 3;
  string message = 4;
}
```

**Функции**:
- Асинхронная отправка уведомлений
- Поддержка email, push, in-app уведомлений
- Очередь сообщений в Redis
- Retry механизм

### 4. Analytics Service
**Технологии**: Python 3.11, FastAPI  
**Порт**: 8126  
**Протокол**: REST API  
**Кэш**: Redis

**Endpoints**:
- `GET /api/analytics/tickets/stats` - статистика по тикетам
- `GET /api/analytics/users/activity` - активность пользователей
- `GET /api/analytics/performance` - метрики производительности

**Метрики**:
- Количество тикетов по статусам
- Среднее время решения
- Загрузка агентов
- Тренды по времени

## Межсервисное взаимодействие

### REST для внешнего API
- Используется для клиент-сервер коммуникации
- Простая интеграция с фронтендом
- Стандартные HTTP методы и статус коды

### gRPC для внутренней коммуникации
- Notification Service использует gRPC для высокой производительности
- Бинарная сериализация (Protobuf)
- Streaming для real-time уведомлений
- Type safety

### Event-Driven через Redis
- Асинхронные события между сервисами
- Pub/Sub для уведомлений
- Очереди для фоновых задач

## Базы данных

### PostgreSQL (Tickets DB)
```sql
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 3,
    assignee_id INTEGER,
    reporter_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_assignee ON tickets(assignee_id);
```

### PostgreSQL (Users DB)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Redis
- **Кэш**: результаты запросов, сессии
- **Очередь**: задачи для Notification Service
- **Pub/Sub**: real-time события

## Инфраструктура

### Docker
Каждый сервис упакован в отдельный Docker образ:

```dockerfile
# tickets-service/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8124
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8124"]
```

### Docker Compose (локальная разработка)
```yaml
version: '3.8'
services:
  tickets-service:
    build: ./tickets-service
    ports:
      - "8124:8124"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres-tickets/tickets
    depends_on:
      - postgres-tickets
      - redis
  
  users-service:
    build: ./users-service
    ports:
      - "8125:8125"
  
  notification-service:
    build: ./notification-service
    ports:
      - "50051:50051"
  
  analytics-service:
    build: ./analytics-service
    ports:
      - "8126:8126"
  
  postgres-tickets:
    image: postgres:15
    environment:
      POSTGRES_DB: tickets
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
  
  postgres-users:
    image: postgres:15
    environment:
      POSTGRES_DB: users
  
  redis:
    image: redis:7-alpine
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Kubernetes

**Deployment для Tickets Service**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tickets-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tickets-app
  template:
    metadata:
      labels:
        app: tickets-app
    spec:
      containers:
      - name: tickets-container
        image: tickets-s15:latest
        ports:
        - containerPort: 8124
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: tickets-db-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8124
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8124
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: tickets-svc-s15
spec:
  type: ClusterIP
  selector:
    app: tickets-app
  ports:
  - port: 8124
    targetPort: 8124
```

**Helm Chart**: см. week-13 для шаблонизации

### CI/CD Pipeline

**GitHub Actions** (см. week-14):
1. **Lint**: flake8, pylint
2. **Test**: pytest с coverage
3. **Build**: Docker образы для всех сервисов
4. **Push**: в Docker Hub / Container Registry
5. **Deploy**: kubectl apply или Helm upgrade

## Безопасность

### Аутентификация и авторизация
- JWT токены для API
- Role-Based Access Control (RBAC)
- Refresh tokens

### Защита данных
- HTTPS для всех соединений
- Хеширование паролей (bcrypt)
- Шифрование чувствительных данных в БД
- Secrets в Kubernetes Secrets

### API Security
- Rate limiting (100 req/min)
- Input validation
- SQL injection защита (ORM)
- CORS политика
- Security headers (CSP, X-Frame-Options)

### Мониторинг
- Логирование всех запросов
- Алерты на подозрительную активность
- Audit log для критических операций

## Мониторинг и Observability

### Метрики (Prometheus)
- Request rate, latency, errors
- Database connection pool
- Queue length
- CPU/Memory usage

### Логирование (ELK Stack)
- Структурированные JSON логи
- Correlation ID для трейсинга
- Централизованное хранилище

### Трейсинг (Jaeger)
- Distributed tracing между сервисами
- Визуализация запросов
- Performance bottlenecks

### Health Checks
- `/health` - liveness probe
- `/ready` - readiness probe
- `/metrics` - Prometheus metrics

## Масштабирование

### Горизонтальное масштабирование
- Kubernetes HPA (Horizontal Pod Autoscaler)
- Автоматическое масштабирование при CPU > 70%
- Min replicas: 2, Max replicas: 10

### Вертикальное масштабирование
- Увеличение resources.limits при необходимости
- Database read replicas для чтения

### Кэширование
- Redis для часто запрашиваемых данных
- TTL: 5 минут для списков, 1 час для статики
- Cache invalidation при обновлениях

## Disaster Recovery

### Backup
- Ежедневные бэкапы PostgreSQL
- Point-in-time recovery
- Хранение в S3 / Cloud Storage

### High Availability
- Multi-AZ deployment
- Database replication
- Load balancing

## Запуск проекта

### Локально (Docker Compose)
```bash
# Клонировать репозиторий
git clone https://github.com/user/tickets-s15.git
cd tickets-s15

# Запустить все сервисы
docker-compose up -d

# Применить миграции
docker-compose exec tickets-service alembic upgrade head

# Проверить статус
curl http://localhost/api/tickets
```

### В Kubernetes
```bash
# Применить манифесты
kubectl apply -f k8s/

# Или через Helm
helm install tickets-s15 ./helm-chart

# Проверить статус
kubectl get pods
kubectl get services
```

## Технологический стек

**Backend**:
- Python 3.11
- FastAPI (REST)
- gRPC + Protobuf
- SQLAlchemy (ORM)
- Alembic (миграции)

**Databases**:
- PostgreSQL 15
- Redis 7

**Infrastructure**:
- Docker
- Kubernetes
- Helm
- Nginx

**CI/CD**:
- GitHub Actions
- Docker Hub

**Monitoring**:
- Prometheus
- Grafana
- ELK Stack

## Дальнейшее развитие

1. **Frontend**: React SPA для UI
2. **WebSocket**: Real-time обновления
3. **File attachments**: Загрузка файлов к тикетам
4. **Search**: Elasticsearch для полнотекстового поиска
5. **Mobile app**: React Native приложение
6. **AI**: Автоматическая категоризация тикетов

## Заключение

Архитектура tickets-s15 демонстрирует современный подход к построению микросервисных систем с использованием REST и gRPC, контейнеризации, оркестрации и CI/CD практик. Система спроектирована с учётом масштабируемости, отказоустойчивости и безопасности.
