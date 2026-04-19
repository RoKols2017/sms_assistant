[Back to README](../README.md) · [Configuration →](configuration.md)

# Getting Started

## Требования

| Что | Зачем |
|-----|-------|
| Docker + Docker Compose | Основной способ запуска |
| OpenAI API key | Генерация текста и изображений |
| VK user token | Настройка VK и публикация постов с изображением |

## Локальный запуск

```bash
docker compose up --build
```

Для локальной разработки `.env` больше не обязателен: compose подставит dev-defaults. Если хотите управлять секретами и параметрами явно, создайте `.env` из `.env.example` и переопределите значения там.

После старта:

1. Откройте `http://localhost:8000`.
2. Зарегистрируйте пользователя.
3. Войдите в dashboard.
4. Заполните `VK settings`.
5. Перейдите на страницу генерации поста.

Важно: в `VK settings` вставляйте именно `user access token`. Если вставить `ключ сообщества`, текстовая публикация может частично работать, но загрузка изображения на стену обычно будет недоступна.

## Запуск на VPS

```bash
git clone <repository-url>
cd sms_assistant
cp .env.example .env
docker compose up -d --build
```

Для production перед запуском:

1. заполните `FLASK_SECRET_KEY` и `DATABASE_URL`;
2. если есть reverse proxy, задайте `TRUST_PROXY_COUNT` и оставьте `PREFERRED_URL_SCHEME=https`;
3. убедитесь, что proxy прокидывает `X-Forwarded-Proto`;
4. при необходимости добавьте `OPENAI_API_KEY`, но отсутствие OpenAI/VK/Telegram не должно ломать сам boot приложения.

Полезные команды:

```bash
docker compose logs -f web
docker compose logs -f postgres
docker compose ps
```

## Что делает bootstrap

При старте `web` контейнера:

1. entrypoint ждет готовности PostgreSQL;
2. выполняет `flask --app wsgi.py db upgrade`;
3. запускает Gunicorn на `0.0.0.0:8000`.
4. Docker healthcheck проверяет `http://127.0.0.1:8000/healthz`.

Ожидаемые логи при нормальном старте:

- `[entrypoint] waiting for database availability`
- `[entrypoint] database ready target=...`
- `[entrypoint] database migrations finished`
- `[entrypoint] starting gunicorn bind=... workers=...`
- `[main.healthz] completed extra=...`

## Первичная проверка

- открывается страница логина;
- `curl http://localhost:8000/healthz` возвращает JSON со `status` и `critical_checks`;
- регистрация сохраняет пользователя в PostgreSQL;
- dashboard доступен после входа;
- settings сохраняют `vk_api_key` и `vk_group_id`.

## Короткий checklist для первого deploy

1. `docker compose ps` показывает `postgres` и `web` в состоянии `healthy`.
2. `docker compose logs -f web` не содержит ошибок про secret key, БД или миграции.
3. `/healthz` возвращает `200 OK`; `optional_providers` могут быть `not_configured` без падения сервиса.
4. Login page открывается по реальному HTTPS-URL через ваш proxy.
5. Session cookie в браузере имеет `Secure` и `HttpOnly` в production.

## See Also

- [Configuration](configuration.md) — все env-переменные и `DATABASE_URL`.
- [VK Integration](vk-integration.md) — какой VK токен нужен и почему.
- [Architecture](architecture.md) — как устроен Flask app factory.
- [Security](security.md) — ограничения VK token и правила работы с секретами.
