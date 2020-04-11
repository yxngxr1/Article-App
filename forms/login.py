from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from wtforms import validators


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), validators.Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
