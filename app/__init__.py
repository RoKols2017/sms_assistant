"""Flask application factory."""

from __future__ import annotations

import logging
from typing import Optional

from flask import Flask

from app.auth import bp as auth_bp
from app.config import AppConfig
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

    if not secret_key:
        if environment == "production":
            raise RuntimeError("FLASK_SECRET_KEY must be set in production.")

        app.config["SECRET_KEY"] = "dev-insecure-secret-key"
        app.logger.warning(
            "[validate_runtime_config] using development secret key extra=%s",
            {"environment": environment},
        )


def create_app(config_object: Optional[type[AppConfig]] = None) -> Flask:
    app = Flask(__name__)
    app_config = config_object or AppConfig
    app.config.from_object(app_config)

    from app import models  # noqa: F401

    configure_logging(app)
    validate_runtime_config(app)
    app.logger.info(
        "[create_app] configuration loaded extra=%s",
        {
            "database_uri": app.config.get("SQLALCHEMY_DATABASE_URI", "").rsplit("@", 1)[-1],
            "vk_api_version": app.config.get("VK_API_VERSION"),
            "csrf_enabled": app.config.get("WTF_CSRF_ENABLED"),
        },
    )

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
