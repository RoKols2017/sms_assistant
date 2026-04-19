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

- `wall.post` и связанные сценарии надежнее всего работают с пользовательским token;
- `photos.getWallUploadServer` требует не только право `photos`, но и подходящий тип авторизации;
- `group/community token` не равен `user access token`, даже если кажется, что список прав похожий;
- методы публикации на стену не гарантированы для каждого token.

Практически важный кейс для этого проекта:

1. `group token` может пройти проверку группы;
2. текстовый пост может частично работать;
3. но загрузка изображения на стену упадет с ошибкой вроде:
`[27] Group authorization failed: method is unavailable with group auth.`

Это не ошибка генерации изображения и не проблема OpenAI. Это признак того, что для wall photo upload используется неправильный тип VK-токена.

Поэтому безопасность и UX в проекте устроены так:

1. token сохраняется для конкретного пользователя;
2. приложение валидирует базовую доступность группы;
3. автопостинг считается optional capability;
4. ошибка VK не должна терять уже сгенерированный контент.

## Пароли и сессии

- используется hash-хранение паролей;
- Flask session cookies помечены как `HttpOnly`;
- в production session и remember cookies должны оставаться `Secure` и уходить только по HTTPS;
- для reverse proxy необходимо явно настраивать `TRUST_PROXY_COUNT`, чтобы Flask корректно понимал `https`-scheme и не строил небезопасные redirect URL;
- формы защищены CSRF через Flask-WTF.

## Что проверить на VPS

- выставлен уникальный `FLASK_SECRET_KEY`;
- проверено, что proxy передаёт `X-Forwarded-Proto` и приложение запускается с корректным `TRUST_PROXY_COUNT`;
- session cookie в браузере имеет флаги `Secure`, `HttpOnly`, `SameSite` согласно production-политике;
- `.env` не попадает в Git и backups без шифрования;
- доступ к VPS ограничен;
- Docker logs не содержат raw token values.

## See Also

- [Configuration](configuration.md) — переменные окружения.
- [VK Integration](vk-integration.md) — подробное объяснение VK токенов и прав.
- [Getting Started](getting-started.md) — запуск в Docker.
- [Architecture](architecture.md) — как разделены web layer и integrations.
