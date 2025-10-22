"""
Тесты для VK публикатора
"""

import pytest
from unittest.mock import patch, MagicMock
from social_publishers.vk_publisher import VKPublisher


class TestVKPublisher:
    """Тесты для класса VKPublisher"""
    
    def test_init_success(self):
        """Тест успешной инициализации"""
        with patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api:
            mock_session = MagicMock()
            mock_vk_api.return_value = mock_session
            
            publisher = VKPublisher(
                access_token="test-token",
                group_id=123456789
            )
            
            assert publisher.access_token == "test-token"
            assert publisher.group_id == 123456789
    
    @patch('social_publishers.vk_publisher.requests.get')
    @patch('social_publishers.vk_publisher.requests.post')
    def test_upload_image_success(self, mock_post, mock_get):
        """Тест успешной загрузки изображения"""
        # Настройка моков
        mock_get.return_value.content = b"image_data"
        mock_get.return_value.raise_for_status.return_value = None
        
        mock_post.return_value.json.return_value = {
            'photo': 'test_photo',
            'server': 'test_server',
            'hash': 'test_hash'
        }
        mock_post.return_value.raise_for_status.return_value = None
        
        with patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api:
            mock_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.photos.getWallUploadServer.return_value = {'upload_url': 'http://test.com/upload'}
            mock_vk.photos.saveWallPhoto.return_value = [{'owner_id': 123, 'id': 456}]
            mock_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_session
            
            publisher = VKPublisher("test-token", 123456)
            
            result = publisher.upload_image("http://example.com/image.jpg")
            
            assert result == "photo123_456"
            mock_get.assert_called_once_with("http://example.com/image.jpg")
            mock_post.assert_called_once()
    
    @patch('social_publishers.vk_publisher.requests.get')
    def test_upload_image_download_error(self, mock_get):
        """Тест ошибки скачивания изображения"""
        mock_get.side_effect = Exception("Download failed")
        
        with patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api:
            mock_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.photos.getWallUploadServer.return_value = {'upload_url': 'http://test.com/upload'}
            mock_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_session
            
            publisher = VKPublisher("test-token", 123456)
            
            result = publisher.upload_image("http://example.com/image.jpg")
            
            assert result is None
    
    def test_upload_image_vk_api_error(self):
        """Тест ошибки VK API при загрузке"""
        with patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api:
            mock_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.photos.getWallUploadServer.side_effect = Exception("VK API error")
            mock_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_session
            
            publisher = VKPublisher("test-token", 123456)
            
            result = publisher.upload_image("http://example.com/image.jpg")
            
            assert result is None
    
    def test_publish_post_text_only(self):
        """Тест публикации только текста"""
        with patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api:
            mock_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.post.return_value = {'post_id': 123}
            mock_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_session
            
            publisher = VKPublisher("test-token", 123456)
            
            result = publisher.publish_post("Test post")
            
            assert result == {'post_id': 123}
            mock_vk.wall.post.assert_called_once_with(
                owner_id=-123456,
                message="Test post",
                attachments=None,
                from_group=1
            )
    
    def test_publish_post_with_image(self):
        """Тест публикации с изображением"""
        with patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api, \
             patch.object(VKPublisher, 'upload_image') as mock_upload:
            
            mock_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.post.return_value = {'post_id': 123}
            mock_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_session
            
            mock_upload.return_value = "photo123_456"
            
            publisher = VKPublisher("test-token", 123456)
            
            result = publisher.publish_post("Test post", "http://example.com/image.jpg")
            
            assert result == {'post_id': 123}
            mock_upload.assert_called_once_with("http://example.com/image.jpg")
            mock_vk.wall.post.assert_called_once_with(
                owner_id=-123456,
                message="Test post",
                attachments="photo123_456",
                from_group=1
            )
    
    def test_publish_post_image_upload_failed(self):
        """Тест публикации при неудачной загрузке изображения"""
        with patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api, \
             patch.object(VKPublisher, 'upload_image') as mock_upload:
            
            mock_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.post.return_value = {'post_id': 123}
            mock_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_session
            
            mock_upload.return_value = None  # Загрузка не удалась
            
            publisher = VKPublisher("test-token", 123456)
            
            result = publisher.publish_post("Test post", "http://example.com/image.jpg")
            
            assert result == {'post_id': 123}
            # Должен опубликовать без изображения
            mock_vk.wall.post.assert_called_once_with(
                owner_id=-123456,
                message="Test post",
                attachments=None,
                from_group=1
            )
    
    def test_publish_post_vk_api_error(self):
        """Тест ошибки VK API при публикации"""
        with patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api:
            mock_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.post.side_effect = Exception("VK API error")
            mock_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_session
            
            publisher = VKPublisher("test-token", 123456)
            
            result = publisher.publish_post("Test post")
            
            assert result is None
    
    def test_publish_post_general_exception(self):
        """Тест общего исключения при публикации"""
        with patch('social_publishers.vk_publisher.vk_api.VkApi') as mock_vk_api:
            mock_session = MagicMock()
            mock_vk = MagicMock()
            mock_vk.wall.post.side_effect = Exception("General error")
            mock_session.get_api.return_value = mock_vk
            mock_vk_api.return_value = mock_session
            
            publisher = VKPublisher("test-token", 123456)
            
            result = publisher.publish_post("Test post")
            
            assert result is None

