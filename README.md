# AI Assistant Dashboard

Небольшой сервис для команды: пишете вопрос — получаете ответ от Claude в удобном виде. Последние обращения сохраняются рядом.

## Что внутри

- FastAPI + async SQLAlchemy + Postgres
- Anthropic API (Claude) для генерации ответов
- Простой фронт на HTML/JS, без сборки
- Всё поднимается в Docker одной командой

## Быстрый старт

1. Скопируйте конфиг:

   ```bash
   cp .env.example .env
   ```

2. Пропишите свои значения в `.env`:

   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-...
   POSTGRES_USER=ai_asist
   POSTGRES_PASSWORD=ai_asist
   POSTGRES_DB=ai_asist
   ```

   Ключ можно получить в [Anthropic Console](https://console.anthropic.com/settings/keys). При создании выбирайте тип **Not linked (legacy key)** — обычный сервисный ключ.

3. Поднимите контейнеры:

   ```bash
   docker-compose up -d --build
   ```

4. Откройте:

   - Дашборд — http://localhost:8000
   - Схема API — http://localhost:8000/docs

## Как понять, что всё живо

Сверху справа появится зелёная метка "ключ валиден" — значит ключ рабочий и сервис на связи. Дальше можно печатать вопрос и жать кнопку.

## Остановить

```bash
docker-compose down
```

Данные в базе остаются между запусками. Если нужно стереть всё начисто:

```bash
docker-compose down -v
```

## Если что-то пошло не так

```bash
docker-compose logs -f backend
```
