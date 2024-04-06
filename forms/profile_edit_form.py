from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length


class ProfileEditForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Сохранить изменения')