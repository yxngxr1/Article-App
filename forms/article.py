from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class ArticleForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = StringField('Краткое описание', validators=[DataRequired()])
    content = TextAreaField("Текст")
    category_id = SelectField("Катагория", choices=[], coerce=int)
    is_private = BooleanField("Личное")
    submit = SubmitField('Отправить')
