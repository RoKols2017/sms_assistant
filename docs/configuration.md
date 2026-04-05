[← Getting Started](getting-started.md) · [Back to README](../README.md) · [Architecture →](architecture.md)

# Configuration

## Основные env-переменные

| Переменная | Назначение |
|------------|------------|
| `FLASK_ENV` | Режим Flask (`development`/`production`) |
| `FLASK_SECRET_KEY` | Секретный ключ сессий и CSRF |
| `DATABASE_URL` | Строка подключения SQLAlchemy/PostgreSQL |
| `OPENAI_API_KEY` | Ключ OpenAI |
| `OPENAI_TEXT_MODEL` | Модель генерации текста |
| `OPENAI_IMAGE_MODEL` | Модель генерации изображений |
| `LOG_LEVEL` | Уровень логирования |
| `TIMEOUT` | Таймаут внешних запросов |
| `MAX_RETRIES` | Повторы интеграционных операций |
| `VK_API_VERSION` | Зафиксированная версия VK API |

## PostgreSQL в Docker Compose

| Переменная | Назначение |
|------------|------------|
| `POSTGRES_DB` | Имя базы данных |
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |

## Пример `.env`

```bash
FLASK_ENV=production
FLASK_SECRET_KEY=change-me-to-a-long-random-secret
POSTGRES_DB=sms_assistant
POSTGRES_USER=sms_assistant
POSTGRES_PASSWORD=change-me-db-password
DATABASE_URL=postgresql://sms_assistant:change-me-db-password@postgres:5432/sms_assistant
OPENAI_API_KEY=your_openai_key
LOG_LEVEL=INFO
TIMEOUT=30
MAX_RETRIES=3
VK_API_VERSION=5.139
OPENAI_TEXT_MODEL=gpt-5
OPENAI_IMAGE_MODEL=dall-e-3
```

## Legacy compatibility

В `.env.example` сохранены пустые `VK_TOKEN`, `VK_GROUP_ID`, `TG_TOKEN`, `TG_CHAT_ID` для совместимости со старым demo-кодом первой части. Для нового Flask MVP основными являются пользовательские настройки, которые вводятся через web UI и сохраняются в PostgreSQL.

## VK settings на пользователя

Через страницу `Settings` пользователь сохраняет:

- `vk_api_key`
- `vk_group_id`

Дополнительно приложение хранит метаданные последней проверки подключения и capability status.

## Обязательные production-требования

- `FLASK_SECRET_KEY` должен быть задан явно;
- приложение не должно запускаться в production без корректного `DATABASE_URL`;
- миграции применяются через `flask db upgrade` в контейнере `web`.

## See Also

- [Getting Started](getting-started.md) — запуск через Docker Compose.
- [Security](security.md) — как обращаться с токенами и secret key.
- [Architecture](architecture.md) — где конфиг используется в приложении.
