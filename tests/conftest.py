"""
Конфигурация тестов
"""

import os
from unittest.mock import patch

import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture(autouse=True)
def mock_environment():
    """Мок переменных окружения для всех тестов"""
    with patch.dict(os.environ, {
        'FLASK_ENV': 'testing',
        'FLASK_SECRET_KEY': 'test-secret-key',
        'OPENAI_API_KEY': 'test-openai-key',
        'VK_TOKEN': 'test-vk-token',
        'VK_GROUP_ID': '123456789',
        'TG_TOKEN': 'test-tg-token',
        'TG_CHAT_ID': '@test_channel',
        'DATABASE_URL': 'sqlite:///:memory:',
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


@pytest.fixture
def app():
    """Flask app fixture for web tests."""
    application = create_app(TestConfig)
    application.config.update(TESTING=True)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI runner."""
    return app.test_cli_runner()
