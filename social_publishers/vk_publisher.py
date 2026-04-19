import logging
from typing import Any, Dict, Optional

import requests
import vk_api

from config import config


logger = logging.getLogger(__name__)


class VKPublisher:
    """
    Класс для публикации постов в ВКонтакте
    """
    
    def __init__(self, access_token: str, group_id: int, api_version: Optional[str] = None, timeout: Optional[int] = None):
        """
        Инициализация публикатора ВК
        
        Args:
            access_token (str): Токен доступа ВК
            group_id (int): ID группы для публикации
        """
        self.access_token = access_token
        self.group_id = group_id
        self.api_version = api_version or config.vk_api_version
        self.timeout = timeout if timeout is not None else getattr(config, "request_timeout", config.timeout)

        if not access_token or not group_id:
            self.vk_session = None
            self.vk = None
            logger.warning(
                "[VKPublisher.__init__] vk disabled extra=%s",
                {"has_token": bool(access_token), "group_id": group_id, "timeout": self.timeout},
            )
            return

        self.vk_session = vk_api.VkApi(token=access_token, api_version=self.api_version)
        self.vk = self.vk_session.get_api()
        logger.info(
            "[VKPublisher.__init__] initialized extra=%s",
            {"group_id": self.group_id, "api_version": self.api_version, "timeout": self.timeout},
        )

    def _has_client(self, method_name: str) -> bool:
        if self.vk is None:
            logger.warning(
                "[%s] vk client unavailable extra=%s",
                method_name,
                {"group_id": self.group_id},
            )
            return False
        return True
    
    def upload_image(self, image_url: str) -> Optional[str]:
        """
        Загружает изображение в ВК и возвращает attachment
        
        Args:
            image_url (str): URL изображения для загрузки
            
        Returns:
            Optional[str]: Attachment строка для использования в посте или None в случае ошибки
        """
        if not self._has_client("VKPublisher.upload_image"):
            return None

        try:
            logger.info(
                "[VKPublisher.upload_image] start extra=%s",
                {"group_id": self.group_id, "image_url": image_url, "api_version": self.api_version},
            )
            
            upload_server = self.vk.photos.getWallUploadServer(group_id=self.group_id)
            upload_url = upload_server['upload_url']

            logger.info(
                "[VKPublisher.upload_image] downloading source image extra=%s",
                {"group_id": self.group_id, "timeout": self.timeout},
            )
            response = requests.get(image_url, timeout=self.timeout)
            response.raise_for_status()

            files = {'photo': ('image.jpg', response.content, 'image/jpeg')}
            logger.info(
                "[VKPublisher.upload_image] uploading image to vk extra=%s",
                {"group_id": self.group_id, "timeout": self.timeout},
            )
            upload_response = requests.post(upload_url, files=files, timeout=self.timeout)
            upload_response.raise_for_status()

            upload_data = upload_response.json()

            photo_data = self.vk.photos.saveWallPhoto(
                group_id=self.group_id,
                photo=upload_data['photo'],
                server=upload_data['server'],
                hash=upload_data['hash']
            )

            photo = photo_data[0]
            attachment = f"photo{photo['owner_id']}_{photo['id']}"

            logger.info(
                "[VKPublisher.upload_image] completed extra=%s",
                {"group_id": self.group_id, "attachment": attachment},
            )
            return attachment

        except requests.RequestException as e:
            logger.error("[VKPublisher.upload_image] request error extra=%s", {"error": str(e), "group_id": self.group_id})
            return None
        except vk_api.exceptions.ApiError as e:
            logger.error("[VKPublisher.upload_image] vk api error extra=%s", {"error": str(e), "group_id": self.group_id})
            return None
        except Exception as e:
            logger.exception(
                "[VKPublisher.upload_image] unexpected error extra=%s",
                {"error": str(e), "group_id": self.group_id},
            )
            return None

    def probe_wall_upload_access(self) -> bool:
        if not self._has_client("VKPublisher.probe_wall_upload_access"):
            return False

        try:
            logger.info(
                "[VKPublisher.probe_wall_upload_access] start extra=%s",
                {"group_id": self.group_id, "api_version": self.api_version},
            )
            self.vk.photos.getWallUploadServer(group_id=self.group_id)
            logger.info(
                "[VKPublisher.probe_wall_upload_access] completed extra=%s",
                {"group_id": self.group_id, "result": True},
            )
            return True
        except vk_api.exceptions.ApiError as e:
            logger.warning(
                "[VKPublisher.probe_wall_upload_access] vk api denied extra=%s",
                {"group_id": self.group_id, "error": str(e)},
            )
            return False
        except Exception as e:
            logger.exception(
                "[VKPublisher.probe_wall_upload_access] unexpected error extra=%s",
                {"group_id": self.group_id, "error": str(e)},
            )
            return False
    
    def publish_post(self, text: str, image_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Публикует пост в группу ВК
        
        Args:
            text (str): Текст поста
            image_url (Optional[str]): URL изображения для прикрепления
            
        Returns:
            Optional[Dict[str, Any]]: Данные опубликованного поста или None в случае ошибки
        """
        if not self._has_client("VKPublisher.publish_post"):
            return None

        try:
            logger.info(
                "[VKPublisher.publish_post] start extra=%s",
                {"group_id": self.group_id, "has_image": bool(image_url), "api_version": self.api_version},
            )
            
            attachments = []

            if image_url:
                attachment = self.upload_image(image_url)
                if attachment:
                    attachments.append(attachment)
                else:
                    logger.warning(
                        "[VKPublisher.publish_post] image upload failed, continuing without image extra=%s",
                        {"group_id": self.group_id},
                    )
            
            post_data = self.vk.wall.post(
                owner_id=-self.group_id,  # Отрицательный ID для группы
                message=text,
                attachments=','.join(attachments) if attachments else None,
                from_group=1  # Публикация от имени группы
            )

            logger.info(
                "[VKPublisher.publish_post] completed extra=%s",
                {"group_id": self.group_id, "post_id": post_data.get('post_id')},
            )
            return post_data

        except vk_api.exceptions.ApiError as e:
            logger.error("[VKPublisher.publish_post] vk api error extra=%s", {"error": str(e), "group_id": self.group_id})
            return None
        except Exception as e:
            logger.exception(
                "[VKPublisher.publish_post] unexpected error extra=%s",
                {"error": str(e), "group_id": self.group_id},
            )
            return None
