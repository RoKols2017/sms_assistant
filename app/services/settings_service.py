from __future__ import annotations

import logging
from datetime import datetime, UTC

from app.extensions import db
from app.models.user import User
from app.models.vk_settings import VKSettings


logger = logging.getLogger(__name__)


class SettingsService:
    def get_or_create_vk_settings(self, user: User) -> VKSettings:
        logger.info(
            "[SettingsService.get_or_create_vk_settings] start extra=%s",
            {"user_id": user.id},
        )
        if user.vk_settings is None:
            user.vk_settings = VKSettings(user=user, vk_api_key="", vk_group_id=0)
        return user.vk_settings

    def save_vk_settings(
        self,
        user: User,
        vk_api_key: str,
        vk_group_id: int,
        validation_status: str = "unknown",
        validation_message: str | None = None,
        can_access_group: bool | None = None,
        can_post_to_wall: bool | None = None,
        can_upload_wall_photo: bool | None = None,
    ) -> VKSettings:
        logger.info(
            "[SettingsService.save_vk_settings] start extra=%s",
            {"user_id": user.id, "vk_group_id": vk_group_id, "validation_status": validation_status},
        )

        settings = user.vk_settings or VKSettings(user=user, vk_api_key=vk_api_key, vk_group_id=vk_group_id)
        settings.vk_api_key = vk_api_key.strip()
        settings.vk_group_id = vk_group_id
        settings.validation_status = validation_status
        settings.validation_message = validation_message
        settings.can_access_group = can_access_group
        settings.can_post_to_wall = can_post_to_wall
        settings.can_upload_wall_photo = can_upload_wall_photo
        settings.last_validated_at = datetime.now(UTC)

        db.session.add(settings)
        db.session.commit()

        logger.info(
            "[SettingsService.save_vk_settings] completed extra=%s",
            {"user_id": user.id, "settings_id": settings.id, "validation_status": settings.validation_status},
        )
        return settings
