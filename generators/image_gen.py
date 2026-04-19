"""Модуль для генерации изображений через OpenAI Images API."""

from __future__ import annotations

import logging
from typing import Optional

import openai

from config import config


logger = logging.getLogger(__name__)


def _configured_model(name: str, default: str) -> str:
    value = getattr(config, name, None)
    return value if isinstance(value, str) and value.strip() else default


class ImageGenerator:
    """
    Класс для генерации изображений с использованием DALL-E 3 API
    
    БЕЗОПАСНОСТЬ:
    - API ключ загружается из переменных окружения
    - Валидация входных данных
    - Логирование всех операций
    - Обработка ошибок API
    """
    
    def __init__(self, openai_key: Optional[str] = None, model: Optional[str] = None, timeout: Optional[int] = None):
        """
        Инициализация генератора изображений
        
        Args:
            openai_key (Optional[str]): API ключ OpenAI (если не указан, берется из конфига)
            model (str): Модель OpenAI для генерации изображений (по умолчанию "dall-e-3")
        
        Raises:
            ValueError: При некорректных входных данных
        """
        resolved_model = model or _configured_model('openai_image_model', 'dall-e-3')
        self.model = resolved_model
        self.timeout = timeout if timeout is not None else getattr(config, 'request_timeout', config.timeout)
        
        # Валидация модели
        valid_models = ["dall-e-3", "dall-e-2"]
        if self.model not in valid_models:
            logger.warning(f"Модель '{self.model}' не в списке рекомендуемых: {valid_models}")
        
        # Получаем API ключ из конфига или параметра
        if openai_key:
            self.openai_key = openai_key
        else:
            self.openai_key = config.openai_api_key

        if self.openai_key:
            self.client = openai.OpenAI(api_key=self.openai_key, timeout=self.timeout)
        else:
            self.client = None
            logger.warning(
                "[ImageGenerator.__init__] openai disabled extra=%s",
                {"model": self.model, "timeout": self.timeout},
            )

        logger.info(
            "[ImageGenerator.__init__] initialized extra=%s",
            {"model": self.model, "timeout": self.timeout},
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

        if self.client is None:
            logger.warning(
                "[ImageGenerator.generate_image] skipped missing openai key extra=%s",
                {"model": self.model},
            )
            return None

        try:
            logger.info(
                "[ImageGenerator.generate_image] start extra=%s",
                {"model": self.model, "prompt_preview": prompt[:80], "timeout": self.timeout},
            )

            logger.info(
                "[ImageGenerator.generate_image] requesting openai image extra=%s",
                {"model": self.model, "timeout": self.timeout},
            )
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
            logger.error("[ImageGenerator.generate_image] authentication error extra=%s", {"error": str(e)})
            return None
        except openai.RateLimitError as e:
            logger.error("[ImageGenerator.generate_image] rate limit extra=%s", {"error": str(e)})
            return None
        except openai.BadRequestError as e:
            logger.error("[ImageGenerator.generate_image] bad request extra=%s", {"error": str(e)})
            return None
        except openai.APIError as e:
            logger.error("[ImageGenerator.generate_image] api error extra=%s", {"error": str(e)})
            return None
        except Exception as e:
            logger.exception(
                "[ImageGenerator.generate_image] unexpected error extra=%s",
                {"error": str(e), "model": self.model},
            )
            return None
