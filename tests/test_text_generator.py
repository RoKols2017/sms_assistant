"""
Тесты для генератора текста
"""

import pytest
from unittest.mock import patch, MagicMock
from generators.text_gen import TextGenerator


class TestTextGenerator:
    """Тесты для класса TextGenerator"""
    
    def test_init_success(self):
        """Тест успешной инициализации"""
        with patch('generators.text_gen.config') as mock_config:
            mock_config.openai_api_key = 'test-key'
            
            generator = TextGenerator(
                tone="дружелюбный",
                topic="технологии",
                model="gpt-5"
            )
            
            assert generator.tone == "дружелюбный"
            assert generator.topic == "технологии"
            assert generator.model == "gpt-5"
    
    def test_init_invalid_tone(self):
        """Тест ошибки при пустом тоне"""
        with pytest.raises(ValueError, match="Тон поста не может быть пустым"):
            TextGenerator(tone="", topic="технологии")
    
    def test_init_invalid_topic(self):
        """Тест ошибки при пустой теме"""
        with pytest.raises(ValueError, match="Тема поста не может быть пустой"):
            TextGenerator(tone="дружелюбный", topic="")
    
    def test_init_whitespace_handling(self):
        """Тест обработки пробелов"""
        with patch('generators.text_gen.config') as mock_config:
            mock_config.openai_api_key = 'test-key'
            
            generator = TextGenerator(
                tone="  дружелюбный  ",
                topic="  технологии  "
            )
            
            assert generator.tone == "дружелюбный"
            assert generator.topic == "технологии"
    
    def test_init_model_validation(self):
        """Тест валидации модели"""
        with patch('generators.text_gen.config') as mock_config:
            mock_config.openai_api_key = 'test-key'
            
            # Валидная модель
            generator = TextGenerator(
                tone="дружелюбный",
                topic="технологии",
                model="gpt-5"
            )
            assert generator.model == "gpt-5"
            
            # Невалидная модель (должно вызвать предупреждение)
            with patch('generators.text_gen.logger') as mock_logger:
                TextGenerator(
                    tone="дружелюбный",
                    topic="технологии",
                    model="invalid-model"
                )
                mock_logger.warning.assert_called_once()
    
    @patch('generators.text_gen.openai.OpenAI')
    def test_generate_post_success(self, mock_openai):
        """Тест успешной генерации поста"""
        # Настройка мока
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Тестовый пост"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch('generators.text_gen.config') as mock_config:
            mock_config.openai_api_key = 'test-key'
            
            generator = TextGenerator(
                tone="дружелюбный",
                topic="технологии"
            )
            
            result = generator.generate_post()
            
            assert result == "Тестовый пост"
            mock_client.chat.completions.create.assert_called_once()
    
    @patch('generators.text_gen.openai.OpenAI')
    def test_generate_post_authentication_error(self, mock_openai):
        """Тест ошибки аутентификации"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Authentication failed")
        mock_openai.return_value = mock_client
        
        with patch('generators.text_gen.config') as mock_config:
            mock_config.openai_api_key = 'test-key'
            
            generator = TextGenerator(
                tone="дружелюбный",
                topic="технологии"
            )
            
            result = generator.generate_post()
            
            assert result is None
    
    @patch('generators.text_gen.openai.OpenAI')
    def test_generate_post_rate_limit_error(self, mock_openai):
        """Тест ошибки лимита запросов"""
        from openai import RateLimitError
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RateLimitError("Rate limit exceeded")
        mock_openai.return_value = mock_client
        
        with patch('generators.text_gen.config') as mock_config:
            mock_config.openai_api_key = 'test-key'
            
            generator = TextGenerator(
                tone="дружелюбный",
                topic="технологии"
            )
            
            result = generator.generate_post()
            
            assert result is None
    
    @patch('generators.text_gen.openai.OpenAI')
    def test_generate_post_api_error(self, mock_openai):
        """Тест ошибки API"""
        from openai import APIError
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APIError("API error")
        mock_openai.return_value = mock_client
        
        with patch('generators.text_gen.config') as mock_config:
            mock_config.openai_api_key = 'test-key'
            
            generator = TextGenerator(
                tone="дружелюбный",
                topic="технологии"
            )
            
            result = generator.generate_post()
            
            assert result is None
    
    def test_generate_post_prompt_construction(self):
        """Тест построения промпта"""
        with patch('generators.text_gen.openai.OpenAI') as mock_openai, \
             patch('generators.text_gen.config') as mock_config:
            
            mock_config.openai_api_key = 'test-key'
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Тестовый пост"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            generator = TextGenerator(
                tone="профессиональный",
                topic="искусственный интеллект"
            )
            
            generator.generate_post()
            
            # Проверяем, что промпт содержит правильные параметры
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args[1]['messages']
            
            assert any("профессиональный" in msg['content'] for msg in messages)
            assert any("искусственный интеллект" in msg['content'] for msg in messages)
    
    def test_generate_post_model_usage(self):
        """Тест использования модели"""
        with patch('generators.text_gen.openai.OpenAI') as mock_openai, \
             patch('generators.text_gen.config') as mock_config:
            
            mock_config.openai_api_key = 'test-key'
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Тестовый пост"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            generator = TextGenerator(
                tone="дружелюбный",
                topic="технологии",
                model="gpt-4o"
            )
            
            generator.generate_post()
            
            # Проверяем, что используется правильная модель
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == "gpt-4o"

