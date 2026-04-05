from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from app.models.user import User
from app.services.vk_service import VKService


logger = logging.getLogger(__name__)


@dataclass
class VKStatsResult:
    group_name: Optional[str]
    members_count: Optional[int]
    validation_message: Optional[str]


class StatsService:
    def __init__(self) -> None:
        self.vk_service = VKService()

    def get_vk_stats_for_user(self, user: User) -> VKStatsResult:
        logger.info("[StatsService.get_vk_stats_for_user] start extra=%s", {"user_id": user.id})
        settings = user.vk_settings
        if not settings:
            return VKStatsResult(None, None, "Сначала заполните VK settings.")

        group_info = self.vk_service.get_group_info(
            token=settings.vk_api_key,
            group_id=settings.vk_group_id,
            fields=["members_count"],
        )
        members_count = self.vk_service.extract_members_count(
            payload=group_info,
            fallback_group_id=settings.vk_group_id,
            token=settings.vk_api_key,
        )
        result = VKStatsResult(
            group_name=group_info.get("name") if group_info else None,
            members_count=members_count,
            validation_message=settings.validation_message,
        )
        logger.info(
            "[StatsService.get_vk_stats_for_user] completed extra=%s",
            {"user_id": user.id, "members_count": members_count},
        )
        return result
