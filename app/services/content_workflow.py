from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from app.extensions import db
from app.models.generated_post import GeneratedPost
from app.models.user import User
from app.services.openai_service import OpenAIService
from app.services.vk_service import VKService


logger = logging.getLogger(__name__)


@dataclass
class ContentWorkflowResult:
    generated_post: GeneratedPost
    vk_warning: Optional[str] = None


class ContentWorkflowService:
    def __init__(self) -> None:
        self.openai_service = OpenAIService()
        self.vk_service = VKService()

    def generate_for_user(
        self,
        user: User,
        tone: str,
        topic: str,
        generate_image: bool,
        auto_post_vk: bool,
    ) -> ContentWorkflowResult:
        logger.info(
            "[ContentWorkflowService.generate_for_user] start extra=%s",
            {
                "user_id": user.id,
                "tone": tone,
                "topic": topic,
                "generate_image": generate_image,
                "auto_post_vk": auto_post_vk,
            },
        )

        try:
            post_text = self.openai_service.generate_post(tone=tone, topic=topic)
            image_url = None
            if generate_image:
                image_prompt = f"Create a social media illustration about {topic}. Tone: {tone}."
                image_url = self.openai_service.generate_image(image_prompt)

            settings = user.vk_settings if auto_post_vk else None

            generated_post = GeneratedPost(
                user=user,
                tone=tone,
                topic=topic,
                generated_text=post_text,
                image_url=image_url,
                generate_image_requested=generate_image,
                auto_post_vk_requested=auto_post_vk,
                vk_publish_status="not_requested",
            )

            vk_warning = None
            if auto_post_vk:
                vk_image_url = image_url
                if not settings or not settings.vk_api_key or not settings.vk_group_id:
                    generated_post.vk_publish_status = "skipped"
                    generated_post.vk_publish_message = "VK settings are missing."
                    vk_warning = "Пост сгенерирован, но автопостинг в VK пропущен: настройки VK не заполнены."
                elif settings.can_access_group is False:
                    generated_post.vk_publish_status = "skipped"
                    generated_post.vk_publish_message = "VK group access validation failed."
                    vk_warning = "Контент успешно сгенерирован, но автопостинг в VK пропущен: нет доступа к группе VK."
                elif settings.can_post_to_wall is False:
                    generated_post.vk_publish_status = "skipped"
                    generated_post.vk_publish_message = "VK group settings indicate posting to wall is disabled."
                    vk_warning = "Контент успешно сгенерирован, но автопостинг в VK пропущен: в настройках группы публикация на стену недоступна."
                else:
                    if generate_image and settings.can_upload_wall_photo is False:
                        vk_image_url = None
                        vk_warning = (
                            "Контент успешно сгенерирован и опубликован в VK без изображения: для token недоступна загрузка wall photo."
                        )
                    publish_result = self.vk_service.publish_post(
                        token=settings.vk_api_key,
                        group_id=settings.vk_group_id,
                        text=post_text,
                        image_url=vk_image_url,
                    )
                    if publish_result and publish_result.get("post_id") is not None:
                        generated_post.vk_publish_status = "published"
                        generated_post.vk_publish_message = (
                            "Пост опубликован в VK без изображения."
                            if image_url and vk_image_url is None
                            else "Пост опубликован в VK."
                        )
                        generated_post.vk_post_id = int(publish_result["post_id"])
                    else:
                        generated_post.vk_publish_status = "failed"
                        generated_post.vk_publish_message = "VK не принял публикацию или token не имеет нужных прав."
                        vk_warning = (
                            "Контент успешно сгенерирован, но автопостинг в VK не выполнен. Проверьте права token `wall` и `photos`."
                        )

            db.session.add(generated_post)
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception(
                "[ContentWorkflowService.generate_for_user] failed extra=%s",
                {"user_id": user.id, "topic": topic, "auto_post_vk": auto_post_vk},
            )
            raise

        logger.info(
            "[ContentWorkflowService.generate_for_user] completed extra=%s",
            {"user_id": user.id, "generated_post_id": generated_post.id, "vk_status": generated_post.vk_publish_status},
        )
        return ContentWorkflowResult(generated_post=generated_post, vk_warning=vk_warning)
