from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from flask import current_app

from social_publishers.vk_publisher import VKPublisher
from social_stats.stats_collector import StatsCollector


logger = logging.getLogger(__name__)


class VKService:
    def _api_version(self) -> str:
        return current_app.config.get("VK_API_VERSION", "5.139")

    def get_group_info(self, token: str, group_id: int, fields: Optional[list[str]] = None) -> Optional[Dict[str, Any]]:
        logger.info(
            "[VKService.get_group_info] start extra=%s",
            {"group_id": group_id, "fields": fields or [], "api_version": self._api_version()},
        )
        collector = StatsCollector(vk_access_token=token, api_version=self._api_version())
        return collector.get_group_info(group_id, fields=fields)

    def extract_members_count(self, payload: Optional[Dict[str, Any]], fallback_group_id: int, token: str) -> Optional[int]:
        if payload and payload.get("members_count") is not None:
            return int(payload["members_count"])

        collector = StatsCollector(
            vk_access_token=token,
            api_version=self._api_version(),
            timeout=current_app.config.get("REQUEST_TIMEOUT"),
        )
        return collector.get_group_members_count(fallback_group_id)

    def publish_post(self, token: str, group_id: int, text: str, image_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        logger.info(
            "[VKService.publish_post] start extra=%s",
            {"group_id": group_id, "has_image": bool(image_url), "api_version": self._api_version()},
        )
        publisher = VKPublisher(
            access_token=token,
            group_id=group_id,
            api_version=self._api_version(),
            timeout=current_app.config.get("REQUEST_TIMEOUT"),
        )
        return publisher.publish_post(text=text, image_url=image_url)

    def probe_wall_upload_access(self, token: str, group_id: int) -> bool:
        logger.info(
            "[VKService.probe_wall_upload_access] start extra=%s",
            {"group_id": group_id, "api_version": self._api_version()},
        )
        publisher = VKPublisher(
            access_token=token,
            group_id=group_id,
            api_version=self._api_version(),
            timeout=current_app.config.get("REQUEST_TIMEOUT"),
        )
        return publisher.probe_wall_upload_access()
