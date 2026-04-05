[← Architecture](architecture.md) · [Back to README](../README.md) · [Security →](security.md)

# Testing

## Что проверяется

- app factory и регистрация routes;
- регистрация/логин пользователя;
- сохранение VK settings;
- content workflow и graceful degradation при проблемах VK.

## Тесты

```bash
python -m pytest tests/ -v
```

## Статическая проверка синтаксиса

```bash
python -m compileall app config.py generators social_publishers social_stats
```

## Docker smoke-check

После настройки окружения:

```bash
docker compose up --build
docker compose logs -f web
```

Дополнительно проверьте, что в логах `web` есть успешный `db upgrade`, а не откат на bootstrap-режим.

## Текущее ограничение локального окружения агента

В текущем рабочем окружении системный Python был без `pip`, поэтому во время этой сессии полноценный runtime-прогон Flask/pytest локально не выполнялся. Для проекта это компенсируется Docker-сценарием, который устанавливает зависимости внутри контейнера.

## See Also

- [Getting Started](getting-started.md) — основной запуск.
- [Configuration](configuration.md) — env-переменные для тестового и Docker запуска.
- [Architecture](architecture.md) — какие слои покрываются тестами.
