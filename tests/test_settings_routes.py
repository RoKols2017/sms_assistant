from unittest.mock import patch

from app.models.user import User
from app.models.vk_settings import VKSettings


def register_and_login(client):
    client.post(
        "/auth/register",
        data={
            "email": "settings@example.com",
            "password": "supersecret123",
            "confirm_password": "supersecret123",
        },
        follow_redirects=True,
    )


def test_settings_save_vk_configuration(client, app):
    register_and_login(client)

    with patch("app.settings.routes.VKCapabilityService.validate") as mock_validate:
        mock_validate.return_value.validation_status = "validated"
        mock_validate.return_value.validation_message = "ok"
        mock_validate.return_value.can_access_group = True
        mock_validate.return_value.can_post_to_wall = None
        mock_validate.return_value.can_upload_wall_photo = None

        response = client.post(
            "/settings/",
            data={"vk_api_key": "test-valid-vk-token", "vk_group_id": "123456"},
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert "Настройки VK сохранены" in response.get_data(as_text=True)

    with app.app_context():
        user = User.query.filter_by(email="settings@example.com").first()
        settings = VKSettings.query.filter_by(user_id=user.id).first()
        assert settings is not None
        assert settings.vk_group_id == 123456
        assert settings.validation_status in {"validated", "invalid"}
