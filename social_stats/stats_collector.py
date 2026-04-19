import logging
from typing import Any, Dict, Optional

import telebot
import vk_api

from config import config


logger = logging.getLogger(__name__)


class StatsCollector:
    """
    Класс для сбора статистики из социальных сетей
    """
    
    def __init__(
        self,
        vk_access_token: Optional[str] = None,
        telegram_bot_token: Optional[str] = None,
        api_version: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        Инициализация сборщика статистики
        
        Args:
            vk_access_token (Optional[str]): Токен доступа ВК для получения статистики
            telegram_bot_token (Optional[str]): Токен Telegram бота для получения статистики
        """
        self.vk_access_token = vk_access_token
        self.telegram_bot_token = telegram_bot_token
        self.api_version = api_version or config.vk_api_version
        self.timeout = timeout if timeout is not None else getattr(config, "request_timeout", config.timeout)

        if vk_access_token:
            self.vk_session = vk_api.VkApi(token=vk_access_token, api_version=self.api_version)
            self.vk = self.vk_session.get_api()
        else:
            self.vk = None

        if telegram_bot_token:
            self.bot = telebot.TeleBot(telegram_bot_token)
        else:
            self.bot = None

        logger.info(
            "[StatsCollector.__init__] initialized extra=%s",
            {
                "has_vk": bool(vk_access_token),
                "has_telegram": bool(telegram_bot_token),
                "api_version": self.api_version,
                "timeout": self.timeout,
            },
        )

    def _extract_group(self, payload: Any) -> Optional[Dict[str, Any]]:
        if isinstance(payload, list):
            return payload[0] if payload else None

        if isinstance(payload, dict):
            groups = payload.get("groups")
            if isinstance(groups, list) and groups:
                return groups[0]

        return None

    def get_group_info(self, group_id: int, fields: Optional[list[str]] = None) -> Optional[Dict[str, Any]]:
        if not self.vk:
            logger.error("[StatsCollector.get_group_info] vk not configured extra=%s", {"group_id": group_id})
            return None

        try:
            logger.info(
                "[StatsCollector.get_group_info] start extra=%s",
                {"group_id": group_id, "api_version": self.api_version, "fields": fields or []},
            )
            payload = self.vk.groups.getById(
                group_id=group_id,
                fields=",".join(fields or ["members_count"]),
            )
            group = self._extract_group(payload)
            logger.info(
                "[StatsCollector.get_group_info] completed extra=%s",
                {"group_id": group_id, "has_group": bool(group)},
            )
            return group
        except vk_api.exceptions.ApiError as e:
            logger.error("[StatsCollector.get_group_info] vk api error extra=%s", {"group_id": group_id, "error": str(e)})
            return None
        except Exception as e:
            logger.exception(
                "[StatsCollector.get_group_info] unexpected error extra=%s",
                {"group_id": group_id, "error": str(e)},
            )
            return None

    def get_group_members_count(self, group_id: int) -> Optional[int]:
        if not self.vk:
            logger.error(
                "[StatsCollector.get_group_members_count] vk not configured extra=%s",
                {"group_id": group_id},
            )
            return None

        group_info = self.get_group_info(group_id, fields=["members_count"])
        if group_info and group_info.get("members_count") is not None:
            logger.info(
                "[StatsCollector.get_group_members_count] using groups.getById extra=%s",
                {"group_id": group_id, "members_count": group_info.get("members_count")},
            )
            return int(group_info["members_count"])

        try:
            logger.info(
                "[StatsCollector.get_group_members_count] fallback groups.getMembers start extra=%s",
                {"group_id": group_id},
            )
            payload = self.vk.groups.getMembers(group_id=group_id, count=1)
            members_count = payload.get("count") if isinstance(payload, dict) else None
            logger.info(
                "[StatsCollector.get_group_members_count] fallback groups.getMembers extra=%s",
                {"group_id": group_id, "members_count": members_count},
            )
            return int(members_count) if members_count is not None else None
        except vk_api.exceptions.ApiError as e:
            logger.error(
                "[StatsCollector.get_group_members_count] fallback vk api error extra=%s",
                {"group_id": group_id, "error": str(e)},
            )
            return None
        except Exception as e:
            logger.exception(
                "[StatsCollector.get_group_members_count] unexpected fallback error extra=%s",
                {"group_id": group_id, "error": str(e)},
            )
            return None
    
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
            logger.error("[StatsCollector.get_vk_stats] vk not configured extra=%s", {"group_id": group_id})
            return None
        
        try:
            logger.info(
                "[StatsCollector.get_vk_stats] start extra=%s",
                {"group_id": group_id, "post_id": post_id},
            )

            post_info = self.vk.wall.getById(
                posts=f"-{group_id}_{post_id}",
                extended=1
            )

            if not post_info or not post_info[0]:
                logger.warning("[StatsCollector.get_vk_stats] post not found extra=%s", {"group_id": group_id, "post_id": post_id})
                return None

            post = post_info[0]

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

            logger.info(
                "[StatsCollector.get_vk_stats] completed extra=%s",
                {"group_id": group_id, "post_id": post_id},
            )
            return stats

        except vk_api.exceptions.ApiError as e:
            logger.error("[StatsCollector.get_vk_stats] vk api error extra=%s", {"group_id": group_id, "post_id": post_id, "error": str(e)})
            return None
        except Exception as e:
            logger.exception(
                "[StatsCollector.get_vk_stats] unexpected error extra=%s",
                {"group_id": group_id, "post_id": post_id, "error": str(e)},
            )
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
            logger.error("[StatsCollector.get_telegram_stats] telegram not configured extra=%s", {"chat_id": chat_id})
            return None
        
        try:
            logger.info(
                "[StatsCollector.get_telegram_stats] start extra=%s",
                {"chat_id": chat_id, "message_id": message_id},
            )

            message = self.bot.get_chat(chat_id)

            member_count = 0
            try:
                member_count = self.bot.get_chat_member_count(chat_id)
            except Exception as e:
                logger.warning(
                    "[StatsCollector.get_telegram_stats] member count unavailable extra=%s",
                        {"chat_id": chat_id, "error": str(e)},
                )

            stats = {
                'message_id': message_id,
                'chat_id': chat_id,
                'chat_title': message.title if hasattr(message, 'title') else 'Unknown',
                'chat_type': message.type if hasattr(message, 'type') else 'Unknown',
                'member_count': member_count,
                'is_channel': message.type == 'channel' if hasattr(message, 'type') else False
            }

            if stats['is_channel']:
                try:
                    stats['estimated_reach'] = member_count
                    stats['engagement_rate'] = 0.0  # Telegram не предоставляет точные метрики
                except Exception as e:
                    logger.warning("[StatsCollector.get_telegram_stats] channel metrics unavailable extra=%s", {"chat_id": chat_id, "error": str(e)})

            logger.info(
                "[StatsCollector.get_telegram_stats] completed extra=%s",
                {"chat_id": chat_id, "message_id": message_id},
            )
            return stats

        except telebot.apihelper.ApiTelegramException as e:
            logger.error("[StatsCollector.get_telegram_stats] telegram api error extra=%s", {"chat_id": chat_id, "message_id": message_id, "error": str(e)})
            return None
        except Exception as e:
            logger.exception(
                "[StatsCollector.get_telegram_stats] unexpected error extra=%s",
                {"chat_id": chat_id, "message_id": message_id, "error": str(e)},
            )
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
        logger.info(
            "[StatsCollector.get_combined_stats] start extra=%s",
            {
                "has_vk_request": bool(vk_post_id and vk_group_id),
                "has_telegram_request": bool(telegram_message_id and telegram_chat_id),
            },
        )
        combined_stats = {
            'timestamp': None,
            'vk_stats': None,
            'telegram_stats': None
        }

        if vk_post_id and vk_group_id:
            vk_stats = self.get_vk_stats(vk_post_id, vk_group_id)
            combined_stats['vk_stats'] = vk_stats

        if telegram_message_id and telegram_chat_id:
            telegram_stats = self.get_telegram_stats(telegram_message_id, telegram_chat_id)
            combined_stats['telegram_stats'] = telegram_stats

        logger.info(
            "[StatsCollector.get_combined_stats] completed extra=%s",
            {
                "has_vk_stats": combined_stats['vk_stats'] is not None,
                "has_telegram_stats": combined_stats['telegram_stats'] is not None,
            },
        )
        return combined_stats
