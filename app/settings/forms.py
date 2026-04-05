from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class VKSettingsForm(FlaskForm):
    vk_api_key = PasswordField(
        "VK API key",
        validators=[DataRequired(), Length(min=10, max=4096)],
        render_kw={"autocomplete": "off"},
    )
    vk_group_id = IntegerField(
        "VK Group ID",
        validators=[DataRequired(), NumberRange(min=1, message="ID группы должен быть положительным.")],
    )
    submit = SubmitField("Сохранить")
