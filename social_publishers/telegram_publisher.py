import logging
from typing import Any, Dict, Optional

import requests
import telebot

from config import config


logger = logging.getLogger(__name__)


class TelegramPublisher:
    """
    Класс для публикации сообщений в Telegram
    """
    
    def __init__(self, bot_token: str, chat_id: str, timeout: Optional[int] = None):
        """
        Инициализация публикатора Telegram
        
        Args:
            bot_token (str): Токен Telegram бота
            chat_id (str): ID чата для отправки сообщений
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.timeout = timeout if timeout is not None else getattr(config, "request_timeout", config.timeout)

        if not bot_token or not chat_id:
            self.bot = None
            logger.warning(
                "[TelegramPublisher.__init__] telegram disabled extra=%s",
                {"has_token": bool(bot_token), "has_chat_id": bool(chat_id), "timeout": self.timeout},
            )
            return

        self.bot = telebot.TeleBot(bot_token)
        logger.info(
            "[TelegramPublisher.__init__] initialized extra=%s",
            {"chat_id": self.chat_id, "timeout": self.timeout},
        )
    
    def send_post(self, text: str, image_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Отправляет сообщение в Telegram чат
        
        Args:
            text (str): Текст сообщения
            image_url (Optional[str]): URL изображения для отправки
            
        Returns:
            Optional[Dict[str, Any]]: Данные отправленного сообщения или None в случае ошибки
        """
        if not self.bot:
            logger.warning(
                "[TelegramPublisher.send_post] telegram bot unavailable extra=%s",
                {"chat_id": self.chat_id},
            )
            return None

        try:
            logger.info(
                "[TelegramPublisher.send_post] start extra=%s",
                {"chat_id": self.chat_id, "has_image": bool(image_url), "timeout": self.timeout},
            )
            
            if image_url:
                # Отправляем сообщение с изображением
                return self._send_photo_message(text, image_url)
            else:
                # Отправляем только текстовое сообщение
                return self._send_text_message(text)
                
        except Exception as e:
            logger.exception(
                "[TelegramPublisher.send_post] unexpected error extra=%s",
                {"chat_id": self.chat_id, "error": str(e)},
            )
            return None
    
    def _send_text_message(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Отправляет текстовое сообщение
        
        Args:
            text (str): Текст сообщения
            
        Returns:
            Optional[Dict[str, Any]]: Данные отправленного сообщения или None в случае ошибки
        """
        if not self.bot:
            logger.warning(
                "[TelegramPublisher._send_text_message] telegram bot unavailable extra=%s",
                {"chat_id": self.chat_id},
            )
            return None

        try:
            logger.info(
                "[TelegramPublisher._send_text_message] start extra=%s",
                {"chat_id": self.chat_id, "text_length": len(text)},
            )
            message = self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='HTML'
            )

            logger.info(
                "[TelegramPublisher._send_text_message] completed extra=%s",
                {"chat_id": self.chat_id, "message_id": message.message_id},
            )
            return {
                'message_id': message.message_id,
                'chat_id': message.chat.id,
                'text': message.text
            }

        except telebot.apihelper.ApiTelegramException as e:
            logger.error(
                "[TelegramPublisher._send_text_message] telegram api error extra=%s",
                {"chat_id": self.chat_id, "error": str(e)},
            )
            return None
        except Exception as e:
            logger.exception(
                "[TelegramPublisher._send_text_message] unexpected error extra=%s",
                {"chat_id": self.chat_id, "error": str(e)},
            )
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
        if not self.bot:
            logger.warning(
                "[TelegramPublisher._send_photo_message] telegram bot unavailable extra=%s",
                {"chat_id": self.chat_id},
            )
            return None

        try:
            logger.info(
                "[TelegramPublisher._send_photo_message] start extra=%s",
                {"chat_id": self.chat_id, "image_url": image_url, "timeout": self.timeout},
            )

            # Проверяем доступность изображения, чтобы Telegram не получил битую ссылку.
            response = requests.get(image_url, stream=True, timeout=self.timeout)
            response.raise_for_status()

            message = self.bot.send_photo(
                chat_id=self.chat_id,
                photo=image_url,
                caption=text,
                parse_mode='HTML'
            )

            logger.info(
                "[TelegramPublisher._send_photo_message] completed extra=%s",
                {"chat_id": self.chat_id, "message_id": message.message_id},
            )
            return {
                'message_id': message.message_id,
                'chat_id': message.chat.id,
                'text': message.caption,
                'photo': message.photo
            }

        except requests.RequestException as e:
            logger.error(
                "[TelegramPublisher._send_photo_message] image fetch error extra=%s",
                {"chat_id": self.chat_id, "image_url": image_url, "error": str(e)},
            )
            return None
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(
                "[TelegramPublisher._send_photo_message] telegram api error extra=%s",
                {"chat_id": self.chat_id, "error": str(e)},
            )
            return None
        except Exception as e:
            logger.exception(
                "[TelegramPublisher._send_photo_message] unexpected error extra=%s",
                {"chat_id": self.chat_id, "image_url": image_url, "error": str(e)},
            )
            return None
