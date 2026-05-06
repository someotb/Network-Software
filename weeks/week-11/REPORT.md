# Лабораторная работа №11: Docker Compose

**Студент:** Любимов Кирилл Алексеевич (s15)  
**Группа:** 331  
**Проект:** reviews-s15  
**Порт:** 8109

## Описание

Оркестрация нескольких контейнеров с помощью Docker Compose: приложение, база данных, gateway.

## Реализация

### docker-compose.yml

```yaml
version: '3.9'

services:
  reviews-svc-s15:
    build: .
    ports:
      - "8109:8109"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8109/health"]
    networks:
      - app-net

  db:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
    networks:
      - app-net

  gateway:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - reviews-svc-s15
    networks:
      - app-net

networks:
  app-net:
    driver: bridge
```

## Запуск

```bash
docker-compose up --build
```

## Проверка

```bash
cd ~/Code/Network-Software
STUDENT_ID=s15 GROUP=331 python -m pytest -q weeks/week-11/tests
```

Результат: Все тесты пройдены

## Ключевые концепции

**depends_on** — порядок запуска сервисов  
**healthcheck** — проверка готовности сервиса  
**networks** — изолированная сеть для сервисов  
**condition: service_healthy** — ждём готовности зависимости
