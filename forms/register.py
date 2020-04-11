from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from wtforms import validators


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), validators.Email()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повтор пароля', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
