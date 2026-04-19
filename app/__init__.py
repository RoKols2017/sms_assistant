"""Flask application factory."""

from __future__ import annotations

import logging
from typing import Optional

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.auth import bp as auth_bp
from app.config import BaseConfig, describe_database_target, get_config_class
from app.content import bp as content_bp
from app.extensions import bcrypt, csrf, db, login_manager, migrate
from app.main import bp as main_bp
from app.settings import bp as settings_bp
from app.stats import bp as stats_bp


def configure_logging(app: Flask) -> None:
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s [%(name)s] %(message)s"
            )
        )
        app.logger.addHandler(handler)

    app.logger.setLevel(log_level)
    logging.getLogger().setLevel(log_level)
    app.logger.info(
        "[create_app] logging configured extra=%s",
        {
            "level": log_level_name,
            "environment": app.config.get("ENVIRONMENT"),
        },
    )


def register_blueprints(app: Flask) -> None:
    for blueprint in (main_bp, auth_bp, settings_bp, content_bp, stats_bp):
        app.register_blueprint(blueprint)
        app.logger.info(
            "[register_blueprints] blueprint registered extra=%s",
            {"name": blueprint.name, "url_prefix": blueprint.url_prefix},
        )


def register_error_handlers(app: Flask) -> None:
    from app.errors import register_error_handlers as register

    register(app)


def validate_runtime_config(app: Flask) -> None:
    secret_key = app.config.get("SECRET_KEY")
    environment = app.config.get("ENVIRONMENT", "production")
    database_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    has_openai = bool(app.config.get("OPENAI_API_KEY"))
    has_vk_token = bool(app.config.get("VK_TOKEN"))
    has_vk_group = bool(app.config.get("VK_GROUP_ID"))
    has_tg_token = bool(app.config.get("TG_TOKEN"))
    has_tg_chat = bool(app.config.get("TG_CHAT_ID"))

    if not secret_key:
        if environment == "production":
            app.logger.error(
                "[validate_runtime_config] missing production secret key extra=%s",
                {"environment": environment},
            )
            raise RuntimeError("FLASK_SECRET_KEY must be set in production.")

        app.config["SECRET_KEY"] = "dev-insecure-secret-key"
        app.logger.warning(
            "[validate_runtime_config] using development secret key extra=%s",
            {"environment": environment},
        )

    if not database_uri and environment == "production":
        app.logger.error(
            "[validate_runtime_config] missing production database uri extra=%s",
            {"environment": environment},
        )
        raise RuntimeError(
            "DATABASE_URL or SQLALCHEMY_DATABASE_URI must be set in production."
        )

    if has_vk_token != has_vk_group:
        app.logger.warning(
            "[validate_runtime_config] vk optional integration partially configured extra=%s",
            {"has_token": has_vk_token, "has_group_id": has_vk_group},
        )

    if has_tg_token != has_tg_chat:
        app.logger.warning(
            "[validate_runtime_config] telegram optional integration partially configured extra=%s",
            {"has_token": has_tg_token, "has_chat_id": has_tg_chat},
        )

    app.logger.info(
        "[validate_runtime_config] optional provider configuration extra=%s",
        {
            "openai": has_openai,
            "vk": has_vk_token and has_vk_group,
            "telegram": has_tg_token and has_tg_chat,
        },
    )


def configure_proxy_support(app: Flask) -> None:
    proxy_count = app.config.get("TRUST_PROXY_COUNT", 0) or 0
    if proxy_count > 0:
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=proxy_count,
            x_proto=proxy_count,
            x_host=proxy_count,
            x_port=proxy_count,
            x_prefix=proxy_count,
        )
        app.logger.info(
            "[create_app] proxy support enabled extra=%s",
            {"trusted_proxy_count": proxy_count},
        )
        return

    app.logger.info(
        "[create_app] proxy support disabled extra=%s",
        {"trusted_proxy_count": proxy_count},
    )


def log_runtime_config(app: Flask) -> None:
    database_target = describe_database_target(app.config.get("SQLALCHEMY_DATABASE_URI"))
    app.logger.info(
        "[create_app] configuration loaded extra=%s",
        {
            "environment": app.config.get("ENVIRONMENT"),
            "database": database_target,
            "csrf_enabled": app.config.get("WTF_CSRF_ENABLED"),
            "request_timeout": app.config.get("REQUEST_TIMEOUT"),
            "preferred_url_scheme": app.config.get("PREFERRED_URL_SCHEME"),
            "secure_cookie_mode": {
                "session": app.config.get("SESSION_COOKIE_SECURE"),
                "remember": app.config.get("REMEMBER_COOKIE_SECURE"),
                "samesite": app.config.get("SESSION_COOKIE_SAMESITE"),
            },
            "proxy_aware_mode": app.config.get("TRUST_PROXY_COUNT", 0) > 0,
            "optional_integrations": {
                "openai": bool(app.config.get("OPENAI_API_KEY")),
                "vk": bool(app.config.get("VK_TOKEN") and app.config.get("VK_GROUP_ID")),
                "telegram": bool(app.config.get("TG_TOKEN") and app.config.get("TG_CHAT_ID")),
            },
        },
    )


def create_app(config_object: Optional[type[BaseConfig]] = None) -> Flask:
    app = Flask(__name__)
    app_config = get_config_class(config_object)
    app.config.from_mapping(app_config.build())

    from app import models  # noqa: F401

    configure_logging(app)
    validate_runtime_config(app)
    configure_proxy_support(app)
    log_runtime_config(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    register_blueprints(app)
    register_error_handlers(app)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        app.logger.info("[init_db_command] start")
        db.create_all()
        app.logger.info("[init_db_command] completed")

    return app
