"""
Модуль для публикации сообщений в Telegram через бот
"""

import telebot
import requests
from typing import Optional, Dict, Any
import logging


class TelegramPublisher:
    """
    Класс для публикации сообщений в Telegram
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Инициализация публикатора Telegram
        
        Args:
            bot_token (str): Токен Telegram бота
            chat_id (str): ID чата для отправки сообщений
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        
        # Инициализация Telegram бота
        self.bot = telebot.TeleBot(bot_token)
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def send_post(self, text: str, image_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Отправляет сообщение в Telegram чат
        
        Args:
            text (str): Текст сообщения
            image_url (Optional[str]): URL изображения для отправки
            
        Returns:
            Optional[Dict[str, Any]]: Данные отправленного сообщения или None в случае ошибки
        """
        try:
            self.logger.info(f"Отправка сообщения в чат {self.chat_id}")
            
            if image_url:
                # Отправляем сообщение с изображением
                return self._send_photo_message(text, image_url)
            else:
                # Отправляем только текстовое сообщение
                return self._send_text_message(text)
                
        except Exception as e:
            error_msg = f"Неожиданная ошибка при отправке сообщения: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
    
    def _send_text_message(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Отправляет текстовое сообщение
        
        Args:
            text (str): Текст сообщения
            
        Returns:
            Optional[Dict[str, Any]]: Данные отправленного сообщения или None в случае ошибки
        """
        try:
            message = self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='HTML'
            )
            
            self.logger.info(f"Текстовое сообщение отправлено, ID: {message.message_id}")
            return {
                'message_id': message.message_id,
                'chat_id': message.chat.id,
                'text': message.text
            }
            
        except telebot.apihelper.ApiTelegramException as e:
            error_msg = f"Ошибка Telegram API при отправке текста: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
        except Exception as e:
            error_msg = f"Ошибка при отправке текстового сообщения: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
    
    def _send_photo_message(self, text: str, image_url: str) -> Optional[Dict[str, Any]]:
        """
        Отправляет сообщение с изображением
        
        Args:
            text (str): Текст сообщения
            image_url (str): URL изображения
            
        Returns:
            Optional[Dict[str, Any]]: Данные отправленного сообщения или None в случае ошибки
        """
        try:
            self.logger.info(f"Отправка изображения: {image_url}")
            
            # Скачиваем изображение
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            # Отправляем фото с подписью
            message = self.bot.send_photo(
                chat_id=self.chat_id,
                photo=image_url,
                caption=text,
                parse_mode='HTML'
            )
            
            self.logger.info(f"Сообщение с изображением отправлено, ID: {message.message_id}")
            return {
                'message_id': message.message_id,
                'chat_id': message.chat.id,
                'text': message.caption,
                'photo': message.photo
            }
            
        except requests.RequestException as e:
            error_msg = f"Ошибка при скачивании изображения: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
        except telebot.apihelper.ApiTelegramException as e:
            error_msg = f"Ошибка Telegram API при отправке изображения: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
        except Exception as e:
            error_msg = f"Ошибка при отправке сообщения с изображением: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None


if __name__ == "__main__":
    # Тестирование класса
    print("Тестирование TelegramPublisher...")
    
    # Замените на ваши реальные данные для тестирования
    test_token = "your-telegram-bot-token-here"
    test_chat_id = "@your_channel"  # или ID чата
    
    publisher = TelegramPublisher(
        bot_token=test_token,
        chat_id=test_chat_id
    )
    
    # Тестовое сообщение
    test_text = "Тестовое сообщение от SMM-бота! 🤖\n\nЭто автоматически сгенерированный пост."
    test_image_url = "https://example.com/image.jpg"  # Замените на реальный URL
    
    # Отправка сообщения с изображением
    result = publisher.send_post(test_text, test_image_url)
    if result:
        print(f"Сообщение с изображением отправлено! ID: {result.get('message_id')}")
    else:
        print("Не удалось отправить сообщение с изображением")
    
    # Отправка только текстового сообщения
    result_text_only = publisher.send_post("Простое текстовое сообщение")
    if result_text_only:
        print(f"Текстовое сообщение отправлено! ID: {result_text_only.get('message_id')}")
    else:
        print("Не удалось отправить текстовое сообщение")
