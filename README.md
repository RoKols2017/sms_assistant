# SMM Assistant

> Flask-приложение для генерации SMM-постов, изображений и автопубликации в VK с хранением пользователей в PostgreSQL.

Проект превращает первую часть учебного репозитория в веб-приложение: регистрация и вход, пользовательские VK-настройки, генерация контента через OpenAI и базовая VK-статистика в одном Docker-ready сервисе.

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

После запуска приложение доступно на `http://localhost:8000`.

## Что умеет MVP

- **Регистрация и вход**: обычная сессионная auth на Flask.
- **Пользовательские VK settings**: хранение token и group id в PostgreSQL.
- **Генерация поста**: `tone`, `topic`, генерация текста и изображения.
- **Автопостинг в VK**: выполняется best-effort и не ломает генерацию при отказе VK.
- **VK Stats**: минимум число подписчиков группы.

## Docker Compose на VPS

```bash
cp .env.example .env
docker compose up -d --build
docker compose logs -f web
```

## Важная оговорка по VK

Автопостинг в VK зависит от прав конкретного пользовательского token. По актуальной документации VK методы публикации на стену и загрузки wall photo требуют специальные права `wall` и `photos`, которые доступны не для каждого сценария. Если VK не разрешает публикацию, приложение все равно вернет сгенерированный текст и изображение, а пользователю покажет предупреждение.

## Документация

| Руководство | Описание |
|-------------|----------|
| [Getting Started](docs/getting-started.md) | Локальный запуск и первый вход |
| [Configuration](docs/configuration.md) | Env-переменные Flask, OpenAI и Postgres |
| [Architecture](docs/architecture.md) | Структура Flask modular monolith |
| [Testing](docs/testing.md) | Тесты, smoke-check и статические проверки |
| [Security](docs/security.md) | Секреты, пароли и ограничения VK token |

## Ключевые файлы

- `wsgi.py` — WSGI entrypoint для Gunicorn.
- `app/__init__.py` — Flask app factory.
- `docker-compose.yml` — web + postgres.
- `docker/entrypoint.sh` — ожидание БД и запуск `flask db upgrade`.

## Лицензия

MIT License.
