# Лабораторная работа №6: GraphQL клиент

**Студент:** Любимов Кирилл Алексеевич (s15)  
**Группа:** 331  
**Ресурс:** likes (лайки)  
**Дополнительное поле:** target (цель лайка)

## Описание задания

Реализовать GraphQL клиент для отправки запросов к GraphQL серверу. Клиент должен уметь:
- Формировать правильный JSON payload для GraphQL запросов
- Использовать переменные вместо прямой подстановки значений
- Обрабатывать ответы сервера (data и errors)

## Реализация

### Функция `build_payload` (`app/client.py`)

```python
PROJECT_CODE = "likes-s15"

def build_payload(query: str, variables: dict) -> dict:
    return {
        "query": query,
        "variables": variables
    }
```

Функция формирует стандартный JSON для GraphQL запроса:
- `query` — текст запроса (Query или Mutation)
- `variables` — словарь с переменными для подстановки

## Как работает GraphQL клиент

### Структура запроса

Все GraphQL запросы отправляются на один endpoint (`/graphql`) методом POST с JSON телом:

```json
{
  "query": "query($id: ID!) { like(id: $id) { id target } }",
  "variables": { "id": "1" }
}
```

### Пример использования

#### Query — получение данных:
```python
import requests

payload = build_payload(
    query="query { likes { id target } }",
    variables={}
)
response = requests.post("http://localhost:8214/graphql", json=payload)
data = response.json()
```

#### Mutation — создание лайка:
```python
payload = build_payload(
    query="""
        mutation($text: String!, $target: String!) {
            createLike(input: {text: $text, target: $target}) {
                id
                text
                target
            }
        }
    """,
    variables={
        "text": "Отличный пост!",
        "target": "post-123"
    }
)
response = requests.post("http://localhost:8214/graphql", json=payload)
```

### Обработка ответов

GraphQL может вернуть три варианта ответа:

1. **Успех** — только `data`:
```json
{
  "data": { "likes": [...] }
}
```

2. **Ошибка** — только `errors`:
```json
{
  "errors": [{ "message": "Like not found" }]
}
```

3. **Частичный успех** — `data` + `errors`:
```json
{
  "data": { "like1": {...}, "like2": null },
  "errors": [{ "message": "Like 2 not found" }]
}
```

**Важно:** HTTP статус 200 не гарантирует успех! Нужно проверять поле `errors`.

## Ключевые концепции

### Зачем нужны переменные?

**Плохо (прямая подстановка):**
```python
user_id = input()
query = f"{{ like(id: {user_id}) {{ target }} }}"  # Опасно!
```

**Хорошо (переменные):**
```python
query = "query($id: ID!) { like(id: $id) { target } }"
variables = {"id": user_id}  # Безопасно
```

**Причины:**
1. **Безопасность** — защита от GraphQL injection
2. **Производительность** — сервер кэширует парсинг запроса
3. **Читаемость** — запрос отделён от данных

### Один endpoint для всего

В REST:
- `GET /likes` — получить список
- `GET /likes/1` — получить один
- `POST /likes` — создать

В GraphQL:
- `POST /graphql` — всё через один endpoint
- Тип операции и структура данных в теле запроса

## Проверка

```bash
# Запустить тесты
cd ~/Code/Network-Software
STUDENT_ID=s15 GROUP=331 python -m pytest -q weeks/week-06/tests
```

Результат: Все тесты пройдены

## Ответы на вопросы

### 1. Зачем нужны variables? Почему нельзя склеивать строки?

**Причины:**
- **Безопасность:** Защита от GraphQL injection (как SQL injection)
- **Производительность:** Сервер кэширует парсинг запроса (запрос всегда одинаковый, меняются только переменные)
- **Валидация:** Сервер проверяет типы переменных

### 2. Из каких полей состоит стандартный JSON-запрос?

```json
{
  "query": "query($id: ID!) { ... }",
  "variables": { "id": 1 },
  "operationName": "GetLike"  // опционально
}
```

Обязательные поля:
- `query` — текст запроса
- `variables` — словарь с переменными

### 3. Почему у GraphQL только один endpoint?

В REST разные URL для разных ресурсов (`/users`, `/posts`). В GraphQL вся информация о запросе (тип операции, поля, фильтры) передаётся в теле запроса, поэтому endpoint один — `/graphql`.

### 4. Что означает поле errors? Может ли оно прийти с data?

`errors` означает, что произошла ошибка при выполнении запроса. Может прийти вместе с `data` при **частичном успехе**:

```graphql
query {
  like1: like(id: 1) { target }  # Найден
  like2: like(id: 999) { target }  # Не найден
}
```

Ответ:
```json
{
  "data": { "like1": {...}, "like2": null },
  "errors": [{ "message": "Like 999 not found" }]
}
```

### 5. Как обрабатывать ошибки при статусе 200?

В GraphQL статус 200 не гарантирует успех. Нужно проверять поле `errors`:

```python
response = requests.post(url, json=payload)
data = response.json()

if "errors" in data:
    print("Ошибки:", data["errors"])
if "data" in data:
    print("Данные:", data["data"])
```

### 6. Плюсы типизированных клиентов (Apollo, Relay)?

**Преимущества:**
- **Кэширование на уровне приложения** (не зависит от HTTP)
- **Автоматическая типизация** (генерация TypeScript типов из схемы)
- **Нормализация данных** (один объект в кэше, даже если пришёл в разных запросах)
- **Оптимистичные обновления** (UI обновляется до ответа сервера)
- **Автоматический retry** и обработка ошибок
- **DevTools** для отладки запросов

Простые HTTP-запросы проще, но для больших приложений типизированные клиенты дают много преимуществ.
