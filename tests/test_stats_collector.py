"""
Тесты для сборщика статистики
"""

import pytest
from unittest.mock import patch, MagicMock
from social_stats.stats_collector import StatsCollector


class TestStatsCollector:
    """Тесты для класса StatsCollector"""
    
    def test_init_with_tokens(self):
        """Тест инициализации с токенами"""
        with patch('social_stats.stats_collector.vk_api.VkApi') as mock_vk_api, \
             patch('social_stats.stats_collector.telebot.TeleBot') as mock_telebot:
            
            mock_vk_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_vk_session
            
            mock_bot = MagicMock()
            mock_telebot.return_value = mock_bot
            
            collector = StatsCollector(
                vk_access_token="test-vk-token",
                telegram_bot_token="test-tg-token"
            )
            
            assert collector.vk_access_token == "test-vk-token"
            assert collector.telegram_bot_token == "test-tg-token"
            assert collector.vk is not None
            assert collector.bot is not None
    
    def test_init_without_tokens(self):
        """Тест инициализации без токенов"""
        collector = StatsCollector()
        
        assert collector.vk_access_token is None
        assert collector.telegram_bot_token is None
        assert collector.vk is None
        assert collector.bot is None
    
    def test_get_vk_stats_no_vk_api(self):
        """Тест получения статистики ВК без инициализированного API"""
        collector = StatsCollector()
        
        result = collector.get_vk_stats(123, 456)
        
        assert result is None
    
    def test_get_vk_stats_success(self):
        """Тест успешного получения статистики ВК"""
        with patch('social_stats.stats_collector.vk_api.VkApi') as mock_vk_api:
            mock_vk_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.getById.return_value = [{
                'likes': {'count': 10},
                'reposts': {'count': 5},
                'comments': {'count': 3},
                'views': {'count': 100},
                'text': 'Test post',
                'date': 1234567890
            }]
            mock_vk_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_vk_session
            
            collector = StatsCollector(vk_access_token="test-token")
            
            result = collector.get_vk_stats(123, 456)
            
            assert result['post_id'] == 123
            assert result['group_id'] == 456
            assert result['likes'] == 10
            assert result['reposts'] == 5
            assert result['comments'] == 3
            assert result['views'] == 100
            assert result['text'] == 'Test post'
            assert result['date'] == 1234567890
    
    def test_get_vk_stats_post_not_found(self):
        """Тест получения статистики ВК для несуществующего поста"""
        with patch('social_stats.stats_collector.vk_api.VkApi') as mock_vk_api:
            mock_vk_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.getById.return_value = []
            mock_vk_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_vk_session
            
            collector = StatsCollector(vk_access_token="test-token")
            
            result = collector.get_vk_stats(123, 456)
            
            assert result is None
    
    def test_get_vk_stats_api_error(self):
        """Тест ошибки VK API при получении статистики"""
        with patch('social_stats.stats_collector.vk_api.VkApi') as mock_vk_api:
            mock_vk_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.getById.side_effect = Exception("VK API error")
            mock_vk_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_vk_session
            
            collector = StatsCollector(vk_access_token="test-token")
            
            result = collector.get_vk_stats(123, 456)
            
            assert result is None
    
    def test_get_telegram_stats_no_bot(self):
        """Тест получения статистики Telegram без инициализированного бота"""
        collector = StatsCollector()
        
        result = collector.get_telegram_stats(123, "@test_channel")
        
        assert result is None
    
    def test_get_telegram_stats_success(self):
        """Тест успешного получения статистики Telegram"""
        with patch('social_stats.stats_collector.telebot.TeleBot') as mock_telebot:
            mock_bot = MagicMock()
            mock_chat = MagicMock()
            mock_chat.title = "Test Channel"
            mock_chat.type = "channel"
            mock_bot.get_chat.return_value = mock_chat
            mock_bot.get_chat_member_count.return_value = 1000
            mock_telebot.return_value = mock_bot
            
            collector = StatsCollector(telegram_bot_token="test-token")
            
            result = collector.get_telegram_stats(123, "@test_channel")
            
            assert result['message_id'] == 123
            assert result['chat_id'] == "@test_channel"
            assert result['chat_title'] == "Test Channel"
            assert result['chat_type'] == "channel"
            assert result['member_count'] == 1000
            assert result['is_channel'] is True
            assert result['estimated_reach'] == 1000
    
    def test_get_telegram_stats_member_count_error(self):
        """Тест ошибки получения количества участников"""
        with patch('social_stats.stats_collector.telebot.TeleBot') as mock_telebot:
            mock_bot = MagicMock()
            mock_chat = MagicMock()
            mock_chat.title = "Test Channel"
            mock_chat.type = "channel"
            mock_bot.get_chat.return_value = mock_chat
            mock_bot.get_chat_member_count.side_effect = Exception("Member count error")
            mock_telebot.return_value = mock_bot
            
            collector = StatsCollector(telegram_bot_token="test-token")
            
            result = collector.get_telegram_stats(123, "@test_channel")
            
            assert result['member_count'] == 0
    
    def test_get_telegram_stats_api_error(self):
        """Тест ошибки Telegram API при получении статистики"""
        with patch('social_stats.stats_collector.telebot.TeleBot') as mock_telebot:
            mock_bot = MagicMock()
            mock_bot.get_chat.side_effect = Exception("Telegram API error")
            mock_telebot.return_value = mock_bot
            
            collector = StatsCollector(telegram_bot_token="test-token")
            
            result = collector.get_telegram_stats(123, "@test_channel")
            
            assert result is None
    
    def test_get_combined_stats_vk_only(self):
        """Тест комбинированной статистики только для VK"""
        with patch('social_stats.stats_collector.vk_api.VkApi') as mock_vk_api, \
             patch.object(StatsCollector, 'get_vk_stats') as mock_get_vk:
            
            mock_vk_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_vk_session
            
            mock_get_vk.return_value = {'likes': 10, 'reposts': 5}
            
            collector = StatsCollector(vk_access_token="test-token")
            
            result = collector.get_combined_stats(
                vk_post_id=123,
                vk_group_id=456
            )
            
            assert result['vk_stats'] == {'likes': 10, 'reposts': 5}
            assert result['telegram_stats'] is None
    
    def test_get_combined_stats_telegram_only(self):
        """Тест комбинированной статистики только для Telegram"""
        with patch('social_stats.stats_collector.telebot.TeleBot') as mock_telebot, \
             patch.object(StatsCollector, 'get_telegram_stats') as mock_get_tg:
            
            mock_bot = MagicMock()
            mock_telebot.return_value = mock_bot
            
            mock_get_tg.return_value = {'member_count': 1000}
            
            collector = StatsCollector(telegram_bot_token="test-token")
            
            result = collector.get_combined_stats(
                telegram_message_id=123,
                telegram_chat_id="@test_channel"
            )
            
            assert result['vk_stats'] is None
            assert result['telegram_stats'] == {'member_count': 1000}
    
    def test_get_combined_stats_both(self):
        """Тест комбинированной статистики для обеих платформ"""
        with patch('social_stats.stats_collector.vk_api.VkApi') as mock_vk_api, \
             patch('social_stats.stats_collector.telebot.TeleBot') as mock_telebot, \
             patch.object(StatsCollector, 'get_vk_stats') as mock_get_vk, \
             patch.object(StatsCollector, 'get_telegram_stats') as mock_get_tg:
            
            mock_vk_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_vk_session
            
            mock_bot = MagicMock()
            mock_telebot.return_value = mock_bot
            
            mock_get_vk.return_value = {'likes': 10}
            mock_get_tg.return_value = {'member_count': 1000}
            
            collector = StatsCollector(
                vk_access_token="test-token",
                telegram_bot_token="test-token"
            )
            
            result = collector.get_combined_stats(
                vk_post_id=123,
                vk_group_id=456,
                telegram_message_id=789,
                telegram_chat_id="@test_channel"
            )
            
            assert result['vk_stats'] == {'likes': 10}
            assert result['telegram_stats'] == {'member_count': 1000}

