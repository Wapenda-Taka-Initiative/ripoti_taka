from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from ..models import User

class LoginForm(FlaskForm):
    user_name = StringField("Username", validators = [InputRequired(), 
        Length(3, 64)])
    password = PasswordField("Password", validators = [InputRequired(), 
        Length(8, 32)])
    remember_me = BooleanField("Keep me logged in")
