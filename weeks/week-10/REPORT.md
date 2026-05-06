# Лабораторная работа №10: Docker контейнеризация

**Студент:** Любимов Кирилл Алексеевич (s15)  
**Группа:** 331  
**Проект:** photos-s15  
**Порт:** 8175

## Описание

Упаковка приложения в Docker контейнер с использованием multi-stage build для оптимизации размера образа.

## Реализация

### Dockerfile (Multi-stage build)

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
EXPOSE 8175
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8175"]
```

**Преимущества multi-stage:**
- Stage 1 (builder): устанавливаем зависимости
- Stage 2 (final): копируем только результат
- Размер образа: ~150-200 MB вместо ~1GB

### .dockerignore

```
.venv
__pycache__
*.pyc
.git
.pytest_cache
tests/
```

Исключаем лишние файлы из контекста сборки.

## Запуск

```bash
docker build -t photos-s15 .
docker run -p 8175:8175 photos-s15
```

## Проверка

```bash
cd ~/Code/Network-Software
STUDENT_ID=s15 GROUP=331 python -m pytest -q weeks/week-10/tests
```

Результат: Все тесты пройдены

## Ключевые концепции

**Multi-stage build** — несколько FROM в одном Dockerfile  
**Layer caching** — Docker кэширует неизменённые слои  
**Image size** — меньше образ = быстрее деплой  
**.dockerignore** — исключает файлы из контекста сборки
