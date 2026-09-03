# AI-ассистент команды — мини-дашборд

FastAPI-бэкенд + простой HTML/JS-фронт для общения с Claude и хранения истории последних запросов в Postgres.

## Запуск

1. Скопируйте `.env.example` в `.env` и впишите свой ключ:

   ```bash
   cp .env.example .env
   ```

   Откройте `.env` и замените `ANTHROPIC_API_KEY=sk-ant-your-key-here` на реальный ключ Anthropic. При желании также поменяйте `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`.

2. Поднимите оба сервиса одной командой:

   ```bash
   docker-compose up --build
   ```

   `backend` дождётся, пока Postgres пройдёт healthcheck, и только потом стартует.

3. Откройте дашборд: http://localhost:8000

## Что где

- `POST /ask` — принимает `{"question": "..."}`, вызывает Anthropic API (модель `claude-sonnet-4-6`), сохраняет пару вопрос/ответ в Postgres и возвращает её.
- `GET /history` — последние 5 записей из таблицы `messages`, отсортированные по дате (новые первыми).
- `GET /health/api-key` — делает минимальный запрос к Anthropic API (`max_tokens=1`) и возвращает `{"status": "valid" | "invalid" | "expired" | "error"}`. Статус также отображается бейджем в правом верхнем углу дашборда.
- Статические файлы фронта лежат в `static/` (`index.html`, `app.js`, `style.css`) — без сборки, чистый HTML/JS, markdown рендерится в браузере через `marked` + `DOMPurify` (CDN).

## Структура бэкенда

- `main.py` — FastAPI-приложение и роуты.
- `models.py` — SQLAlchemy-модель `Message`.
- `schemas.py` — Pydantic-схемы запросов/ответов.
- `anthropic_client.py` — вызовы Anthropic API через `httpx`.
- `database.py` — async-движок SQLAlchemy (asyncpg) и `init_db()`, который делает `create_all` при старте приложения (без Alembic — таблица создаётся автоматически).

## Логи

```bash
docker-compose logs -f backend
docker-compose logs -f postgres
```

## Остановка

```bash
docker-compose down
```

Данные Postgres хранятся в volume `postgres_data` и переживают `docker-compose down` (без `-v`).

## Локальный запуск без Docker (опционально)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Поднимите Postgres любым способом и укажите строку подключения:
export DATABASE_URL=postgresql+asyncpg://ai_asist:ai_asist@localhost:5432/ai_asist
export ANTHROPIC_API_KEY=sk-ant-...

uvicorn main:app --reload
```
