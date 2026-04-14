# group_finance

Стартовый Django-проект для внутренней системы управленческого учета группы компаний.

## Стек

- Python 3.12+
- Django 5+
- PostgreSQL
- Docker / Docker Compose

## Структура

- `src`-layout для Python-кода
- настройки разделены на:
  - `group_finance.settings.base`
  - `group_finance.settings.dev`
  - `group_finance.settings.prod`
- приложения:
  - `core`
  - `org`
  - `people`
  - `imports`
  - `banking`
  - `worklog`
  - `payroll`
  - `expenses`
  - `revenue`
  - `analytics`

## Быстрый старт

1. Скопируйте пример env:

   ```bash
   cp .env.example .env
   ```

2. Поднимите проект:

   ```bash
   docker compose up --build
   ```

3. Откройте сервис:

   - приложение: http://localhost:8000/
   - healthcheck: http://localhost:8000/health/
   - admin: http://localhost:8000/admin/

## Переменные окружения

- `DJANGO_SETTINGS_MODULE` - модуль настроек Django
- `DJANGO_SECRET_KEY` - секретный ключ
- `DJANGO_DEBUG` - режим отладки
- `DJANGO_ALLOWED_HOSTS` - список хостов через запятую
- `POSTGRES_DB` - имя базы
- `POSTGRES_USER` - пользователь PostgreSQL
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `POSTGRES_HOST` - хост PostgreSQL
- `POSTGRES_PORT` - порт PostgreSQL

## Локальный запуск без Docker

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```
