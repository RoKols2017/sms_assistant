from __future__ import annotations

import logging

from flask import current_app

from generators.image_gen import ImageGenerator
from generators.text_gen import TextGenerator


logger = logging.getLogger(__name__)


class OpenAIService:
    def generate_post(self, tone: str, topic: str) -> str:
        logger.info("[OpenAIService.generate_post] start extra=%s", {"tone": tone, "topic": topic})
        generator = TextGenerator(
            tone=tone,
            topic=topic,
            openai_key=current_app.config.get("OPENAI_API_KEY"),
            model=current_app.config.get("OPENAI_TEXT_MODEL"),
            timeout=current_app.config.get("REQUEST_TIMEOUT"),
        )
        result = generator.generate_post()
        if not result:
            raise RuntimeError("Не удалось сгенерировать текст поста.")
        logger.info("[OpenAIService.generate_post] completed extra=%s", {"topic": topic, "length": len(result)})
        return result

    def generate_image(self, prompt: str) -> str:
        logger.info("[OpenAIService.generate_image] start extra=%s", {"prompt_preview": prompt[:80]})
        generator = ImageGenerator(
            openai_key=current_app.config.get("OPENAI_API_KEY"),
            model=current_app.config.get("OPENAI_IMAGE_MODEL"),
            timeout=current_app.config.get("REQUEST_TIMEOUT"),
        )
        result = generator.generate_image(prompt)
        if not result:
            raise RuntimeError("Не удалось сгенерировать изображение.")
        logger.info("[OpenAIService.generate_image] completed extra=%s", {"has_url": bool(result)})
        return result
