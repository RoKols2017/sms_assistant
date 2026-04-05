from app import create_app
from app.config import TestConfig


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
