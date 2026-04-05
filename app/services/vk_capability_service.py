from __future__ import annotations

import logging
from dataclasses import dataclass

from app.services.vk_service import VKService


logger = logging.getLogger(__name__)


@dataclass
class VKCapabilityResult:
    validation_status: str
    validation_message: str
    can_access_group: bool | None
    can_post_to_wall: bool | None
    can_upload_wall_photo: bool | None


class VKCapabilityService:
    def __init__(self) -> None:
        self.vk_service = VKService()

    def validate(self, token: str, group_id: int) -> VKCapabilityResult:
        logger.info(
            "[VKCapabilityService.validate] start extra=%s",
            {"group_id": group_id, "token_length": len(token or "")},
        )
        if not token or len(token.strip()) < 10:
            return VKCapabilityResult(
                validation_status="invalid",
                validation_message="Похоже, VK token заполнен некорректно.",
                can_access_group=False,
                can_post_to_wall=False,
                can_upload_wall_photo=False,
            )

        group_info = self.vk_service.get_group_info(
            token=token,
            group_id=group_id,
            fields=["members_count", "can_post"],
        )
        if not group_info:
            return VKCapabilityResult(
                validation_status="invalid",
                validation_message="Не удалось получить информацию о группе VK. Проверьте token и group id.",
                can_access_group=False,
                can_post_to_wall=False,
                can_upload_wall_photo=False,
            )

        can_post_from_group_settings = group_info.get("can_post")
        can_upload_wall_photo = self.vk_service.probe_wall_upload_access(token=token, group_id=group_id)

        validation_status = "validated"
        validation_message = (
            "Проверка VK прошла успешно. Доступ к группе подтвержден. "
            "Право `photos` проверено через wall upload probe. Право `wall` VK не позволяет надежно проверить без реальной публикации, "
            "поэтому финальная попытка автопостинга все равно выполняется в best-effort режиме."
        )

        if can_post_from_group_settings is False:
            validation_status = "limited"
            validation_message = (
                "Группа доступна, но поле `can_post` показывает, что публикация на стену ограничена настройками сообщества."
            )
        elif not can_upload_wall_photo:
            validation_status = "limited"
            validation_message = (
                "Группа доступна, но право загрузки wall photo недоступно. Автопостинг с изображением будет пропущен."
            )

        result = VKCapabilityResult(
            validation_status=validation_status,
            validation_message=validation_message,
            can_access_group=True,
            can_post_to_wall=bool(can_post_from_group_settings) if can_post_from_group_settings is not None else None,
            can_upload_wall_photo=can_upload_wall_photo,
        )
        logger.info(
            "[VKCapabilityService.validate] completed extra=%s",
            {
                "group_id": group_id,
                "status": result.validation_status,
                "can_post_to_wall": result.can_post_to_wall,
                "can_upload_wall_photo": result.can_upload_wall_photo,
            },
        )
        return result
