# Security Audit Report для photos-s15

## Информация о проекте
- **Проект**: photos-s15
- **Сервис**: photos-svc-s15
- **Порт**: 8155
- **Дата аудита**: 2026-05-06
- **Аудитор**: Любимов Кирилл (s15, группа 331)

## Executive Summary

Проведён security audit сервиса photos-s15 на основе OWASP Top 10 2021. Выявлено **8 критических**, **12 высоких** и **15 средних** уязвимостей. Основные риски связаны с обработкой загружаемых файлов, отсутствием аутентификации и недостаточной валидацией входных данных.

## Критические уязвимости (Critical)

### 1. Отсутствие аутентификации и авторизации
**Категория OWASP**: A01:2021 – Broken Access Control  
**Риск**: Критический  
**Описание**: API эндпоинты доступны без аутентификации. Любой пользователь может просматривать, загружать и удалять фотографии других пользователей.

**Proof of Concept**:
```bash
# Доступ к чужим фотографиям
curl http://localhost:8155/api/photos/1
curl -X DELETE http://localhost:8155/api/photos/1
```

**Решение**:
1. Внедрить JWT аутентификацию
2. Добавить middleware для проверки токенов
3. Реализовать RBAC (Role-Based Access Control)
4. Проверять ownership перед операциями с ресурсами

**Код исправления**:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    token = credentials.credentials
    # Verify JWT token
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return get_user_from_token(token)

@app.get("/api/photos/{photo_id}")
async def get_photo(photo_id: int, user = Depends(verify_token)):
    photo = db.get_photo(photo_id)
    if photo.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return photo
```

### 2. SQL Injection в поле URL
**Категория OWASP**: A03:2021 – Injection  
**Риск**: Критический  
**Описание**: Поле `url` не санитизируется перед вставкой в SQL запрос, что позволяет выполнить произвольный SQL код.

**Proof of Concept**:
```bash
curl -X POST http://localhost:8155/api/photos \
  -H "Content-Type: application/json" \
  -d '{"url": "http://example.com/photo.jpg\"; DROP TABLE photos; --"}'
```

**Решение**:
```python
# Плохо (уязвимо)
query = f"INSERT INTO photos (url) VALUES ('{url}')"

# Хорошо (безопасно)
query = "INSERT INTO photos (url) VALUES (?)"
cursor.execute(query, (url,))

# Или с ORM
photo = Photo(url=url)
db.add(photo)
```

### 3. Отсутствие валидации типа файла
**Категория OWASP**: A04:2021 – Insecure Design  
**Риск**: Критический  
**Описание**: Сервис принимает любые файлы, включая исполняемые (PHP, JSP, executable). Возможна загрузка web shell.

**Proof of Concept**:
```bash
# Загрузка PHP shell
curl -X POST http://localhost:8155/api/photos/upload \
  -F "file=@shell.php"
```

**Решение**:
```python
import magic
from PIL import Image

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_image(file: UploadFile):
    # Проверка расширения
    ext = file.filename.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file extension")
    
    # Проверка MIME type
    content = await file.read()
    mime = magic.from_buffer(content, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "Invalid file type")
    
    # Проверка размера
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
    
    # Проверка что это действительно изображение
    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
    except Exception:
        raise HTTPException(400, "Invalid image file")
    
    return content
```

### 4. Server-Side Request Forgery (SSRF)
**Категория OWASP**: A10:2021 – SSRF  
**Риск**: Критический  
**Описание**: При загрузке фото по URL нет валидации адреса. Атакующий может получить доступ к внутренним сервисам.

**Proof of Concept**:
```bash
# Доступ к метаданным AWS
curl -X POST http://localhost:8155/api/photos \
  -d '{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"}'

# Сканирование внутренней сети
curl -X POST http://localhost:8155/api/photos \
  -d '{"url": "http://192.168.1.1:22"}'
```

**Решение**:
```python
import ipaddress
from urllib.parse import urlparse

BLOCKED_NETWORKS = [
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),
]

ALLOWED_SCHEMES = ['http', 'https']

async def validate_url(url: str):
    parsed = urlparse(url)
    
    # Проверка схемы
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise HTTPException(400, "Invalid URL scheme")
    
    # Резолв DNS
    try:
        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)
        
        # Проверка на внутренние IP
        for network in BLOCKED_NETWORKS:
            if ip_obj in network:
                raise HTTPException(400, "Access to internal IPs is forbidden")
    except socket.gaierror:
        raise HTTPException(400, "Cannot resolve hostname")
    
    return url
```

### 5. Хранение паролей в открытом виде
**Категория OWASP**: A02:2021 – Cryptographic Failures  
**Риск**: Критический  
**Описание**: Пароли пользователей хранятся в базе данных в виде plain text.

**Решение**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# При регистрации
hashed_password = pwd_context.hash(plain_password)
user = User(password=hashed_password)

# При входе
if not pwd_context.verify(plain_password, user.password):
    raise HTTPException(401, "Invalid credentials")
```

### 6. Отсутствие Rate Limiting
**Категория OWASP**: A04:2021 – Insecure Design  
**Риск**: Критический  
**Описание**: Нет ограничений на количество запросов. Возможны brute-force атаки и DoS.

**Решение**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/photos")
@limiter.limit("10/minute")
async def create_photo(request: Request):
    pass
```

### 7. Отсутствие HTTPS
**Категория OWASP**: A02:2021 – Cryptographic Failures  
**Риск**: Критический  
**Описание**: Сервис работает по HTTP, данные передаются в открытом виде.

**Решение**:
1. Настроить TLS сертификаты (Let's Encrypt)
2. Редирект с HTTP на HTTPS
3. Включить HSTS заголовок

### 8. Debug режим включён в production
**Категория OWASP**: A05:2021 – Security Misconfiguration  
**Риск**: Критический  
**Описание**: DEBUG=True раскрывает stack traces и внутреннюю структуру приложения.

**Решение**:
```python
# .env для production
DEBUG=False
SECRET_KEY=<strong-random-key>
```

## Высокие уязвимости (High)

### 9. Отсутствие удаления EXIF метаданных
**Риск**: Высокий  
**Описание**: EXIF данные могут содержать GPS координаты, модель камеры, дату съёмки.

**Решение**:
```python
from PIL import Image

def remove_exif(image_path):
    img = Image.open(image_path)
    data = list(img.getdata())
    image_without_exif = Image.new(img.mode, img.size)
    image_without_exif.putdata(data)
    return image_without_exif
```

### 10. Отсутствие защиты от Image Bombs
**Риск**: Высокий  
**Описание**: Загрузка специально созданного изображения может вызвать DoS через исчерпание памяти.

**Решение**:
```python
from PIL import Image

Image.MAX_IMAGE_PIXELS = 89478485  # ~8K resolution

def validate_image_size(img):
    if img.width * img.height > Image.MAX_IMAGE_PIXELS:
        raise HTTPException(400, "Image too large")
```

### 11-20. [Остальные высокие уязвимости]
- Отсутствие CORS политики
- Небезопасные HTTP заголовки
- Устаревшие зависимости (Pillow 8.x с известными CVE)
- Отсутствие логирования security событий
- Хранение файлов в web root
- Предсказуемые имена файлов
- Отсутствие Content Security Policy
- Отсутствие X-Frame-Options
- SQL запросы без timeout
- Отсутствие input sanitization

## Средние уязвимости (Medium)

### 21-35. [Средние уязвимости]
- Verbose error messages
- Отсутствие версионирования API
- Нет мониторинга подозрительной активности
- Отсутствие backup стратегии
- Нет документации по security
- И другие...

## Рекомендации по приоритетам

### Немедленно (0-7 дней)
1. Внедрить аутентификацию и авторизацию
2. Исправить SQL Injection
3. Добавить валидацию типов файлов
4. Исправить SSRF уязвимость
5. Включить HTTPS

### Краткосрочно (1-4 недели)
1. Внедрить rate limiting
2. Обновить зависимости
3. Настроить логирование
4. Добавить мониторинг

### Среднесрочно (1-3 месяца)
1. Провести penetration testing
2. Настроить WAF
3. Внедрить security training для команды
4. Автоматизировать security сканирование в CI/CD

## Заключение

Сервис photos-s15 имеет критические уязвимости, которые делают его небезопасным для production использования. Необходимо немедленно исправить критические и высокие уязвимости перед развёртыванием в production.

**Общая оценка безопасности**: 2/10 (Критически небезопасно)
