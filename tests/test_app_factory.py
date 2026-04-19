from unittest.mock import patch

from app import create_app
from app.config import DevelopmentConfig, ProductionConfig, TestConfig
from werkzeug.middleware.proxy_fix import ProxyFix


def test_create_app_registers_expected_routes():
    app = create_app(TestConfig)

    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/dashboard" in routes
    assert "/auth/login" in routes
    assert "/auth/register" in routes
    assert "/settings/" in routes
    assert "/content/generate" in routes
    assert "/stats/vk" in routes


def test_init_db_command(runner):
    result = runner.invoke(args=["init-db"])

    assert result.exit_code == 0


def test_create_app_uses_runtime_environment_defaults():
    with patch.dict(
        "os.environ",
        {
            "FLASK_ENV": "development",
            "FLASK_SECRET_KEY": "dev-secret",
            "LOG_LEVEL": "DEBUG",
        },
        clear=True,
    ):
        app = create_app()

    assert app.config["ENVIRONMENT"] == DevelopmentConfig.ENVIRONMENT
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///smm_assistant-dev.db"
    assert app.config["LOG_LEVEL"] == "DEBUG"


def test_create_app_requires_production_database_url():
    with patch.dict(
        "os.environ",
        {
            "FLASK_ENV": "production",
            "FLASK_SECRET_KEY": "prod-secret",
        },
        clear=True,
    ):
        try:
            create_app(ProductionConfig)
        except RuntimeError as exc:
            assert str(exc) == "DATABASE_URL or SQLALCHEMY_DATABASE_URI must be set in production."
        else:
            raise AssertionError("Expected create_app to reject missing production database config")


def test_create_app_uses_test_config_defaults():
    with patch.dict("os.environ", {}, clear=True):
        app = create_app(TestConfig)

    assert app.config["ENVIRONMENT"] == TestConfig.ENVIRONMENT
    assert app.config["TESTING"] is True
    assert app.config["WTF_CSRF_ENABLED"] is False


def test_create_app_wraps_wsgi_with_proxyfix_when_enabled():
    with patch.dict(
        "os.environ",
        {
            "FLASK_ENV": "production",
            "FLASK_SECRET_KEY": "prod-secret",
            "DATABASE_URL": "postgresql://user:secret@db:5432/smm_assistant",
            "TRUST_PROXY_COUNT": "1",
        },
        clear=True,
    ):
        app = create_app(ProductionConfig)

    assert isinstance(app.wsgi_app, ProxyFix)
