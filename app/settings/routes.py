import logging

from flask import flash, render_template
from flask_login import current_user, login_required

from app.settings import bp
from app.settings.forms import VKSettingsForm
from app.services.settings_service import SettingsService
from app.services.vk_capability_service import VKCapabilityService


logger = logging.getLogger(__name__)


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    settings_service = SettingsService()
    existing_settings = current_user.vk_settings

    form = VKSettingsForm(
        data={
            "vk_api_key": existing_settings.vk_api_key if existing_settings else "",
            "vk_group_id": existing_settings.vk_group_id if existing_settings else None,
        }
    )

    if form.validate_on_submit():
        logger.info(
            "[settings.index] save attempt extra=%s",
            {"user_id": current_user.id, "vk_group_id": form.vk_group_id.data},
        )
        capability_result = VKCapabilityService().validate(
            token=form.vk_api_key.data,
            group_id=form.vk_group_id.data,
        )
        settings = settings_service.save_vk_settings(
            user=current_user,
            vk_api_key=form.vk_api_key.data,
            vk_group_id=form.vk_group_id.data,
            validation_status=capability_result.validation_status,
            validation_message=capability_result.validation_message,
            can_access_group=capability_result.can_access_group,
            can_post_to_wall=capability_result.can_post_to_wall,
            can_upload_wall_photo=capability_result.can_upload_wall_photo,
        )
        flash("Настройки VK сохранены.", "success")
        return render_template("settings.html", form=form, settings=settings)

    return render_template("settings.html", form=form, settings=existing_settings)
