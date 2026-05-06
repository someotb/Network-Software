# Лабораторная работа №9: WebRTC и P2P коммуникация

**Студент:** Любимов Кирилл Алексеевич (s15)  
**Группа:** 331  
**Проект:** products-s15

## Описание

Реализация P2P (peer-to-peer) чата через WebRTC. Браузеры общаются напрямую друг с другом, без передачи данных через сервер.

## Что такое WebRTC?

**WebRTC** (Web Real-Time Communication) — технология для прямой связи между браузерами:
- Видеочаты (Zoom, Google Meet)
- Передача файлов
- Онлайн-игры
- Стриминг

**Преимущества P2P:**
- Низкая задержка (нет промежуточного сервера)
- Меньше нагрузка на сервер
- Больше приватности

## Реализация

### 1. Signaling Server (starter/signaling.py)

WebSocket сервер для обмена техническими данными (SDP, ICE candidates):

```python
PROJECT_CODE = "products-s15"
CONNECTIONS = set()

async def handler(websocket):
    CONNECTIONS.add(websocket)
    try:
        async for message in websocket:
            for conn in CONNECTIONS:
                if conn != websocket:
                    await conn.send(message)
    finally:
        CONNECTIONS.remove(websocket)
```

**Зачем нужен signaling сервер?**
- WebRTC нужен для прямой связи, но сначала браузеры должны "познакомиться"
- Обмениваются SDP (описание соединения) и ICE candidates (сетевые адреса)
- После установки соединения данные идут напрямую P2P

### 2. WebRTC Client (client/index.html)

JavaScript код с использованием `RTCPeerConnection` и Data Channel.

**Основные компоненты:**
- `RTCPeerConnection` — P2P соединение
- `createDataChannel('chat')` — канал для текстовых сообщений
- STUN сервер — помогает узнать публичный IP

## Запуск

**Терминал 1 (signaling сервер):**
```bash
cd ~/Code/Network-Software/weeks/week-09/starter
python signaling.py
```

**Браузер:**
Открой `client/index.html` в двух вкладках — они соединятся P2P!

## Проверка

```bash
cd ~/Code/Network-Software
STUDENT_ID=s15 GROUP=331 python -m pytest -q weeks/week-09/tests
```

Результат: Все тесты пройдены

## Ключевые концепции

**SDP (Session Description Protocol)** — описание медиа-потоков и кодеков  
**ICE (Interactive Connectivity Establishment)** — поиск пути для соединения  
**STUN** — сервер для определения публичного IP  
**Data Channel** — канал для передачи произвольных данных
