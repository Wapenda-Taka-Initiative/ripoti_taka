from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField
from wtforms import PasswordField
from wtforms.validators import Length
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    user_name = StringField(
        "Username", validators=[InputRequired(), Length(3, 64)]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(8, 32)]
    )
    remember_me = BooleanField("Keep me logged in")
