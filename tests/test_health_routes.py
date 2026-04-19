from unittest.mock import patch

from app import create_app
from app.config import TestConfig


def test_healthz_returns_ok_when_database_is_available():
    with patch.dict("os.environ", {}, clear=True):
        app = create_app(TestConfig)

    with patch("app.main.routes.db.session.execute") as mock_execute:
        response = app.test_client().get("/healthz")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["critical_checks"]["database"]["status"] == "ok"
    mock_execute.assert_called_once()


def test_healthz_returns_degraded_for_partial_optional_provider_config():
    with patch.dict(
        "os.environ",
        {
            "VK_TOKEN": "vk-token-only",
        },
        clear=True,
    ):
        app = create_app(TestConfig)

    with patch("app.main.routes.db.session.execute"):
        response = app.test_client().get("/healthz")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "degraded"
    assert payload["optional_providers"]["vk"]["status"] == "misconfigured"


def test_healthz_returns_service_unavailable_when_database_fails():
    with patch.dict("os.environ", {}, clear=True):
        app = create_app(TestConfig)

    with patch(
        "app.main.routes.db.session.execute",
        side_effect=RuntimeError("database unavailable"),
    ):
        response = app.test_client().get("/healthz")

    assert response.status_code == 503
    payload = response.get_json()
    assert payload["status"] == "error"
    assert payload["critical_checks"]["database"]["reason"] == "database_unreachable"
