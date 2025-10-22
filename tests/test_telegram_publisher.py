"""
Тесты для Telegram публикатора
"""

import pytest
from unittest.mock import patch, MagicMock
from social_publishers.telegram_publisher import TelegramPublisher


class TestTelegramPublisher:
    """Тесты для класса TelegramPublisher"""
    
    def test_init_success(self):
        """Тест успешной инициализации"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot:
            mock_bot = MagicMock()
            mock_telebot.return_value = mock_bot
            
            publisher = TelegramPublisher(
                bot_token="test-token",
                chat_id="@test_channel"
            )
            
            assert publisher.bot_token == "test-token"
            assert publisher.chat_id == "@test_channel"
    
    def test_send_post_text_only(self):
        """Тест отправки только текста"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot:
            mock_bot = MagicMock()
            mock_message = MagicMock()
            mock_message.message_id = 123
            mock_message.chat.id = 456
            mock_message.text = "Test message"
            mock_bot.send_message.return_value = mock_message
            mock_telebot.return_value = mock_bot
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher.send_post("Test message")
            
            assert result['message_id'] == 123
            assert result['chat_id'] == 456
            assert result['text'] == "Test message"
            mock_bot.send_message.assert_called_once_with(
                chat_id="@test_channel",
                text="Test message",
                parse_mode='HTML'
            )
    
    def test_send_post_with_image(self):
        """Тест отправки с изображением"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot, \
             patch('social_publishers.telegram_publisher.requests.get') as mock_get:
            
            mock_bot = MagicMock()
            mock_message = MagicMock()
            mock_message.message_id = 123
            mock_message.chat.id = 456
            mock_message.caption = "Test message"
            mock_message.photo = "photo_data"
            mock_bot.send_photo.return_value = mock_message
            mock_telebot.return_value = mock_bot
            
            mock_get.return_value.raise_for_status.return_value = None
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher.send_post("Test message", "http://example.com/image.jpg")
            
            assert result['message_id'] == 123
            assert result['chat_id'] == 456
            assert result['text'] == "Test message"
            assert result['photo'] == "photo_data"
            mock_bot.send_photo.assert_called_once_with(
                chat_id="@test_channel",
                photo="http://example.com/image.jpg",
                caption="Test message",
                parse_mode='HTML'
            )
    
    def test_send_post_image_download_error(self):
        """Тест ошибки скачивания изображения"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot, \
             patch('social_publishers.telegram_publisher.requests.get') as mock_get:
            
            mock_bot = MagicMock()
            mock_telebot.return_value = mock_bot
            
            mock_get.side_effect = Exception("Download failed")
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher.send_post("Test message", "http://example.com/image.jpg")
            
            assert result is None
    
    def test_send_post_telegram_api_error(self):
        """Тест ошибки Telegram API"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot:
            mock_bot = MagicMock()
            mock_bot.send_message.side_effect = Exception("Telegram API error")
            mock_telebot.return_value = mock_bot
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher.send_post("Test message")
            
            assert result is None
    
    def test_send_post_general_exception(self):
        """Тест общего исключения"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot:
            mock_bot = MagicMock()
            mock_bot.send_message.side_effect = Exception("General error")
            mock_telebot.return_value = mock_bot
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher.send_post("Test message")
            
            assert result is None
    
    def test_send_text_message_success(self):
        """Тест успешной отправки текстового сообщения"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot:
            mock_bot = MagicMock()
            mock_message = MagicMock()
            mock_message.message_id = 123
            mock_message.chat.id = 456
            mock_message.text = "Test message"
            mock_bot.send_message.return_value = mock_message
            mock_telebot.return_value = mock_bot
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher._send_text_message("Test message")
            
            assert result['message_id'] == 123
            assert result['chat_id'] == 456
            assert result['text'] == "Test message"
    
    def test_send_text_message_api_error(self):
        """Тест ошибки API при отправке текста"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot:
            mock_bot = MagicMock()
            mock_bot.send_message.side_effect = Exception("API error")
            mock_telebot.return_value = mock_bot
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher._send_text_message("Test message")
            
            assert result is None
    
    def test_send_photo_message_success(self):
        """Тест успешной отправки фото"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot, \
             patch('social_publishers.telegram_publisher.requests.get') as mock_get:
            
            mock_bot = MagicMock()
            mock_message = MagicMock()
            mock_message.message_id = 123
            mock_message.chat.id = 456
            mock_message.caption = "Test caption"
            mock_message.photo = "photo_data"
            mock_bot.send_photo.return_value = mock_message
            mock_telebot.return_value = mock_bot
            
            mock_get.return_value.raise_for_status.return_value = None
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher._send_photo_message("Test caption", "http://example.com/image.jpg")
            
            assert result['message_id'] == 123
            assert result['chat_id'] == 456
            assert result['text'] == "Test caption"
            assert result['photo'] == "photo_data"
    
    def test_send_photo_message_download_error(self):
        """Тест ошибки скачивания при отправке фото"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot, \
             patch('social_publishers.telegram_publisher.requests.get') as mock_get:
            
            mock_bot = MagicMock()
            mock_telebot.return_value = mock_bot
            
            mock_get.side_effect = Exception("Download failed")
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher._send_photo_message("Test caption", "http://example.com/image.jpg")
            
            assert result is None
    
    def test_send_photo_message_telegram_error(self):
        """Тест ошибки Telegram при отправке фото"""
        with patch('social_publishers.telegram_publisher.telebot.TeleBot') as mock_telebot, \
             patch('social_publishers.telegram_publisher.requests.get') as mock_get:
            
            mock_bot = MagicMock()
            mock_bot.send_photo.side_effect = Exception("Telegram error")
            mock_telebot.return_value = mock_bot
            
            mock_get.return_value.raise_for_status.return_value = None
            
            publisher = TelegramPublisher("test-token", "@test_channel")
            
            result = publisher._send_photo_message("Test caption", "http://example.com/image.jpg")
            
            assert result is None

