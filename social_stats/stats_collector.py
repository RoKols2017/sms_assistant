"""
Модуль для сбора статистики из социальных сетей
"""

import vk_api
import telebot
import requests
from typing import Optional, Dict, Any
import logging


class StatsCollector:
    """
    Класс для сбора статистики из социальных сетей
    """
    
    def __init__(self, vk_access_token: Optional[str] = None, telegram_bot_token: Optional[str] = None):
        """
        Инициализация сборщика статистики
        
        Args:
            vk_access_token (Optional[str]): Токен доступа ВК для получения статистики
            telegram_bot_token (Optional[str]): Токен Telegram бота для получения статистики
        """
        self.vk_access_token = vk_access_token
        self.telegram_bot_token = telegram_bot_token
        
        # Инициализация VK API если токен предоставлен
        if vk_access_token:
            self.vk_session = vk_api.VkApi(token=vk_access_token)
            self.vk = self.vk_session.get_api()
        else:
            self.vk = None
        
        # Инициализация Telegram бота если токен предоставлен
        if telegram_bot_token:
            self.bot = telebot.TeleBot(telegram_bot_token)
        else:
            self.bot = None
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_vk_stats(self, post_id: int, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает статистику поста ВК
        
        Args:
            post_id (int): ID поста
            group_id (int): ID группы
            
        Returns:
            Optional[Dict[str, Any]]: Словарь со статистикой или None в случае ошибки
        """
        if not self.vk:
            error_msg = "VK API не инициализирован. Укажите vk_access_token в конструкторе."
            self.logger.error(error_msg)
            print(error_msg)
            return None
        
        try:
            self.logger.info(f"Получение статистики поста {post_id} из группы {group_id}")
            
            # Получаем информацию о посте
            post_info = self.vk.wall.getById(
                posts=f"-{group_id}_{post_id}",
                extended=1
            )
            
            if not post_info or not post_info[0]:
                self.logger.warning(f"Пост {post_id} не найден")
                return None
            
            post = post_info[0]
            
            # Извлекаем статистику
            stats = {
                'post_id': post_id,
                'group_id': group_id,
                'likes': post.get('likes', {}).get('count', 0),
                'reposts': post.get('reposts', {}).get('count', 0),
                'comments': post.get('comments', {}).get('count', 0),
                'views': post.get('views', {}).get('count', 0) if 'views' in post else 0,
                'text': post.get('text', ''),
                'date': post.get('date', 0)
            }
            
            self.logger.info(f"Статистика получена: {stats}")
            return stats
            
        except vk_api.exceptions.ApiError as e:
            error_msg = f"Ошибка VK API при получении статистики: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
        except Exception as e:
            error_msg = f"Неожиданная ошибка при получении статистики ВК: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
    
    def get_telegram_stats(self, message_id: int, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает статистику сообщения Telegram
        
        Args:
            message_id (int): ID сообщения
            chat_id (str): ID чата/канала
            
        Returns:
            Optional[Dict[str, Any]]: Словарь со статистикой или None в случае ошибки
        """
        if not self.bot:
            error_msg = "Telegram API не инициализирован. Укажите telegram_bot_token в конструкторе."
            self.logger.error(error_msg)
            print(error_msg)
            return None
        
        try:
            self.logger.info(f"Получение статистики сообщения {message_id} из чата {chat_id}")
            
            # Получаем информацию о сообщении
            message = self.bot.get_chat(chat_id)
            
            # Для каналов получаем статистику через get_chat_member_count
            member_count = 0
            try:
                member_count = self.bot.get_chat_member_count(chat_id)
            except Exception as e:
                self.logger.warning(f"Не удалось получить количество участников: {e}")
            
            # Базовые метрики для Telegram
            stats = {
                'message_id': message_id,
                'chat_id': chat_id,
                'chat_title': message.title if hasattr(message, 'title') else 'Unknown',
                'chat_type': message.type if hasattr(message, 'type') else 'Unknown',
                'member_count': member_count,
                'is_channel': message.type == 'channel' if hasattr(message, 'type') else False
            }
            
            # Для каналов пытаемся получить дополнительную статистику
            if stats['is_channel']:
                try:
                    # Получаем информацию о последних сообщениях для оценки активности
                    # Это приблизительная оценка, так как Telegram API ограничен
                    stats['estimated_reach'] = member_count
                    stats['engagement_rate'] = 0.0  # Telegram не предоставляет точные метрики
                except Exception as e:
                    self.logger.warning(f"Не удалось получить дополнительную статистику канала: {e}")
            
            self.logger.info(f"Статистика Telegram получена: {stats}")
            return stats
            
        except telebot.apihelper.ApiTelegramException as e:
            error_msg = f"Ошибка Telegram API при получении статистики: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
        except Exception as e:
            error_msg = f"Неожиданная ошибка при получении статистики Telegram: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
    
    def get_combined_stats(self, vk_post_id: Optional[int] = None, vk_group_id: Optional[int] = None,
                          telegram_message_id: Optional[int] = None, telegram_chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Получает комбинированную статистику из всех доступных источников
        
        Args:
            vk_post_id (Optional[int]): ID поста ВК
            vk_group_id (Optional[int]): ID группы ВК
            telegram_message_id (Optional[int]): ID сообщения Telegram
            telegram_chat_id (Optional[str]): ID чата Telegram
            
        Returns:
            Dict[str, Any]: Словарь с комбинированной статистикой
        """
        combined_stats = {
            'timestamp': None,
            'vk_stats': None,
            'telegram_stats': None
        }
        
        # Получаем статистику ВК
        if vk_post_id and vk_group_id:
            vk_stats = self.get_vk_stats(vk_post_id, vk_group_id)
            combined_stats['vk_stats'] = vk_stats
        
        # Получаем статистику Telegram
        if telegram_message_id and telegram_chat_id:
            telegram_stats = self.get_telegram_stats(telegram_message_id, telegram_chat_id)
            combined_stats['telegram_stats'] = telegram_stats
        
        return combined_stats


if __name__ == "__main__":
    # Тестирование класса
    print("Тестирование StatsCollector...")
    
    # Замените на ваши реальные данные для тестирования
    test_vk_token = "your-vk-access-token-here"
    test_telegram_token = "your-telegram-bot-token-here"
    
    collector = StatsCollector(
        vk_access_token=test_vk_token,
        telegram_bot_token=test_telegram_token
    )
    
    # Тестирование статистики ВК
    vk_stats = collector.get_vk_stats(
        post_id=123456789,  # Замените на реальный ID поста
        group_id=123456789  # Замените на реальный ID группы
    )
    if vk_stats:
        print(f"Статистика ВК: {vk_stats}")
    else:
        print("Не удалось получить статистику ВК")
    
    # Тестирование статистики Telegram
    telegram_stats = collector.get_telegram_stats(
        message_id=123,  # Замените на реальный ID сообщения
        chat_id="@your_channel"  # Замените на реальный ID чата
    )
    if telegram_stats:
        print(f"Статистика Telegram: {telegram_stats}")
    else:
        print("Не удалось получить статистику Telegram")
    
    # Тестирование комбинированной статистики
    combined = collector.get_combined_stats(
        vk_post_id=123456789,
        vk_group_id=123456789,
        telegram_message_id=123,
        telegram_chat_id="@your_channel"
    )
    print(f"Комбинированная статистика: {combined}")
