"""Legacy-compatible environment configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


def _to_optional_int(raw_value: Optional[str], field_name: str) -> Optional[int]:
    if raw_value in (None, ""):
        return None

    try:
        return int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} должен быть числом") from exc


@dataclass
class Config:
    """Legacy config used by existing modules and tests.

    `strict=True` keeps the old behavior for direct config validation in tests.
    The module-level `config` instance uses `strict=False` so importing legacy
    modules does not break the Flask app before runtime settings are configured.
    """

    strict: bool = True

    def __post_init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.vk_token = os.getenv("VK_TOKEN")
        self.vk_group_id = _to_optional_int(os.getenv("VK_GROUP_ID"), "VK_GROUP_ID")
        self.telegram_token = os.getenv("TG_TOKEN")
        self.telegram_chat_id = os.getenv("TG_CHAT_ID")

        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("TIMEOUT", "30"))
        self.openai_text_model = os.getenv("OPENAI_TEXT_MODEL", "gpt-5")
        self.openai_image_model = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")
        self.vk_api_version = os.getenv("VK_API_VERSION", "5.139")

        if self.strict:
            self._validate_required_values()

    def _validate_required_values(self) -> None:
        missing = [
            name
            for name, value in {
                "OPENAI_API_KEY": self.openai_api_key,
                "VK_TOKEN": self.vk_token,
                "VK_GROUP_ID": self.vk_group_id,
                "TG_TOKEN": self.telegram_token,
                "TG_CHAT_ID": self.telegram_chat_id,
            }.items()
            if value in (None, "")
        ]

        if missing:
            raise ValueError(
                "Отсутствуют обязательные переменные окружения: " + ", ".join(missing)
            )


config = Config(strict=False)
