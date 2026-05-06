# Лабораторная работа №7: gRPC сервис

**Студент:** Любимов Кирилл Алексеевич (s15)  
**Группа:** 331  
**Ресурс:** tickets (тикеты/заявки)  
**Дополнительное поле:** status (статус)  
**Сервис:** TicketsService  
**Package:** tickets.v1  

## Описание задания

Реализовать gRPC сервис для работы с тикетами. Сервис должен поддерживать:
- Создание нового тикета (CreateTicket)
- Получение списка всех тикетов (GetTickets)

## Что такое gRPC?

**gRPC** (Google Remote Procedure Call) — это система удалённого вызова процедур. В отличие от REST, где мы делаем HTTP запросы с JSON, в gRPC мы вызываем функции на удалённом сервере, как будто они локальные.

**Ключевые отличия от REST:**
- REST: текстовый JSON, HTTP методы (GET/POST/PUT/DELETE)
- gRPC: бинарные данные (Protocol Buffers), вызовы функций (RPC)

**Преимущества gRPC:**
- Быстрее (бинарная сериализация вместо текста)
- Меньше трафика (компактный формат)
- Строгая типизация (контракт в .proto файле)
- Автоматическая генерация клиентов для разных языков

## Реализация

### 1. Protocol Buffers схема (proto/service.proto)

```protobuf
syntax = "proto3";

package tickets.v1;

service TicketsService {
    rpc CreateTicket (CreateTicketRequest) returns (CreateTicketResponse);
    rpc GetTickets (GetTicketsRequest) returns (GetTicketsResponse);
}

message CreateTicketRequest {
    string text = 1;
    string status = 2;
}

message CreateTicketResponse {
    string id = 1;
    string text = 2;
    string status = 3;
}

message GetTicketsRequest {}

message GetTicketsResponse {
    repeated Ticket tickets = 1;
}

message Ticket {
    string id = 1;
    string text = 2;
    string status = 3;
}
```

**Структура .proto файла:**
- `syntax = "proto3"` — версия Protocol Buffers
- `package tickets.v1` — пространство имён
- `service TicketsService` — описание сервиса с методами
- `rpc CreateTicket (...)` — метод (как функция)
- `message` — структура данных (как класс)
- Цифры (1, 2, 3) — номера полей для бинарного формата (не значения!)

**Важно про номера полей:**
- Начинаются с 1 (не с 0)
- Нельзя менять после релиза (для обратной совместимости)
- Используются в бинарном формате вместо имён полей

### 2. Генерация кода

Из .proto файла генерируем Python код:

```bash
cd ~/Code/Network-Software/weeks/week-07
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/service.proto
```

**Что делает команда:**
- `python -m grpc_tools.protoc` — запускает компилятор protobuf
- `-I.` — где искать .proto файлы (текущая директория)
- `--python_out=.` — куда генерировать код для сообщений (message)
- `--grpc_python_out=.` — куда генерировать код для gRPC сервиса
- `proto/service.proto` — путь к .proto файлу

**Результат:**
- `proto/service_pb2.py` — классы для данных (Ticket, CreateTicketRequest, etc.)
- `proto/service_pb2_grpc.py` — классы для сервера и клиента

### 3. Реализация сервера (starter/service.py)

```python
import grpc
from concurrent import futures
import sys
sys.path.append("proto")
import service_pb2
import service_pb2_grpc

tickets_db = []

class TicketsServiceServicer(service_pb2_grpc.TicketsServiceServicer):
    def CreateTicket(self, request, context):
        # Создаём новый тикет
        new_ticket = service_pb2.Ticket(
            id=str(len(tickets_db) + 1),
            text=request.text,
            status=request.status
        )
        # Добавляем в базу
        tickets_db.append(new_ticket)
        # Возвращаем Response
        return service_pb2.CreateTicketResponse(
            id=new_ticket.id,
            text=new_ticket.text,
            status=new_ticket.status
        )

    def GetTickets(self, request, context):
        # Возвращаем все тикеты
        return service_pb2.GetTicketsResponse(tickets=tickets_db)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_TicketsServiceServicer_to_server(
        TicketsServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

**Логика работы:**

1. **CreateTicket:**
   - Получаем `request` (CreateTicketRequest) с полями `text` и `status`
   - Создаём объект `Ticket` с уникальным `id`
   - Сохраняем в `tickets_db`
   - Возвращаем `CreateTicketResponse`

2. **GetTickets:**
   - Возвращаем `GetTicketsResponse` со списком всех тикетов из `tickets_db`

3. **serve():**
   - Создаём gRPC сервер
   - Регистрируем наш сервис
   - Запускаем на порту 50051

## Запуск

```bash
cd ~/Code/Network-Software/weeks/week-07/starter
python service.py
```

Сервер будет слушать на `localhost:50051`

## Проверка

```bash
cd ~/Code/Network-Software
STUDENT_ID=s15 GROUP=331 python -m pytest -q weeks/week-07/tests
```

Результат: Все тесты пройдены

## Ответы на вопросы

### 1. Зачем нужен файл .proto? Почему не писать классы сразу на Python?

**Причины:**
- **Кроссплатформенность:** Один .proto файл генерирует код для Python, Go, Java, C++, JavaScript
- **Контракт:** .proto — это строгий контракт между клиентом и сервером
- **Обратная совместимость:** Protobuf гарантирует, что старые клиенты будут работать с новыми серверами
- **Оптимизация:** Компилятор генерирует эффективный код для сериализации

Если писать классы вручную на Python, другие команды (на Go, Java) не смогут автоматически создать клиент.

### 2. Что такое Unary RPC? Чем он похож на REST?

**Unary RPC** — самый простой тип взаимодействия в gRPC:
- Клиент отправляет **один** запрос
- Сервер возвращает **один** ответ

**Похож на REST:**
- REST: `POST /tickets` → получаем ответ
- gRPC: `CreateTicket(request)` → получаем response

**Отличия:**
- REST: HTTP запрос с JSON
- gRPC: вызов функции с бинарными данными

Есть и другие типы RPC:
- **Server streaming:** клиент отправляет один запрос, сервер возвращает поток ответов
- **Client streaming:** клиент отправляет поток запросов, сервер возвращает один ответ
- **Bidirectional streaming:** оба отправляют потоки

### 3. Почему gRPC эффективнее REST (JSON)?

**По процессору:**
- JSON: нужно парсить текст, преобразовывать строки в числа
- Protobuf: бинарный формат, данные уже в нужном виде

**По трафику:**
- JSON: `{"id": 123, "text": "Hello", "status": "open"}` — 45 байт
- Protobuf: `[1: 123, 2: "Hello", 3: "open"]` — примерно 15 байт (передаём номера полей, а не имена)

**Пример:**
- REST: имена полей передаются каждый раз
- gRPC: имена полей заменены на номера (1, 2, 3)

### 4. Что такое обратная совместимость? Зачем номера полей?

**Обратная совместимость** — старые клиенты работают с новыми серверами (и наоборот).

**Пример:**

Версия 1:
```protobuf
message Ticket {
    string id = 1;
    string text = 2;
}
```

Версия 2 (добавили поле):
```protobuf
message Ticket {
    string id = 1;
    string text = 2;
    string status = 3;  // Новое поле
}
```

**Что происходит:**
- Старый клиент отправляет только поля 1 и 2 → новый сервер понимает
- Новый сервер отправляет поля 1, 2, 3 → старый клиент игнорирует поле 3

**Правила:**
- Нельзя менять номера существующих полей
- Нельзя удалять обязательные поля
- Можно добавлять новые поля с новыми номерами

### 5. Что такое Stub и Servicer?

**Servicer (сервер):**
- Класс, который **реализует** методы сервиса
- Наследуется от сгенерированного базового класса
- Содержит бизнес-логику

```python
class TicketsServiceServicer(service_pb2_grpc.TicketsServiceServicer):
    def CreateTicket(self, request, context):
        # Логика создания тикета
        return response
```

**Stub (клиент):**
- Сгенерированный класс для **вызова** методов сервиса
- Выглядит как обычный Python объект
- Автоматически упаковывает данные и отправляет по сети

```python
channel = grpc.insecure_channel('localhost:50051')
stub = service_pb2_grpc.TicketsServiceStub(channel)
response = stub.CreateTicket(request)  # Вызов как обычной функции
```

### 6. Когда выбрать REST, а когда gRPC?

**Выбирай REST когда:**
- Публичное API (браузеры, curl, Postman)
- Простые CRUD операции
- Нужна читаемость (JSON легко читать)
- Клиенты на разных платформах без кодогенерации
- Кэширование на уровне HTTP (CDN, браузер)

**Выбирай gRPC когда:**
- Микросервисы внутри компании (сервис-сервис)
- Нужна максимальная производительность
- Большой объём данных (streaming)
- Строгая типизация контрактов
- Клиенты на разных языках (автогенерация кода)
- Реалтайм коммуникация (bidirectional streaming)

**Пример:**
- REST: мобильное приложение → публичное API
- gRPC: микросервис авторизации → микросервис заказов

## Ключевые концепции

### Protocol Buffers (Protobuf)

Язык описания данных (IDL — Interface Definition Language):
- Описываем структуру один раз в .proto
- Генерируем код для любого языка
- Бинарная сериализация (быстро и компактно)

### Типы данных в Protobuf

- `string` — строка
- `int32`, `int64` — целые числа
- `float`, `double` — числа с плавающей точкой
- `bool` — булево значение
- `repeated` — массив (список)
- `message` — вложенная структура

### Генерация кода

Из одного .proto файла генерируются:
- `_pb2.py` — классы для данных (message)
- `_pb2_grpc.py` — классы для сервера (Servicer) и клиента (Stub)

Эти файлы автоматически сгенерированы, их не нужно редактировать вручную.
