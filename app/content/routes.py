import logging

from flask import flash, render_template
from flask_login import current_user, login_required

from app.content import bp
from app.content.forms import PostGenerationForm
from app.services.content_workflow import ContentWorkflowService


logger = logging.getLogger(__name__)


@bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate():
    form = PostGenerationForm()
    result = None

    if form.validate_on_submit():
        logger.info(
            "[content.generate] start extra=%s",
            {"user_id": current_user.id, "topic": form.topic.data, "auto_post_vk": form.auto_post_vk.data},
        )
        try:
            workflow_result = ContentWorkflowService().generate_for_user(
                user=current_user,
                tone=form.tone.data,
                topic=form.topic.data,
                generate_image=form.generate_image.data,
                auto_post_vk=form.auto_post_vk.data,
            )
        except Exception as exc:
            logger.exception(
                "[content.generate] workflow failed extra=%s",
                {"user_id": current_user.id, "error": str(exc)},
            )
            flash("Не удалось обработать генерацию контента. Проверьте настройки и попробуйте снова.", "danger")
        else:
            result = workflow_result.generated_post
            if workflow_result.vk_warning:
                flash(workflow_result.vk_warning, "warning")
            else:
                flash("Контент успешно сгенерирован.", "success")

    return render_template("content/generator.html", form=form, result=result)
