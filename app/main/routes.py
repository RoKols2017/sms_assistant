import logging

from flask import current_app, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import text

from app.extensions import db
from app.main import bp


logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    logger.info("[main.dashboard] render extra=%s", {"user_id": current_user.id})
    return render_template("dashboard.html")


@bp.route("/healthz")
def healthz():
    logger.info("[main.healthz] start")

    critical_checks = {"app": {"status": "ok"}}
    optional_providers = {}
    response_status = 200
    overall_status = "ok"

    try:
        db.session.execute(text("SELECT 1"))
        critical_checks["database"] = {"status": "ok"}
    except Exception as exc:
        logger.exception("[main.healthz] database check failed extra=%s", {"error": str(exc)})
        critical_checks["database"] = {"status": "error", "reason": "database_unreachable"}
        overall_status = "error"
        response_status = 503

    optional_providers["openai"] = {
        "status": "configured" if current_app.config.get("OPENAI_API_KEY") else "not_configured"
    }

    provider_pairs = {
        "vk": (
            bool(current_app.config.get("VK_TOKEN")),
            bool(current_app.config.get("VK_GROUP_ID")),
        ),
        "telegram": (
            bool(current_app.config.get("TG_TOKEN")),
            bool(current_app.config.get("TG_CHAT_ID")),
        ),
    }

    for provider_name, (has_primary, has_secondary) in provider_pairs.items():
        if has_primary and has_secondary:
            optional_providers[provider_name] = {"status": "configured"}
        elif has_primary or has_secondary:
            optional_providers[provider_name] = {"status": "misconfigured"}
            if overall_status == "ok":
                overall_status = "degraded"
        else:
            optional_providers[provider_name] = {"status": "not_configured"}

    payload = {
        "status": overall_status,
        "environment": current_app.config.get("ENVIRONMENT"),
        "critical_checks": critical_checks,
        "optional_providers": optional_providers,
    }
    logger.info(
        "[main.healthz] completed extra=%s",
        {
            "status": overall_status,
            "response_status": response_status,
            "database": critical_checks["database"]["status"],
        },
    )
    return jsonify(payload), response_status
