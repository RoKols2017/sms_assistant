"""
Модуль для публикации постов в ВКонтакте через VK API
"""

import vk_api
import requests
from typing import Optional, Dict, Any
import logging


class VKPublisher:
    """
    Класс для публикации постов в ВКонтакте
    """
    
    def __init__(self, access_token: str, group_id: int):
        """
        Инициализация публикатора ВК
        
        Args:
            access_token (str): Токен доступа ВК
            group_id (int): ID группы для публикации
        """
        self.access_token = access_token
        self.group_id = group_id
        
        # Инициализация VK API
        self.vk_session = vk_api.VkApi(token=access_token)
        self.vk = self.vk_session.get_api()
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def upload_image(self, image_url: str) -> Optional[str]:
        """
        Загружает изображение в ВК и возвращает attachment
        
        Args:
            image_url (str): URL изображения для загрузки
            
        Returns:
            Optional[str]: Attachment строка для использования в посте или None в случае ошибки
        """
        try:
            self.logger.info(f"Загрузка изображения: {image_url}")
            
            # Получаем адрес сервера для загрузки
            upload_server = self.vk.photos.getWallUploadServer(group_id=self.group_id)
            upload_url = upload_server['upload_url']
            
            # Скачиваем изображение
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Загружаем на сервер ВК
            files = {'photo': ('image.jpg', response.content, 'image/jpeg')}
            upload_response = requests.post(upload_url, files=files)
            upload_response.raise_for_status()
            
            upload_data = upload_response.json()
            
            # Сохраняем фото в альбом группы
            photo_data = self.vk.photos.saveWallPhoto(
                group_id=self.group_id,
                photo=upload_data['photo'],
                server=upload_data['server'],
                hash=upload_data['hash']
            )
            
            # Формируем attachment
            photo = photo_data[0]
            attachment = f"photo{photo['owner_id']}_{photo['id']}"
            
            self.logger.info(f"Изображение успешно загружено: {attachment}")
            return attachment
            
        except requests.RequestException as e:
            error_msg = f"Ошибка при скачивании изображения: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
        except vk_api.exceptions.ApiError as e:
            error_msg = f"Ошибка VK API при загрузке изображения: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
        except Exception as e:
            error_msg = f"Неожиданная ошибка при загрузке изображения: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
    
    def publish_post(self, text: str, image_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Публикует пост в группу ВК
        
        Args:
            text (str): Текст поста
            image_url (Optional[str]): URL изображения для прикрепления
            
        Returns:
            Optional[Dict[str, Any]]: Данные опубликованного поста или None в случае ошибки
        """
        try:
            self.logger.info(f"Публикация поста в группу {self.group_id}")
            
            attachments = []
            
            # Если есть изображение, загружаем его
            if image_url:
                attachment = self.upload_image(image_url)
                if attachment:
                    attachments.append(attachment)
                else:
                    self.logger.warning("Не удалось загрузить изображение, публикуем без него")
            
            # Публикуем пост
            post_data = self.vk.wall.post(
                owner_id=-self.group_id,  # Отрицательный ID для группы
                message=text,
                attachments=','.join(attachments) if attachments else None,
                from_group=1  # Публикация от имени группы
            )
            
            self.logger.info(f"Пост успешно опубликован, ID: {post_data['post_id']}")
            return post_data
            
        except vk_api.exceptions.ApiError as e:
            error_msg = f"Ошибка VK API при публикации: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None
        except Exception as e:
            error_msg = f"Неожиданная ошибка при публикации: {e}"
            self.logger.error(error_msg)
            print(error_msg)
            return None


if __name__ == "__main__":
    # Тестирование класса
    print("Тестирование VKPublisher...")
    
    # Замените на ваши реальные данные для тестирования
    test_token = "your-vk-access-token-here"
    test_group_id = 123456789  # ID вашей группы
    
    publisher = VKPublisher(
        access_token=test_token,
        group_id=test_group_id
    )
    
    # Тестовый пост
    test_text = "Тестовый пост от SMM-бота! 🤖"
    test_image_url = "https://example.com/image.jpg"  # Замените на реальный URL
    
    # Публикация поста с изображением
    result = publisher.publish_post(test_text, test_image_url)
    if result:
        print(f"Пост успешно опубликован! ID: {result.get('post_id')}")
    else:
        print("Не удалось опубликовать пост")
    
    # Публикация поста без изображения
    result_text_only = publisher.publish_post("Пост только с текстом")
    if result_text_only:
        print(f"Текстовый пост опубликован! ID: {result_text_only.get('post_id')}")
    else:
        print("Не удалось опубликовать текстовый пост")
