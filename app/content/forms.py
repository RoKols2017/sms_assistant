from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class PostGenerationForm(FlaskForm):
    tone = StringField("Tone", validators=[DataRequired(), Length(min=2, max=128)])
    topic = StringField("Topic", validators=[DataRequired(), Length(min=2, max=255)])
    generate_image = BooleanField("Сгенерировать изображение")
    auto_post_vk = BooleanField("Автопост в VK")
    submit = SubmitField("Сгенерировать")
