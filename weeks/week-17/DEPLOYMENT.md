# Руководство по развёртыванию tickets-s15

## Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/user/tickets-s15.git
cd tickets-s15

# Запустить все сервисы
docker-compose up -d

# Проверить работоспособность
curl http://localhost/api/tickets
```

## Требования

- Docker 20.10+
- Docker Compose 2.0+
- RAM: 4GB минимум
- Disk: 10GB свободного места

## Локальная разработка

### Запуск с Docker Compose

```bash
docker-compose up -d
```

Сервисы будут доступны:
- Tickets API: http://localhost:8124
- Users API: http://localhost:8125
- Analytics API: http://localhost:8126
- Notification gRPC: localhost:50051
- Nginx Gateway: http://localhost
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Развёртывание в Kubernetes

```bash
# Создать namespace
kubectl create namespace tickets-s15

# Применить манифесты
kubectl apply -f k8s/

# Или через Helm
helm install tickets-s15 ./helm-chart
```

## Мониторинг

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Troubleshooting

```bash
# Логи
docker-compose logs -f tickets-service

# Статус
docker-compose ps

# Перезапуск
docker-compose restart tickets-service
```

Подробная документация: см. ARCHITECTURE.md
