# Отчет по Docker - photos-s15

## Сборка и запуск

```bash
docker build -t photos-s15 .
docker run -p 8175:8175 photos-s15
```

## Оптимизация

**Multi-stage build:**
- Stage 1 (builder): устанавливаем зависимости
- Stage 2 (final): копируем только установленные пакеты

**Результат:**
- Размер образа (image size): ~150-200 MB (вместо ~1GB без multi-stage)
- Количество слоёв (layers): 8 слоёв
- Кэширование: изменение кода не требует переустановки зависимостей

**Слои Docker (Docker layers):**
1. FROM python:3.11-slim (базовый образ)
2. WORKDIR /app
3. COPY requirements.txt
4. RUN pip install (кэшируется!)
5. COPY . . (код приложения)
6. EXPOSE 8175
7. CMD uvicorn

**Проект:** photos-s15
