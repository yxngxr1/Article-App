from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from wtforms import validators


class UserEditForm(FlaskForm):
    email = EmailField('Почта', validators=[validators.Email()])
    name = StringField('Имя')
    surname = StringField('Фамилия')
    info = TextAreaField('О себе')
    age = StringField('Возраст')
    city_from = StringField('Город')
    submit = SubmitField('Изменить')
