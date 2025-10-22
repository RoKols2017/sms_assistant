"""
Конфигурация тестов
"""

import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_environment():
    """Мок переменных окружения для всех тестов"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-openai-key',
        'VK_TOKEN': 'test-vk-token',
        'VK_GROUP_ID': '123456789',
        'TG_TOKEN': 'test-tg-token',
        'TG_CHAT_ID': '@test_channel',
        'LOG_LEVEL': 'INFO',
        'MAX_RETRIES': '3',
        'TIMEOUT': '30'
    }):
        yield


@pytest.fixture
def mock_openai_client():
    """Мок OpenAI клиента"""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = mock_openai.return_value
        yield mock_client


@pytest.fixture
def mock_vk_api():
    """Мок VK API"""
    with patch('vk_api.VkApi') as mock_vk:
        mock_session = mock_vk.return_value
        mock_vk_api = mock_session.get_api.return_value
        yield mock_vk_api


@pytest.fixture
def mock_telegram_bot():
    """Мок Telegram бота"""
    with patch('telebot.TeleBot') as mock_telebot:
        mock_bot = mock_telebot.return_value
        yield mock_bot


@pytest.fixture
def mock_requests():
    """Мок requests"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        yield mock_get, mock_post

