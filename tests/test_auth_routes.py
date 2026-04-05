from app.models.user import User


def test_register_creates_user_and_redirects(client, app):
    response = client.post(
        "/auth/register",
        data={
            "email": "user@example.com",
            "password": "supersecret123",
            "confirm_password": "supersecret123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Регистрация прошла успешно" in response.get_data(as_text=True)

    with app.app_context():
        assert User.query.filter_by(email="user@example.com").first() is not None


def test_login_rejects_invalid_password(client, app):
    client.post(
        "/auth/register",
        data={
            "email": "user2@example.com",
            "password": "supersecret123",
            "confirm_password": "supersecret123",
        },
        follow_redirects=True,
    )

    response = client.post(
        "/auth/login",
        data={"email": "user2@example.com", "password": "wrong-password"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Неверный email или пароль" in response.get_data(as_text=True)


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=False)

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
