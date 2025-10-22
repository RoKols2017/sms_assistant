# 🤖 SMM-система с ИИ

Автоматизированная система для создания и публикации контента в социальных сетях с использованием искусственного интеллекта.

## 🚀 Возможности

- **Генерация текста** - создание SMM-постов с помощью GPT-5 (ChatGPT-5)
- **Генерация изображений** - создание визуального контента с помощью DALL-E 3
- **Публикация в VK** - автоматическая публикация в ВКонтакте
- **Публикация в Telegram** - отправка сообщений в Telegram каналы
- **Сбор статистики** - мониторинг метрик и аналитика
- **Безопасность** - защищенная работа с API ключами

## 📋 Требования

- Python 3.8+
- OpenAI API ключ
- VK API токен
- Telegram Bot токен

## 🛠️ Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd PE7.2
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте переменные окружения:**
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами
```

4. **Проверьте конфигурацию:**
```bash
python test_env.py
```

## 🔧 Конфигурация

Создайте файл `.env` в корне проекта:

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_key_here

# VK API
VK_TOKEN=your_vk_token_here
VK_GROUP_ID=your_vk_group_id_here

# Telegram Bot API
TG_TOKEN=your_telegram_token_here
TG_CHAT_ID=your_telegram_chat_id_here

# Дополнительные настройки
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=30

# Модели OpenAI (опционально)
OPENAI_TEXT_MODEL=gpt-5
OPENAI_IMAGE_MODEL=dall-e-3
```

## 🚀 Использование

### Быстрый старт

```bash
python test.py
```

### Программное использование

```python
from generators.text_gen import TextGenerator
from generators.image_gen import ImageGenerator
from social_publishers.vk_publisher import VKPublisher
from social_publishers.telegram_publisher import TelegramPublisher

# Генерация контента
text_gen = TextGenerator(tone="дружелюбный", topic="технологии", model="gpt-5")
post_text = text_gen.generate_post()

image_gen = ImageGenerator(model="dall-e-3")
image_url = image_gen.generate_image("Современные технологии")

# Публикация
vk_publisher = VKPublisher(access_token="your_token", group_id=123456)
vk_publisher.publish_post(post_text, image_url)

telegram_publisher = TelegramPublisher(bot_token="your_token", chat_id="@channel")
telegram_publisher.send_post(post_text, image_url)
```

## 📁 Структура проекта

```
PE7.2/
├── .cursor/
│   └── rules/
│       └── project-rules.md
├── generators/
│   ├── text_gen.py          # Генерация текста
│   └── image_gen.py         # Генерация изображений
├── social_publishers/
│   ├── vk_publisher.py      # Публикация в VK
│   └── telegram_publisher.py # Публикация в Telegram
├── social_stats/
│   └── stats_collector.py   # Сбор статистики
├── config.py                # Конфигурация
├── test.py                  # Демонстрация
├── test_env.py             # Тестирование окружения
├── requirements.txt        # Зависимости
├── .env                    # Переменные окружения
├── .gitignore             # Игнорируемые файлы
├── SECURITY.md            # Безопасность
└── README.md              # Документация
```

## 🔒 Безопасность

- ✅ API ключи хранятся в переменных окружения
- ✅ Файл `.env` исключен из Git
- ✅ Валидация входных данных
- ✅ Логирование без секретных данных
- ✅ Обработка ошибок API

**⚠️ Важно:** Никогда не коммитьте файл `.env` в репозиторий!

## 🧪 Тестирование

### Проверка конфигурации
```bash
python test_env.py
```

### Тестирование модулей
```bash
python generators/text_gen.py
python generators/image_gen.py
python social_publishers/vk_publisher.py
python social_publishers/telegram_publisher.py
python social_stats/stats_collector.py
```

### Полная демонстрация
```bash
python test.py
```

## 🤖 Поддерживаемые модели

### OpenAI GPT модели:
- **GPT-5** (ChatGPT-5) - основная модель для генерации текста
- **GPT-4o** - альтернативная модель (устаревшая)
- **GPT-4o-mini** - быстрая модель для простых задач
- **GPT-4-turbo** - мощная модель для сложных задач
- **GPT-3.5-turbo** - экономичная модель

### OpenAI DALL-E модели:
- **DALL-E 3** - основная модель для генерации изображений
- **DALL-E 2** - альтернативная модель (устаревшая)

## 📊 Логирование

Логи сохраняются в папке `logs/`:
- `smm_system.log` - основные логи системы
- Ротация: ежедневно
- Хранение: 30 дней

## 🛠️ Разработка

### Установка для разработки
```bash
pip install -r requirements.txt
pip install -e .
```

### Запуск тестов
```bash
# Полное тестирование с покрытием кода
python run_tests.py

# Или напрямую через pytest
python -m pytest tests/ --cov=. --cov-report=html --cov-fail-under=80

# Конкретные тесты
python run_tests.py --specific
```

### Линтинг
```bash
flake8 .
black .
```

## 📈 Мониторинг

Система автоматически отслеживает:
- Успешность API запросов
- Время выполнения операций
- Ошибки и исключения
- Использование ресурсов

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте файл `.env`
2. Запустите `python test_env.py`
3. Проверьте логи в `logs/`
4. Создайте issue в репозитории

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🔄 Обновления

Для обновления системы:
```bash
git pull origin main
pip install -r requirements.txt
python test_env.py
```

---

**Создано с ❤️ для автоматизации SMM-процессов**
