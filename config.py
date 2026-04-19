"""Legacy compatibility layer around the canonical Flask config module."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import get_env_int, get_env_optional_int


@dataclass
class Config:
    """Legacy config used by existing modules and tests.

    `strict=True` keeps the old behavior for direct config validation in tests.
    The module-level `config` instance uses `strict=False` so importing legacy
    modules does not break the Flask app before runtime settings are configured.
    """

    strict: bool = True

    def __post_init__(self) -> None:
        from app.config import BaseConfig

        runtime_config = BaseConfig.build()

        self.openai_api_key = runtime_config["OPENAI_API_KEY"]
        self.vk_token = runtime_config["VK_TOKEN"]
        self.vk_group_id = get_env_optional_int("VK_GROUP_ID")
        self.telegram_token = runtime_config["TG_TOKEN"]
        self.telegram_chat_id = runtime_config["TG_CHAT_ID"]

        self.log_level = runtime_config["LOG_LEVEL"]
        self.max_retries = get_env_int("MAX_RETRIES", 3)
        legacy_timeout = get_env_int("TIMEOUT", runtime_config["REQUEST_TIMEOUT"])
        self.timeout = legacy_timeout
        self.request_timeout = runtime_config["REQUEST_TIMEOUT"]
        self.openai_text_model = runtime_config["OPENAI_TEXT_MODEL"]
        self.openai_image_model = runtime_config["OPENAI_IMAGE_MODEL"]
        self.vk_api_version = runtime_config["VK_API_VERSION"]

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
