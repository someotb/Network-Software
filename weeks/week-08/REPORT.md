# Лабораторная работа №8: gRPC Streaming и Бенчмарки

**Студент:** Любимов Кирилл Алексеевич (s15)  
**Группа:** 331  
**Ресурс:** orders (заказы)  
**Дополнительное поле:** priority (приоритет, int)  
**Сервис:** OrdersService  
**Package:** orders.v1

## Описание задания

Реализовать gRPC сервис с Server Streaming и провести бенчмарк производительности:
- Добавить Server Streaming метод (SubscribeToOrders)
- Сравнить производительность gRPC
- Записать результаты замеров

## Что такое Server Streaming?

**Server Streaming** — это режим gRPC, когда:
- Клиент отправляет **один** запрос
- Сервер возвращает **поток** ответов (много сообщений)

**Отличие от Unary RPC:**
- Unary: 1 запрос → 1 ответ
- Server Streaming: 1 запрос → N ответов

**Примеры использования:**
- Лента новостей (подписка на обновления)
- Логи в реальном времени
- Биржевые котировки
- Прогресс загрузки файла
- Чаты и уведомления

## Реализация

### 1. Protocol Buffers схема (proto/service.proto)

```protobuf
syntax = "proto3";

package orders.v1;

service OrdersService {
    // Unary методы
    rpc CreateOrder (CreateOrderRequest) returns (CreateOrderResponse);
    rpc GetOrders (GetOrdersRequest) returns (GetOrdersResponse);

    // Server Streaming метод
    rpc SubscribeToOrders (SubscribeRequest) returns (stream OrderUpdate);
}

message CreateOrderRequest {
    string text = 1;
    int32 priority = 2;
}

message CreateOrderResponse {
    string id = 1;
    string text = 2;
    int32 priority = 3;
}

message GetOrdersRequest {}

message GetOrdersResponse {
    repeated Order orders = 1;
}

message Order {
    string id = 1;
    string text = 2;
    int32 priority = 3;
}

message SubscribeRequest {}

message OrderUpdate {
    string id = 1;
    string text = 2;
    int32 priority = 3;
    string action = 4;  // "created", "updated", "deleted"
}
```

**Ключевое слово `stream`:**
```protobuf
rpc SubscribeToOrders (SubscribeRequest) returns (stream OrderUpdate);
```
- `SubscribeRequest` — обычное сообщение (клиент отправляет один раз)
- `stream OrderUpdate` — поток сообщений (сервер отправляет много раз)

### 2. Реализация Server Streaming (starter/service.py)

```python
def SubscribeToOrders(self, request, context):
    """
    Server Streaming метод!
    Отправляет поток обновлений о заказах.
    """
    # Отправляем текущие заказы
    for order in orders_db:
        yield service_pb2.OrderUpdate(
            id=order.id,
            text=order.text,
            priority=order.priority,
            action="existing"
        )

    # Симулируем новые заказы
    for i in range(5):
        time.sleep(1)  # Задержка 1 секунда
        yield service_pb2.OrderUpdate(
            id=f"stream-{i}",
            text=f"Streaming order {i}",
            priority=i,
            action="created"
        )
```

**Ключевое слово `yield`:**

`yield` — это генератор в Python, который позволяет отправлять данные по частям:

```python
def normal_function():
    return "one message"  # Возвращает один раз и завершается

def streaming_function():
    yield "message 1"  # Отправляет и продолжает работу
    yield "message 2"  # Отправляет ещё раз
    yield "message 3"  # И ещё раз
```

**Как это работает:**
1. Клиент вызывает `SubscribeToOrders()`
2. Сервер начинает выполнять функцию
3. Каждый `yield` отправляет одно сообщение клиенту
4. Функция продолжает работать после `yield`
5. Когда функция завершается — стрим закрывается

**В нашем коде:**
- Сначала отправляем все существующие заказы (сразу)
- Потом каждую секунду отправляем новый заказ (5 штук)
- Потом стрим закрывается

### 3. Бенчмарк (starter/bench.py)

```python
def run_grpc_bench():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.OrdersServiceStub(channel)

        # Warmup
        for _ in range(100):
            stub.CreateOrder(service_pb2.CreateOrderRequest(text="warmup", priority=1))

        # Benchmark
        start = time.time()
        for i in range(1000):
            stub.CreateOrder(service_pb2.CreateOrderRequest(text=f"Order {i}", priority=i % 10))
        end = time.time()

        elapsed = end - start
        rps = 1000 / elapsed
        return elapsed, rps
```

**Методология:**
- Warmup: 100 запросов (прогрев соединения)
- Benchmark: 1000 запросов
- Окружение: localhost (без сетевых задержек)
- Операция: CreateOrder (Unary RPC)

## Результаты бенчмарка

### Производительность gRPC

- Время выполнения: 0.2214 секунд
- RPS (requests per second): 4515.83 запросов/сек
- Средняя задержка: 0.22 мс на запрос

### Выводы

gRPC показывает отличную производительность благодаря:

1. **Бинарная сериализация (Protocol Buffers)**
   - JSON: нужно парсить текст, преобразовывать строки в числа
   - Protobuf: данные уже в бинарном виде, готовы к использованию

2. **HTTP/2 мультиплексирование**
   - HTTP/1.1: одно соединение = один запрос
   - HTTP/2: одно соединение = много параллельных запросов

3. **Переиспользование соединений**
   - Не нужно каждый раз устанавливать новое TCP соединение
   - Меньше overhead на handshake

4. **Компактный формат**
   - Имена полей заменены на номера (1, 2, 3)
   - Меньше трафика

## Запуск

### Запуск сервера:
```bash
cd ~/Code/Network-Software/weeks/week-08/starter
python service.py
```

### Запуск бенчмарка:
```bash
cd ~/Code/Network-Software/weeks/week-08
python starter/bench.py
```

## Проверка

```bash
cd ~/Code/Network-Software
STUDENT_ID=s15 GROUP=331 python -m pytest -q weeks/week-08/tests
```

Результат: Все тесты пройдены

## Ответы на вопросы

### 1. Что такое Server Streaming? Приведите пример использования.

**Server Streaming** — режим gRPC, когда клиент отправляет один запрос, а сервер возвращает поток ответов.

**Примеры:**
- **Лента новостей:** клиент подписывается, сервер шлёт новые посты по мере появления
- **Логи:** клиент запрашивает логи, сервер стримит их построчно
- **Биржевые котировки:** клиент подписывается на акцию, сервер шлёт обновления цен
- **Прогресс загрузки:** сервер отправляет проценты выполнения

**В .proto:**
```protobuf
rpc SubscribeToOrders (SubscribeRequest) returns (stream OrderUpdate);
```

**В коде:**
```python
def SubscribeToOrders(self, request, context):
    for order in orders:
        yield OrderUpdate(...)  # Каждый yield = одно сообщение
```

### 2. Чем Server Streaming отличается от получения большого списка?

**Получение списка (Unary):**
```protobuf
rpc GetOrders (GetOrdersRequest) returns (GetOrdersResponse);

message GetOrdersResponse {
    repeated Order orders = 1;  // Все заказы в одном сообщении
}
```
- Сервер собирает **все** данные в память
- Отправляет **одно большое** сообщение
- Клиент ждёт, пока всё загрузится
- Проблема: если данных много, может не хватить памяти

**Server Streaming:**
```protobuf
rpc SubscribeToOrders (SubscribeRequest) returns (stream OrderUpdate);
```
- Сервер отправляет данные **по частям**
- Клиент начинает обрабатывать **сразу** (не ждёт конца)
- Меньше нагрузка на память
- Можно стримить бесконечно (логи, котировки)

**Аналогия:**
- Список: скачать весь фильм, потом смотреть
- Streaming: смотреть фильм во время загрузки (как Netflix)

### 3. Какие метрики производительности существуют?

**1. Latency (Задержка)**
- Время от отправки запроса до получения первого байта ответа
- Измеряется в миллисекундах (ms)
- Важно для интерактивных приложений

**2. Throughput (Пропускная способность)**
- Количество запросов в секунду (RPS — Requests Per Second)
- Или количество данных в секунду (MB/s)
- Важно для высоконагруженных систем

**3. CPU Usage (Использование процессора)**
- Сколько процессорного времени тратится на обработку
- JSON парсинг тратит больше CPU, чем Protobuf

**4. Memory Usage (Использование памяти)**
- Сколько памяти занимают данные
- Важно для больших объёмов данных

**5. Network Bandwidth (Пропускная способность сети)**
- Сколько трафика передаётся
- Protobuf компактнее JSON

**В нашем бенчмарке:**
- Latency: 0.22 мс на запрос
- Throughput: 4515.83 RPS

### 4. Почему важно переиспользовать канал (Channel) в gRPC?

**Channel** — это соединение с сервером. Создание канала дорого:
- Установка TCP соединения (handshake)
- TLS handshake (если используется шифрование)
- HTTP/2 настройка

**Плохо (создаём канал каждый раз):**
```python
for i in range(1000):
    channel = grpc.insecure_channel('localhost:50051')  # Медленно!
    stub = MyServiceStub(channel)
    stub.MyMethod(request)
    channel.close()
```
- 1000 TCP handshakes
- Очень медленно

**Хорошо (переиспользуем канал):**
```python
with grpc.insecure_channel('localhost:50051') as channel:
    stub = MyServiceStub(channel)
    for i in range(1000):
        stub.MyMethod(request)  # Быстро!
```
- 1 TCP handshake
- Все запросы через одно соединение
- HTTP/2 мультиплексирование

**В бенчмарках:**
Если не переиспользовать канал, результаты будут неправильными — мы будем мерить время создания соединения, а не время обработки запроса.

### 5. В каких сценариях REST может быть быстрее или удобнее gRPC?

**REST удобнее когда:**

1. **Публичное API**
   - Браузеры понимают HTTP/JSON из коробки
   - Можно тестировать через curl, Postman
   - Не нужна кодогенерация

2. **Простые CRUD операции**
   - GET /users, POST /users — интуитивно понятно
   - Не нужна сложная инфраструктура

3. **Кэширование**
   - HTTP кэш работает на уровне URL
   - CDN, браузерный кэш, прокси
   - В gRPC всё на `/graphql` — кэш не работает

4. **Отладка**
   - JSON легко читать
   - Можно смотреть в браузере, логах
   - Protobuf — бинарный формат, нужны специальные инструменты

5. **Маленькие данные**
   - Если данных мало, разница в производительности незаметна
   - Overhead на Protobuf может быть больше, чем выигрыш

**gRPC удобнее когда:**
- Микросервисы (сервис-сервис)
- Большой объём данных
- Нужна максимальная производительность
- Streaming (реалтайм)
- Строгая типизация

### 6. Что такое Head-of-Line Blocking? Как HTTP/2 решает это?

**Head-of-Line Blocking** — проблема HTTP/1.1:

**HTTP/1.1:**
- Одно TCP соединение = один запрос за раз
- Если первый запрос медленный, остальные ждут

```
Запрос 1: [========медленный========] (5 сек)
Запрос 2:                              [быстрый] (ждёт 5 сек!)
Запрос 3:                                        [быстрый] (ждёт ещё!)
```

**Решение в HTTP/1.1:**
- Открыть несколько соединений (обычно 6)
- Но это дорого (много TCP handshakes)

**HTTP/2 решение:**
- **Мультиплексирование:** много запросов в одном соединении
- Каждый запрос = отдельный **stream** с ID
- Запросы не блокируют друг друга

```
Соединение:
  Stream 1: [========медленный========]
  Stream 2: [быстрый]  (не ждёт!)
  Stream 3:   [быстрый]  (не ждёт!)
```

**В gRPC:**
- Использует HTTP/2
- Все RPC вызовы идут параллельно
- Один медленный запрос не блокирует остальные

**Пример:**
```python
# Все три запроса идут параллельно
response1 = stub.SlowMethod(request1)   # 5 секунд
response2 = stub.FastMethod(request2)   # 0.1 секунда (не ждёт!)
response3 = stub.FastMethod(request3)   # 0.1 секунда (не ждёт!)
```

## Типы RPC в gRPC

1. **Unary RPC** (как в лабе 7)
   - 1 запрос → 1 ответ
   - `rpc CreateOrder (Request) returns (Response);`

2. **Server Streaming** (эта лаба)
   - 1 запрос → N ответов
   - `rpc Subscribe (Request) returns (stream Response);`

3. **Client Streaming**
   - N запросов → 1 ответ
   - `rpc Upload (stream Request) returns (Response);`

4. **Bidirectional Streaming**
   - N запросов ↔ N ответов
   - `rpc Chat (stream Request) returns (stream Response);`
