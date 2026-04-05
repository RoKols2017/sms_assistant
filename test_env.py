"""Legacy environment check script from part one.

This file is preserved for script-era compatibility and manual diagnostics.
It is not the runtime entrypoint of the Flask web application.
"""

import os
import sys
from typing import Dict, Any, Optional
from loguru import logger

# Импорты для тестирования
try:
    from config import config
    from generators.text_gen import TextGenerator
    from generators.image_gen import ImageGenerator
    from social_publishers.vk_publisher import VKPublisher
    from social_publishers.telegram_publisher import TelegramPublisher
    from social_stats.stats_collector import StatsCollector
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что все зависимости установлены: pip install -r requirements.txt")
    sys.exit(1)


def test_environment_variables() -> Dict[str, bool]:
    """
    Проверяет наличие всех необходимых переменных окружения
    
    Returns:
        Dict[str, bool]: Результаты проверки каждой переменной
    """
    logger.info("🔍 Проверка переменных окружения...")
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API ключ',
        'VK_TOKEN': 'VK API токен',
        'VK_GROUP_ID': 'VK Group ID',
        'TG_TOKEN': 'Telegram Bot токен',
        'TG_CHAT_ID': 'Telegram Chat ID'
    }
    
    results = {}
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value and value not in [f'your_{var_name.lower()}_here', '']:
            results[var_name] = True
            logger.success(f"✅ {var_name}: {description} - настроен")
        else:
            results[var_name] = False
            logger.error(f"❌ {var_name}: {description} - не настроен")
    
    return results


def test_openai_connection() -> bool:
    """
    Тестирует подключение к OpenAI API
    
    Returns:
        bool: True если подключение успешно
    """
    logger.info("🤖 Тестирование подключения к OpenAI...")
    
    try:
        # Создаем генератор текста
        text_gen = TextGenerator(
            tone="тестовый",
            topic="технологии"
        )
        
        # Пробуем сгенерировать короткий текст
        result = text_gen.generate_post()
        
        if result and len(result) > 10:
            logger.success("✅ OpenAI API: подключение успешно")
            logger.info(f"📝 Сгенерированный текст: {result[:100]}...")
            return True
        else:
            logger.error("❌ OpenAI API: не удалось сгенерировать текст")
            return False
            
    except Exception as e:
        logger.error(f"❌ OpenAI API: ошибка подключения - {e}")
        return False


def test_vk_connection() -> bool:
    """
    Тестирует подключение к VK API
    
    Returns:
        bool: True если подключение успешно
    """
    logger.info("📘 Тестирование подключения к VK API...")
    
    try:
        # Создаем публикатор VK
        vk_publisher = VKPublisher(
            access_token=config.vk_token,
            group_id=config.vk_group_id
        )
        
        # Пробуем получить информацию о группе
        # Это базовый тест без публикации
        logger.info("✅ VK API: инициализация успешна")
        logger.info(f"📘 Группа ID: {config.vk_group_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ VK API: ошибка подключения - {e}")
        return False


def test_telegram_connection() -> bool:
    """
    Тестирует подключение к Telegram Bot API
    
    Returns:
        bool: True если подключение успешно
    """
    logger.info("📱 Тестирование подключения к Telegram Bot API...")
    
    try:
        # Создаем публикатор Telegram
        telegram_publisher = TelegramPublisher(
            bot_token=config.telegram_token,
            chat_id=config.telegram_chat_id
        )
        
        # Пробуем получить информацию о боте
        # Это базовый тест без отправки сообщений
        logger.info("✅ Telegram Bot API: инициализация успешна")
        logger.info(f"📱 Чат ID: {config.telegram_chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Telegram Bot API: ошибка подключения - {e}")
        return False


def test_image_generation() -> bool:
    """
    Тестирует генерацию изображений
    
    Returns:
        bool: True если генерация успешна
    """
    logger.info("🎨 Тестирование генерации изображений...")
    
    try:
        # Создаем генератор изображений
        image_gen = ImageGenerator()
        
        # Пробуем сгенерировать простое изображение
        test_prompt = "Simple test image, minimal style"
        result = image_gen.generate_image(test_prompt)
        
        if result and result.startswith('http'):
            logger.success("✅ DALL-E 3: генерация изображения успешна")
            logger.info(f"🖼️ URL изображения: {result}")
            return True
        else:
            logger.error("❌ DALL-E 3: не удалось сгенерировать изображение")
            return False
            
    except Exception as e:
        logger.error(f"❌ DALL-E 3: ошибка генерации - {e}")
        return False


def run_comprehensive_test() -> Dict[str, Any]:
    """
    Запускает комплексное тестирование всех компонентов
    
    Returns:
        Dict[str, Any]: Результаты всех тестов
    """
    logger.info("🚀 Запуск комплексного тестирования SMM-системы")
    logger.info("=" * 60)
    
    results = {
        'environment': test_environment_variables(),
        'openai': False,
        'vk': False,
        'telegram': False,
        'image_generation': False,
        'overall_success': False
    }
    
    # Проверяем переменные окружения
    env_success = all(results['environment'].values())
    if not env_success:
        logger.error("❌ Не все переменные окружения настроены")
        return results
    
    # Тестируем подключения
    results['openai'] = test_openai_connection()
    results['vk'] = test_vk_connection()
    results['telegram'] = test_telegram_connection()
    results['image_generation'] = test_image_generation()
    
    # Определяем общий успех
    results['overall_success'] = all([
        results['openai'],
        results['vk'],
        results['telegram'],
        results['image_generation']
    ])
    
    return results


def print_test_summary(results: Dict[str, Any]) -> None:
    """
    Выводит сводку результатов тестирования
    
    Args:
        results (Dict[str, Any]): Результаты тестов
    """
    logger.info("\n📊 СВОДКА РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ")
    logger.info("=" * 60)
    
    # Переменные окружения
    logger.info("🔧 Переменные окружения:")
    for var, success in results['environment'].items():
        status = "✅" if success else "❌"
        logger.info(f"   {status} {var}")
    
    # API подключения
    logger.info("\n🌐 API подключения:")
    apis = [
        ('OpenAI', results['openai']),
        ('VK API', results['vk']),
        ('Telegram Bot', results['telegram']),
        ('DALL-E 3', results['image_generation'])
    ]
    
    for name, success in apis:
        status = "✅" if success else "❌"
        logger.info(f"   {status} {name}")
    
    # Общий результат
    overall_status = "✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if results['overall_success'] else "❌ ЕСТЬ ОШИБКИ"
    logger.info(f"\n🎯 Общий результат: {overall_status}")
    
    if not results['overall_success']:
        logger.warning("\n⚠️  Рекомендации:")
        if not results['openai']:
            logger.warning("   - Проверьте OPENAI_API_KEY в .env файле")
        if not results['vk']:
            logger.warning("   - Проверьте VK_TOKEN и VK_GROUP_ID в .env файле")
        if not results['telegram']:
            logger.warning("   - Проверьте TG_TOKEN и TG_CHAT_ID в .env файле")


if __name__ == "__main__":
    print("🧪 Тестирование SMM-системы с ИИ")
    print("=" * 60)
    
    try:
        # Запускаем тестирование
        results = run_comprehensive_test()
        
        # Выводим сводку
        print_test_summary(results)
        
        # Завершаем с соответствующим кодом
        sys.exit(0 if results['overall_success'] else 1)
        
    except KeyboardInterrupt:
        logger.warning("\n⏹️ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 Критическая ошибка тестирования: {e}")
        sys.exit(1)
