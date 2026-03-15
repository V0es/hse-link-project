# Запуск проекта
Необходимы Docker и Docker Compose
1. **Клонирование репозитория**
```bash
# via https
git clone https://github.com/V0es/hse-link-project.git

# via ssh
git clone git@github.com:V0es/hse-link-project.git

cd hse-link-project
```
2. **Создание `.env` (например, из `.env.example`)**:
```bash
DATABASE__HOST = 'postgres'
DATABASE__PORT = 5432
DATABASE__USER = 'postgres'
DATABASE__PASSWORD = 'postgres'
DATABASE__NAME = 'postgres'

CACHE__HOST = 'redis'
CACHE__PORT = 6379
CACHE__DB_NUM = 0
CACHE__LINK_PREFIX = 'link'
CACHE__CLICKS_PREFIX = 'clicks'
CACHE__TTL = 3600

CELERY__BROKER_ENGINE = 'redis'
CELERY__BROKER_HOST = 'redis'
CELERY__BROKER_PORT = 6379
CELERY__BROKER_DB = 1

APP__LINK_UNUSED_THRESHOLD_DAYS = 5
```

3. **Создание ключей для JWT**:

- Генерируем приватный ключ:
```bash
# Генерация приватного RSA ключа длины 2048
openssl genrsa -out certs/jwt-private.pem 2048 
```

- Генерируем публичный ключ на основе приватного:
```bash
# Выделяем публичный ключ из пары для сертификата
openssl rsa -in certs/jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

4. **Запуск**
```bash
docker compose up --build
```


# Описание API
## Auth
### Регистрация
```bash
POST /auth/register
```
Тело запроса:
```json
{
  "username": "user1",
  "password": "password123"
}
```
Ответ:
```json
{
  "message": "Registered successfully"
}
```
Ошибки:
`409 User already exists`

### Логин
```bash
POST /auth/login
```
Тело запроса:
```json
{
  "username": "user1",
  "password": "password123"
}
```
Ответ:
```json
{
  "message": "Logged in successfully"
}
```
Куки:
`access_token=<jwt>`
Ошибки:
`403 Incorrect credentials`

## Links
### Создание короткой ссылки
```bash
POST /links/shorten
```
Тело запроса:
```json
{
  "long_url": "https://google.com",
  "expires_at": "2026-01-01T00:00:00",
  "custom_alias": "google"
}
```
Ответ:
```json
{
  "slug": "google",
  "long_url": "https://google.com",
  "expires_at": "2026-01-01T00:00:00"
}
```
Ошибки:
`400 Alias already exists`

Если `custom_alias` не указан - генерируется случайный slug

### Редирект по ссылке
```bash
GET /links/{short_code}
```

Ответ: `302 Redirect`
Ошибки:
- `404 Alias not found`
- `410 Link has expired`

При переходе:
 - увеличивается счётчик переходов в Redis
 - обновляется `last_used_at` в Redis


### Удаление ссылки
```bash
DELETE /links/{short_code}
```

Поддерживается удаление только ссылок, созданных данным пользователем

Ответ:
```json
{
  "message": "link deleted successfully"
}
```

Ошибки:
- `404 Alias not found`
- `403 Not authorized`

### Обновление ссылки
```bash
PUT /links/{short_code}
```
Тело запроса:
```json
{
  "long_url": "https://newsite.com",
  "expires_at": "2026-02-01T00:00:00"
}
```
Ответ:
```json
{
  "slug": "example",
  "long_url": "https://newsite.com",
  "expires_at": "2026-02-01T00:00:00"
}
```

При обновлении происходит также обновление ссылки в кэше Redis

### Получение статистики
```bash
GET /links/{short_code}/stats
```

Пользователь может получать только статистику созданных им ссылок 

Ответ:
```json
{
  "slug": "example",
  "redirects": 124,
  "last_used_at": "2026-02-01T10:20:00"
}
```

Приоисходит сбор редиректов и из БД, и из кэша

# Сбор статистика
Обновления в Redis кэше при редиректе:
 1. Увеличивается счётчик переходов
 2. Обновляется дата последнего перехода по ссылке

Celery задача `sync_stats` раз в 1 минуту переносит статистику из Redis в PostgreSQL

# Удаление неиспользуемых ссылок
Celery задача `flush_abandoned_links` удаляет ссылки из БД, если с последнего перехода прошло `N` дней, где `N`:
```bash
N = $(APP__LINK_UNUSED_THRESHOLD_DAYS) # environment variable
```

# Структура БД
## Таблица Users
- id: integer
- username: string - _index_
- password_hash: string
## Таблица Links
- id: integer
- slug: string - _index_
- long_url: string
- user_id: integer
- redirects: integer
- created_at: datetime
- expires_at: datetime
- last_used_at: datetime - _index_

# Redis
Хранит:
 - Кэш ссылок: `link:{slug} - <long_url>`
 - Число переходов по ссылке: `clicks:{slug} - <redirects_num>`
 - Время последнего перехода: `last_used:{slug} - <last_used_datetime>`

# Celery
Выполнение периодических задач с планировщиком `Beat` \
Задачи:
- `flush_abandoned_links`
    - Удаляет ссылки, по которым не было переходов `N` дней
    - Удаляет информацию об этой ссылки из кэша
- `sync_stats`
    - Переносит статистику ссылки (`redirects`, `last_used`) из кэша в БД
    - Обновляет статистику в кэше
