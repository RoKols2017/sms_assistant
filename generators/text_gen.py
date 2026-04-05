"""Модуль для генерации SMM-постов через OpenAI API."""

from __future__ import annotations

import logging
from typing import Optional

import openai

from config import config


logger = logging.getLogger(__name__)


class TextGenerator:
    """
    Класс для генерации текстовых постов для социальных сетей
    с использованием OpenAI API
    
    БЕЗОПАСНОСТЬ:
    - API ключ загружается из переменных окружения
    - Валидация входных данных
    - Логирование всех операций
    - Обработка ошибок API
    """
    
    def __init__(self, tone: str, topic: str, openai_key: Optional[str] = None, model: str = "gpt-5"):
        """
        Инициализация генератора текста
        
        Args:
            tone (str): Тон поста (например, "дружелюбный", "профессиональный")
            topic (str): Тема поста
            openai_key (Optional[str]): API ключ OpenAI (если не указан, берется из конфига)
            model (str): Модель OpenAI для генерации (по умолчанию "gpt-5")
        
        Raises:
            ValueError: При некорректных входных данных
        """
        # Валидация входных данных
        if not tone or not isinstance(tone, str) or len(tone.strip()) == 0:
            raise ValueError("Тон поста не может быть пустым")
        
        if not topic or not isinstance(topic, str) or len(topic.strip()) == 0:
            raise ValueError("Тема поста не может быть пустой")
        
        self.tone = tone.strip()
        self.topic = topic.strip()
        self.model = model
        
        # Валидация модели
        valid_models = ["gpt-5", "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        if model not in valid_models:
            logger.warning(f"Модель '{model}' не в списке рекомендуемых: {valid_models}")
        
        # Получаем API ключ из конфига или параметра
        if openai_key:
            self.openai_key = openai_key
        else:
            self.openai_key = config.openai_api_key
        
        # Если модель не указана, берем из конфига
        if model == "gpt-5" and hasattr(config, 'openai_text_model'):
            self.model = config.openai_text_model
        
        # Настройка клиента OpenAI (новый API)
        self.client = openai.OpenAI(api_key=self.openai_key)
        
        logger.info(
            "[TextGenerator.__init__] initialized extra=%s",
            {"topic": self.topic, "tone": self.tone, "model": self.model},
        )
    
    def generate_post(self) -> Optional[str]:
        """
        Генерирует текст поста на заданную тему в указанном тоне
        
        Returns:
            Optional[str]: Сгенерированный текст поста или None в случае ошибки
        """
        try:
            logger.info(
                "[TextGenerator.generate_post] start extra=%s",
                {"topic": self.topic, "tone": self.tone, "model": self.model},
            )
            
            prompt = f"Ты SMM-специалист, генерируй пост на тему {self.topic} в {self.tone} тоне"
            
            # Используем новый API OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты опытный SMM-специалист, который создает качественные посты для социальных сетей."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            generated_text = response.choices[0].message.content.strip()
            logger.info(
                "[TextGenerator.generate_post] completed extra=%s",
                {"length": len(generated_text), "model": self.model},
            )
            return generated_text
            
        except openai.AuthenticationError as e:
            error_msg = f"Ошибка аутентификации OpenAI: {e}"
            logger.error("[TextGenerator.generate_post] authentication error extra=%s", {"error": str(e)})
            return None
        except openai.RateLimitError as e:
            error_msg = f"Превышен лимит запросов OpenAI: {e}"
            logger.error("[TextGenerator.generate_post] rate limit extra=%s", {"error": str(e)})
            return None
        except openai.APIError as e:
            error_msg = f"Ошибка OpenAI API: {e}"
            logger.error("[TextGenerator.generate_post] api error extra=%s", {"error": str(e)})
            return None
        except Exception as e:
            error_msg = f"Неожиданная ошибка при генерации текста: {e}"
            logger.exception(
                "[TextGenerator.generate_post] unexpected error extra=%s",
                {"error": str(e), "topic": self.topic},
            )
            return None
