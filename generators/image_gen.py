"""Модуль для генерации изображений через OpenAI Images API."""

from __future__ import annotations

import logging
from typing import Optional

import openai

from config import config


logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    Класс для генерации изображений с использованием DALL-E 3 API
    
    БЕЗОПАСНОСТЬ:
    - API ключ загружается из переменных окружения
    - Валидация входных данных
    - Логирование всех операций
    - Обработка ошибок API
    """
    
    def __init__(self, openai_key: Optional[str] = None, model: str = "dall-e-3"):
        """
        Инициализация генератора изображений
        
        Args:
            openai_key (Optional[str]): API ключ OpenAI (если не указан, берется из конфига)
            model (str): Модель OpenAI для генерации изображений (по умолчанию "dall-e-3")
        
        Raises:
            ValueError: При некорректных входных данных
        """
        self.model = model
        
        # Валидация модели
        valid_models = ["dall-e-3", "dall-e-2"]
        if model not in valid_models:
            logger.warning(f"Модель '{model}' не в списке рекомендуемых: {valid_models}")
        
        # Получаем API ключ из конфига или параметра
        if openai_key:
            self.openai_key = openai_key
        else:
            self.openai_key = config.openai_api_key
        
        # Если модель не указана, берем из конфига
        if model == "dall-e-3" and hasattr(config, 'openai_image_model'):
            self.model = config.openai_image_model
        
        # Настройка клиента OpenAI (новый API)
        self.client = openai.OpenAI(api_key=self.openai_key)
        
        logger.info(
            "[ImageGenerator.__init__] initialized extra=%s",
            {"model": self.model},
        )
    
    def generate_image(self, prompt: str) -> Optional[str]:
        """
        Генерирует изображение по заданному промпту
        
        Args:
            prompt (str): Текстовое описание изображения
            
        Returns:
            Optional[str]: URL сгенерированного изображения или None в случае ошибки
        """
        # Валидация входных данных
        if not prompt or not isinstance(prompt, str) or len(prompt.strip()) == 0:
            logger.error("Промпт для генерации изображения не может быть пустым")
            return None
        
        if len(prompt) > 1000:
            logger.warning("Промпт слишком длинный, обрезаем до 1000 символов")
            prompt = prompt[:1000]
        
        try:
            logger.info(
                "[ImageGenerator.generate_image] start extra=%s",
                {"model": self.model, "prompt_preview": prompt[:80]},
            )
            
            # Используем новый API OpenAI
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(
                "[ImageGenerator.generate_image] completed extra=%s",
                {"model": self.model, "has_url": bool(image_url)},
            )
            return image_url
            
        except openai.AuthenticationError as e:
            error_msg = f"Ошибка аутентификации OpenAI: {e}"
            logger.error("[ImageGenerator.generate_image] authentication error extra=%s", {"error": str(e)})
            return None
        except openai.RateLimitError as e:
            error_msg = f"Превышен лимит запросов OpenAI: {e}"
            logger.error("[ImageGenerator.generate_image] rate limit extra=%s", {"error": str(e)})
            return None
        except openai.BadRequestError as e:
            error_msg = f"Неверный запрос к API: {e}"
            logger.error("[ImageGenerator.generate_image] bad request extra=%s", {"error": str(e)})
            return None
        except openai.APIError as e:
            error_msg = f"Ошибка OpenAI API: {e}"
            logger.error("[ImageGenerator.generate_image] api error extra=%s", {"error": str(e)})
            return None
        except Exception as e:
            error_msg = f"Неожиданная ошибка при генерации изображения: {e}"
            logger.exception(
                "[ImageGenerator.generate_image] unexpected error extra=%s",
                {"error": str(e), "model": self.model},
            )
            return None
