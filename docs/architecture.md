[← Configuration](configuration.md) · [Back to README](../README.md) · [Testing →](testing.md)

# Architecture

## Рабочая архитектура

Проект реализован как Flask modular monolith. Это один web-сервис, который рендерит HTML через Jinja, хранит пользователей и настройки в PostgreSQL и переиспользует legacy-модули первой части как интеграционные адаптеры.

## Ключевые слои

| Слой | Ответственность |
|------|-----------------|
| `app/*/routes.py` | HTTP, формы, redirects, flash messages |
| `app/services/*` | orchestration и бизнес-flow |
| `app/models/*` | SQLAlchemy модели |
| `generators/`, `social_publishers/`, `social_stats/` | legacy integration layer |

## Текущая структура

```text
.
|- app/
|  |- auth/
|  |- main/
|  |- settings/
|  |- content/
|  |- stats/
|  |- models/
|  |- services/
|  `- templates/
|- generators/
|- social_publishers/
|- social_stats/
|- docker/
|- migrations/
|- tests/
|- Dockerfile
|- docker-compose.yml
`- wsgi.py
```

## Важные решения

1. Flask app factory в `app/__init__.py`.
2. SQLAlchemy + PostgreSQL как основной persistence layer.
3. Flask-Login для сессий.
4. Flask-WTF для форм и CSRF.
5. Bootstrap через CDN без кастомного CSS.

## VK integration boundary

- генерация текста и изображения не зависит от успешности VK posting;
- VK publishing выполняется best-effort;
- если VK token не имеет нужных прав, пользователь все равно получает сгенерированный контент;
- subscriber count берется через `groups.getById(fields=members_count)` с fallback на `groups.getMembers`.

## Почему не microservices

Для учебного MVP с Flask, auth, PostgreSQL и Docker отдельные сервисы только усложнили бы разработку и деплой. Нужная граница здесь внутренняя: routes -> services -> models/integrations.

## See Also

- [Configuration](configuration.md) — env-модель приложения.
- [Testing](testing.md) — что и как проверять.
- [Security](security.md) — ограничения VK token и секретов.
