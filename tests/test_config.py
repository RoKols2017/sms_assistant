"""
Тесты для модуля конфигурации
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from config import Config


class TestConfig:
    """Тесты для класса Config"""
    
    def test_config_initialization_success(self):
        """Тест успешной инициализации конфигурации"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-openai-key',
            'VK_TOKEN': 'test-vk-token',
            'VK_GROUP_ID': '123456789',
            'TG_TOKEN': 'test-tg-token',
            'TG_CHAT_ID': '@test_channel'
        }):
            config = Config()
            assert config.openai_api_key == 'test-openai-key'
            assert config.vk_token == 'test-vk-token'
            assert config.vk_group_id == 123456789
            assert config.telegram_token == 'test-tg-token'
            assert config.telegram_chat_id == '@test_channel'
    
    def test_config_missing_required_vars(self):
        """Тест ошибки при отсутствии обязательных переменных"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Отсутствуют обязательные переменные окружения"):
                Config()
    
    def test_config_invalid_group_id(self):
        """Тест ошибки при некорректном VK_GROUP_ID"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'VK_TOKEN': 'test-token',
            'VK_GROUP_ID': 'invalid',
            'TG_TOKEN': 'test-token',
            'TG_CHAT_ID': '@test'
        }):
            with pytest.raises(ValueError, match="VK_GROUP_ID должен быть числом"):
                Config()
    
    def test_config_default_values(self):
        """Тест значений по умолчанию"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'VK_TOKEN': 'test-token',
            'VK_GROUP_ID': '123456',
            'TG_TOKEN': 'test-token',
            'TG_CHAT_ID': '@test'
        }):
            config = Config()
            assert config.log_level == 'INFO'
            assert config.max_retries == 3
            assert config.timeout == 30
            assert config.openai_text_model == 'gpt-5'
            assert config.openai_image_model == 'dall-e-3'
    
    def test_config_custom_values(self):
        """Тест пользовательских значений"""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'VK_TOKEN': 'test-token',
            'VK_GROUP_ID': '123456',
            'TG_TOKEN': 'test-token',
            'TG_CHAT_ID': '@test',
            'LOG_LEVEL': 'DEBUG',
            'MAX_RETRIES': '5',
            'TIMEOUT': '60',
            'OPENAI_TEXT_MODEL': 'gpt-4o',
            'OPENAI_IMAGE_MODEL': 'dall-e-2'
        }):
            config = Config()
            assert config.log_level == 'DEBUG'
            assert config.max_retries == 5
            assert config.timeout == 60
            assert config.openai_text_model == 'gpt-4o'
            assert config.openai_image_model == 'dall-e-2'

