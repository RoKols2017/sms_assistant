import logging

from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

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
