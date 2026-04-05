import logging

from flask import render_template
from flask_login import current_user, login_required

from app.stats import bp
from app.services.stats_service import StatsService


logger = logging.getLogger(__name__)


@bp.route("/vk")
@login_required
def vk_stats():
    logger.info("[stats.vk_stats] start extra=%s", {"user_id": current_user.id})
    stats_result = StatsService().get_vk_stats_for_user(current_user)
    return render_template("stats/vk_stats.html", stats=stats_result)
