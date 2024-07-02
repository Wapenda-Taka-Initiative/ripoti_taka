from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField
from wtforms import PasswordField
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    email_address = StringField(
        "Email address", validators=[InputRequired(), Email(), Length(10, 128)]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(8, 32)]
    )
    remember_me = BooleanField("Keep me logged in")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(8, 32),
        ],
    )
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )


class UnlockScreenForm(FlaskForm):
    password = PasswordField("Enter Password", validators=[DataRequired()])


class ForgotPasswordForm(FlaskForm):
    email_address = StringField(
        "Email address", validators=[InputRequired(), Email(), Length(10, 128)]
    )
