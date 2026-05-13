# CI/CD Pipeline

GitHub Actions pipeline для автоматической сборки, тестирования и деплоя.

## Структура Pipeline

Pipeline состоит из 5 этапов:

### 1. Lint (Проверка кода)
- **flake8** - проверка стиля кода
- **pylint** - статический анализ
- **black** - форматирование (опционально)

### 2. Test (Тестирование)
- Запуск unit тестов с pytest
- Интеграционные тесты с PostgreSQL и Redis
- Генерация coverage отчетов
- Загрузка в Codecov

### 3. Build (Сборка)
- Сборка Docker образов для всех сервисов
- Тестирование docker-compose конфигурации
- Проверка health endpoints

### 4. Security (Безопасность)
- Trivy сканирование уязвимостей
- Загрузка результатов в GitHub Security

### 5. Deploy (Деплой)
- Автоматический деплой при push в main
- Публикация образов в Docker Hub
- Деплой в Kubernetes (опционально)

## Триггеры

Pipeline запускается при:
- Push в ветки: `main`, `master`, `develop`
- Pull Request в ветки: `main`, `master`

## Настройка

### Secrets в GitHub

Добавь следующие secrets в настройках репозитория:

```
Settings → Secrets and variables → Actions → New repository secret
```

**Обязательные secrets:**
- `DOCKER_USERNAME` - логин Docker Hub
- `DOCKER_PASSWORD` - пароль Docker Hub

**Опциональные secrets (для Kubernetes):**
- `KUBE_CONFIG` - конфигурация kubectl
- `KUBE_NAMESPACE` - namespace для деплоя

### Локальный запуск

Проверить pipeline локально с помощью act:

```bash
# Установить act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Запустить lint
act -j lint

# Запустить тесты
act -j test

# Запустить всё
act
```

## Этапы Pipeline

### Lint Stage

```yaml
- flake8 для проверки синтаксиса
- pylint для статического анализа
- Проверка всех Python файлов в services/
```

### Test Stage

```yaml
- Запуск PostgreSQL и Redis в Docker
- Установка зависимостей
- Запуск pytest с coverage
- Генерация XML отчета
```

### Build Stage

```yaml
- Сборка 4 Docker образов
- Проверка docker-compose config
- Запуск контейнеров
- Health check всех сервисов
```

### Security Stage

```yaml
- Trivy сканирование файловой системы
- Поиск уязвимостей в зависимостях
- Загрузка SARIF отчета в GitHub
```

### Deploy Stage

```yaml
- Только для main ветки
- Login в Docker Hub
- Build и push образов с тегом latest
- Опциональный деплой в Kubernetes
```

## Статус Pipeline

Статус можно увидеть:
- В GitHub Actions tab
- В Pull Request checks
- Badge в README (добавить):

```markdown
![CI/CD](https://github.com/username/repo/workflows/CI%2FCD%20Pipeline/badge.svg)
```

## Мониторинг

### GitHub Actions
- Логи каждого job
- Время выполнения
- Статус success/failure

### Codecov
- Coverage отчеты
- Тренды покрытия
- Комментарии в PR

### GitHub Security
- Уязвимости из Trivy
- Dependabot alerts
- Security advisories

## Оптимизация

### Кэширование

Pipeline использует кэширование для ускорения:
- Python dependencies (pip cache)
- Docker layers (buildx cache)
- GitHub Actions cache

### Параллельное выполнение

Jobs выполняются параллельно где возможно:
- lint и security - параллельно
- test после lint
- build после test
- deploy после build и security

## Troubleshooting

### Pipeline падает на lint
```bash
# Локально проверить
flake8 services/
pylint services/*/main.py
```

### Pipeline падает на test
```bash
# Локально запустить тесты
pytest tests/ -v
```

### Pipeline падает на build
```bash
# Проверить docker-compose
docker compose config
docker compose up -d
```

### Deploy не запускается
- Проверь, что push в main ветку
- Проверь наличие secrets в GitHub
- Проверь логи deploy job

## Расширение Pipeline

### Добавить новый stage

```yaml
new-stage:
  name: New Stage
  runs-on: ubuntu-latest
  needs: [previous-stage]
  
  steps:
  - name: Checkout
    uses: actions/checkout@v3
  
  - name: Do something
    run: echo "Hello"
```

### Добавить уведомления

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Добавить деплой в staging

```yaml
deploy-staging:
  if: github.ref == 'refs/heads/develop'
  steps:
  - name: Deploy to staging
    run: kubectl apply -f k8s/staging/
```

## Best Practices

1. **Всегда проверяй локально** перед push
2. **Используй secrets** для чувствительных данных
3. **Кэшируй зависимости** для ускорения
4. **Пиши тесты** для критичного кода
5. **Мониторь coverage** - стремись к 80%+
6. **Проверяй security** регулярно
7. **Документируй изменения** в pipeline

## Файлы

- `.github/workflows/ci-cd.yml` - основной pipeline
- `tests/` - директория с тестами
- `docker-compose.yml` - для локального тестирования

---

**Студент:** s15  
**Группа:** 331  
**Проект:** tickets-s15
