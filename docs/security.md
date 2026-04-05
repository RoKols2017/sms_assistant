[← Testing](testing.md) · [Back to README](../README.md)

# Security

## Базовые правила

| Нельзя | Нужно |
|--------|-------|
| Коммитить `.env` | Хранить секреты только в env |
| Логировать пароли и токены | Логировать только технический контекст |
| Хардкодить `FLASK_SECRET_KEY` | Задавать длинный случайный secret через env |
| Хранить пароли пользователей в plaintext | Хранить только hash |

## Что считается секретом

- `FLASK_SECRET_KEY`
- `OPENAI_API_KEY`
- `POSTGRES_PASSWORD`
- пользовательский `vk_api_key`

## VK token caveat

По актуальной документации VK:

- `wall.post` требует пользовательский token;
- `photos.getWallUploadServer` требует пользовательский token и право `photos`;
- методы публикации на стену не гарантированы для каждого token.

Поэтому безопасность и UX в проекте устроены так:

1. token сохраняется для конкретного пользователя;
2. приложение валидирует базовую доступность группы;
3. автопостинг считается optional capability;
4. ошибка VK не должна терять уже сгенерированный контент.

## Пароли и сессии

- используется hash-хранение паролей;
- Flask session cookies помечены как `HttpOnly`;
- формы защищены CSRF через Flask-WTF.

## Что проверить на VPS

- выставлен уникальный `FLASK_SECRET_KEY`;
- `.env` не попадает в Git и backups без шифрования;
- доступ к VPS ограничен;
- Docker logs не содержат raw token values.

## See Also

- [Configuration](configuration.md) — переменные окружения.
- [Getting Started](getting-started.md) — запуск в Docker.
- [Architecture](architecture.md) — как разделены web layer и integrations.
