from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class ArticleForm(FlaskForm):
    title = StringField('Название статьи', validators=[DataRequired()])
    description = StringField('Описание статьи', validators=[DataRequired()])
    content = TextAreaField("Текст статьи", validators=[DataRequired()])
    category_id = SelectField("Катагория", choices=[], coerce=int)
    is_private = BooleanField("Личное")
    submit = SubmitField('Отправить')
