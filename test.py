"""Legacy demo script from part one.

This file is not the Flask runtime entrypoint for the web application.
Use `wsgi.py` / Docker Compose for the web app and keep this file only as
an integration-style helper for the original script-based workflow.
"""

import os
import sys
from typing import Optional, Dict, Any
from loguru import logger

# Импорты всех созданных классов
from config import config
from generators.text_gen import TextGenerator
from generators.image_gen import ImageGenerator
from social_publishers.vk_publisher import VKPublisher
from social_publishers.telegram_publisher import TelegramPublisher
from social_stats.stats_collector import StatsCollector


def main():
    """
    Основная функция демонстрации работы SMM-системы
    """
    logger.info("🚀 Запуск демонстрации SMM-системы с ИИ")
    logger.info("=" * 50)
    
    # Конфигурация из переменных окружения
    demo_config = {
        'topic': 'технологии',
        'tone': 'дружелюбный'
    }
    
    try:
        # Шаг 1: Генерация текста поста
        logger.info("📝 Шаг 1: Генерация текста поста...")
        text_generator = TextGenerator(
            tone=demo_config['tone'],
            topic=demo_config['topic'],
            model="gpt-5"  # Используем актуальную модель
        )
        
        post_text = text_generator.generate_post()
        if not post_text:
            logger.error("❌ Не удалось сгенерировать текст поста")
            return
        
        logger.success(f"✅ Текст поста сгенерирован:")
        logger.info(f"📄 {post_text}")
        
        # Шаг 2: Генерация изображения
        logger.info("🎨 Шаг 2: Генерация изображения...")
        image_generator = ImageGenerator(model="dall-e-3")  # Используем актуальную модель
        
        # Создаем промпт для изображения на основе темы
        image_prompt = f"Современные технологии, {demo_config['topic']}, стиль минимализм, высокое качество"
        image_url = image_generator.generate_image(image_prompt)
        
        if not image_url:
            logger.warning("❌ Не удалось сгенерировать изображение")
            logger.info("📄 Продолжаем с текстовым постом...")
            image_url = None
        else:
            logger.success(f"✅ Изображение сгенерировано:")
            logger.info(f"🖼️ {image_url}")
        
        # Шаг 3: Публикация в социальных сетях
        logger.info("📱 Шаг 3: Публикация в социальных сетях...")
        
        published_posts = {}
        
        # Публикация в VK
        try:
            logger.info("📘 Публикация в ВКонтакте...")
            vk_publisher = VKPublisher(
                access_token=config.vk_token,
                group_id=config.vk_group_id
            )
            
            vk_result = vk_publisher.publish_post(post_text, image_url)
            if vk_result:
                published_posts['vk'] = {
                    'post_id': vk_result.get('post_id'),
                    'group_id': config.vk_group_id
                }
                logger.success(f"✅ Пост опубликован в ВК! ID: {vk_result.get('post_id')}")
            else:
                logger.error("❌ Не удалось опубликовать в ВК")
        except Exception as e:
            logger.error(f"❌ Ошибка при публикации в ВК: {e}")
        
        # Публикация в Telegram
        try:
            logger.info("📱 Публикация в Telegram...")
            telegram_publisher = TelegramPublisher(
                bot_token=config.telegram_token,
                chat_id=config.telegram_chat_id
            )
            
            telegram_result = telegram_publisher.send_post(post_text, image_url)
            if telegram_result:
                published_posts['telegram'] = {
                    'message_id': telegram_result.get('message_id'),
                    'chat_id': config.telegram_chat_id
                }
                logger.success(f"✅ Пост отправлен в Telegram! ID: {telegram_result.get('message_id')}")
            else:
                logger.error("❌ Не удалось отправить в Telegram")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке в Telegram: {e}")
        
        # Шаг 4: Сбор статистики
        logger.info("📊 Шаг 4: Сбор статистики...")
        
        try:
            stats_collector = StatsCollector(
                vk_access_token=config.vk_token,
                telegram_bot_token=config.telegram_token
            )
            
            # Собираем статистику для опубликованных постов
            if 'vk' in published_posts:
                logger.info("📘 Получение статистики ВК...")
                vk_stats = stats_collector.get_vk_stats(
                    post_id=published_posts['vk']['post_id'],
                    group_id=published_posts['vk']['group_id']
                )
                if vk_stats:
                    logger.success(f"📊 Статистика ВК:")
                    logger.info(f"   👍 Лайки: {vk_stats.get('likes', 0)}")
                    logger.info(f"   🔄 Репосты: {vk_stats.get('reposts', 0)}")
                    logger.info(f"   💬 Комментарии: {vk_stats.get('comments', 0)}")
                    logger.info(f"   👁️ Просмотры: {vk_stats.get('views', 0)}")
                else:
                    logger.error("❌ Не удалось получить статистику ВК")
            
            if 'telegram' in published_posts:
                logger.info("📱 Получение статистики Telegram...")
                telegram_stats = stats_collector.get_telegram_stats(
                    message_id=published_posts['telegram']['message_id'],
                    chat_id=published_posts['telegram']['chat_id']
                )
                if telegram_stats:
                    logger.success(f"📊 Статистика Telegram:")
                    logger.info(f"   👥 Участников: {telegram_stats.get('member_count', 0)}")
                    logger.info(f"   📺 Тип чата: {telegram_stats.get('chat_type', 'Unknown')}")
                    logger.info(f"   📈 Охват: {telegram_stats.get('estimated_reach', 0)}")
                else:
                    logger.error("❌ Не удалось получить статистику Telegram")
        
        except Exception as e:
            logger.error(f"❌ Ошибка при сборе статистики: {e}")
        
        # Итоговый отчет
        logger.success("🎉 Демонстрация завершена!")
        logger.info("=" * 50)
        logger.info(f"📝 Тема поста: {demo_config['topic']}")
        logger.info(f"🎭 Тон: {demo_config['tone']}")
        logger.info(f"📄 Текст: {post_text[:100]}...")
        if image_url:
            logger.info(f"🖼️ Изображение: {image_url}")
        logger.info(f"📱 Опубликовано в: {', '.join(published_posts.keys())}")
        
    except KeyboardInterrupt:
        logger.warning("⏹️ Демонстрация прервана пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


def test_individual_modules():
    """
    Тестирование отдельных модулей
    """
    print("\n🧪 Тестирование отдельных модулей...")
    
    # Тест генератора текста
    try:
        print("📝 Тест TextGenerator...")
        text_gen = TextGenerator("дружелюбный", "тест", "test-key", "gpt-5")
        print("✅ TextGenerator инициализирован")
    except Exception as e:
        print(f"❌ Ошибка TextGenerator: {e}")
    
    # Тест генератора изображений
    try:
        print("🎨 Тест ImageGenerator...")
        image_gen = ImageGenerator("test-key", "dall-e-3")
        print("✅ ImageGenerator инициализирован")
    except Exception as e:
        print(f"❌ Ошибка ImageGenerator: {e}")
    
    # Тест публикаторов
    try:
        print("📘 Тест VKPublisher...")
        vk_pub = VKPublisher("test-token", 123456)
        print("✅ VKPublisher инициализирован")
    except Exception as e:
        print(f"❌ Ошибка VKPublisher: {e}")
    
    try:
        print("📱 Тест TelegramPublisher...")
        tg_pub = TelegramPublisher("test-token", "@test")
        print("✅ TelegramPublisher инициализирован")
    except Exception as e:
        print(f"❌ Ошибка TelegramPublisher: {e}")
    
    # Тест сборщика статистики
    try:
        print("📊 Тест StatsCollector...")
        stats = StatsCollector("test-token", "test-token")
        print("✅ StatsCollector инициализирован")
    except Exception as e:
        print(f"❌ Ошибка StatsCollector: {e}")


if __name__ == "__main__":
    logger.info("🤖 SMM-система с ИИ - Демонстрация")
    logger.info("=" * 50)
    logger.warning("⚠️  Внимание: Для полной работы укажите реальные API ключи в .env файле:")
    logger.info("   - OPENAI_API_KEY")
    logger.info("   - VK_TOKEN")
    logger.info("   - VK_GROUP_ID")
    logger.info("   - TG_TOKEN")
    logger.info("   - TG_CHAT_ID")
    logger.info("=" * 50)
    
    # Тестирование модулей
    test_individual_modules()
    
    # Основная демонстрация
    main()
