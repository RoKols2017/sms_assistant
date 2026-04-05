[Back to README](../README.md) · [Configuration →](configuration.md)

# Getting Started

## Требования

| Что | Зачем |
|-----|-------|
| Docker + Docker Compose | Основной способ запуска |
| OpenAI API key | Генерация текста и изображений |
| VK user token | VK settings и автопостинг |

## Локальный запуск

```bash
cp .env.example .env
docker compose up --build
```

После старта:

1. Откройте `http://localhost:8000`.
2. Зарегистрируйте пользователя.
3. Войдите в dashboard.
4. Заполните `VK settings`.
5. Перейдите на страницу генерации поста.

## Запуск на VPS

```bash
git clone <repository-url>
cd sms_assistant
cp .env.example .env
docker compose up -d --build
```

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

## Первичная проверка

- открывается страница логина;
- регистрация сохраняет пользователя в PostgreSQL;
- dashboard доступен после входа;
- settings сохраняют `vk_api_key` и `vk_group_id`.

## See Also

- [Configuration](configuration.md) — все env-переменные и `DATABASE_URL`.
- [Architecture](architecture.md) — как устроен Flask app factory.
- [Security](security.md) — ограничения VK token и правила работы с секретами.
