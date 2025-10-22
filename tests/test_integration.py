"""
Интеграционные тесты
"""

import pytest
from unittest.mock import patch, MagicMock
from generators.text_gen import TextGenerator
from generators.image_gen import ImageGenerator
from social_publishers.vk_publisher import VKPublisher
from social_publishers.telegram_publisher import TelegramPublisher
from social_stats.stats_collector import StatsCollector


class TestIntegration:
    """Интеграционные тесты системы"""
    
    @pytest.mark.integration
    def test_full_workflow_simulation(self):
        """Тест полного рабочего процесса"""
        with patch('generators.text_gen.openai.OpenAI') as mock_openai_text, \
             patch('generators.image_gen.openai.OpenAI') as mock_openai_image, \
             patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api, \
             patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot, \
             patch('social_stats.stats_collector.vk_api.VkApi') as mock_vk_stats, \
             patch('social_stats.stats_collector.telebot.TeleBot') as mock_tg_stats:
            
            # Настройка моков для генерации текста
            mock_text_client = MagicMock()
            mock_text_response = MagicMock()
            mock_text_response.choices = [MagicMock()]
            mock_text_response.choices[0].message.content = "Тестовый пост о технологиях"
            mock_text_client.chat.completions.create.return_value = mock_text_response
            mock_openai_text.return_value = mock_text_client
            
            # Настройка моков для генерации изображения
            mock_image_client = MagicMock()
            mock_image_response = MagicMock()
            mock_image_response.data = [MagicMock()]
            mock_image_response.data[0].url = "https://example.com/image.jpg"
            mock_image_client.images.generate.return_value = mock_image_response
            mock_openai_image.return_value = mock_image_client
            
            # Настройка моков для VK
            mock_vk_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.post.return_value = {'post_id': 123}
            mock_vk_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_vk_session
            
            # Настройка моков для Telegram
            mock_bot = MagicMock()
            mock_message = MagicMock()
            mock_message.message_id = 456
            mock_message.chat.id = 789
            mock_message.text = "Тестовый пост о технологиях"
            mock_bot.send_message.return_value = mock_message
            mock_telebot.return_value = mock_bot
            
            # Настройка моков для статистики
            mock_vk_stats_session = MagicMock()
            mock_vk_stats_api = MagicMock()
            mock_vk_stats_api.wall.getById.return_value = [{
                'likes': {'count': 10},
                'reposts': {'count': 5},
                'comments': {'count': 3},
                'views': {'count': 100},
                'text': 'Тестовый пост о технологиях',
                'date': 1234567890
            }]
            mock_vk_stats_session.get_api.return_value = mock_vk_stats_api
            mock_vk_stats.return_value = mock_vk_stats_session
            
            mock_tg_bot = MagicMock()
            mock_tg_chat = MagicMock()
            mock_tg_chat.title = "Test Channel"
            mock_tg_chat.type = "channel"
            mock_tg_bot.get_chat.return_value = mock_tg_chat
            mock_tg_bot.get_chat_member_count.return_value = 1000
            mock_tg_stats.return_value = mock_tg_bot
            
            # Выполнение полного процесса
            # 1. Генерация текста
            text_gen = TextGenerator(
                tone="дружелюбный",
                topic="технологии",
                model="gpt-5"
            )
            post_text = text_gen.generate_post()
            assert post_text == "Тестовый пост о технологиях"
            
            # 2. Генерация изображения
            image_gen = ImageGenerator(model="dall-e-3")
            image_url = image_gen.generate_image("Современные технологии")
            assert image_url == "https://example.com/image.jpg"
            
            # 3. Публикация в VK
            vk_publisher = VKPublisher(
                access_token="test-token",
                group_id=123456
            )
            vk_result = vk_publisher.publish_post(post_text, image_url)
            assert vk_result == {'post_id': 123}
            
            # 4. Публикация в Telegram
            tg_publisher = TelegramPublisher(
                bot_token="test-token",
                chat_id="@test_channel"
            )
            tg_result = tg_publisher.send_post(post_text, image_url)
            assert tg_result['message_id'] == 456
            
            # 5. Сбор статистики
            stats_collector = StatsCollector(
                vk_access_token="test-token",
                telegram_bot_token="test-token"
            )
            
            vk_stats = stats_collector.get_vk_stats(123, 123456)
            assert vk_stats['likes'] == 10
            
            tg_stats = stats_collector.get_telegram_stats(456, "@test_channel")
            assert tg_stats['member_count'] == 1000
    
    @pytest.mark.integration
    def test_error_handling_workflow(self):
        """Тест обработки ошибок в рабочем процессе"""
        with patch('generators.text_gen.openai.OpenAI') as mock_openai:
            # Настройка ошибки генерации текста
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("OpenAI error")
            mock_openai.return_value = mock_client
            
            text_gen = TextGenerator(
                tone="дружелюбный",
                topic="технологии"
            )
            
            result = text_gen.generate_post()
            assert result is None
    
    @pytest.mark.integration
    def test_partial_failure_workflow(self):
        """Тест частичного сбоя в процессе"""
        with patch('generators.text_gen.openai.OpenAI') as mock_openai_text, \
             patch('generators.image_gen.openai.OpenAI') as mock_openai_image, \
             patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api, \
             patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot:
            
            # Успешная генерация текста
            mock_text_client = MagicMock()
            mock_text_response = MagicMock()
            mock_text_response.choices = [MagicMock()]
            mock_text_response.choices[0].message.content = "Тестовый пост"
            mock_text_client.chat.completions.create.return_value = mock_text_response
            mock_openai_text.return_value = mock_text_client
            
            # Ошибка генерации изображения
            mock_image_client = MagicMock()
            mock_image_client.images.generate.side_effect = Exception("Image generation failed")
            mock_openai_image.return_value = mock_image_client
            
            # Успешная публикация в VK
            mock_vk_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.post.return_value = {'post_id': 123}
            mock_vk_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_vk_session
            
            # Ошибка публикации в Telegram
            mock_bot = MagicMock()
            mock_bot.send_message.side_effect = Exception("Telegram error")
            mock_telebot.return_value = mock_bot
            
            # Выполнение процесса с частичными сбоями
            text_gen = TextGenerator(tone="дружелюбный", topic="технологии")
            post_text = text_gen.generate_post()
            assert post_text == "Тестовый пост"
            
            image_gen = ImageGenerator()
            image_url = image_gen.generate_image("Test prompt")
            assert image_url is None
            
            vk_publisher = VKPublisher("test-token", 123456)
            vk_result = vk_publisher.publish_post(post_text, image_url)
            assert vk_result == {'post_id': 123}
            
            tg_publisher = TelegramPublisher("test-token", "@test_channel")
            tg_result = tg_publisher.send_post(post_text, image_url)
            assert tg_result is None

