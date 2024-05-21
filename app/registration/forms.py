from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SelectField
from wtforms import PasswordField
from wtforms import TextAreaField
from wtforms import ValidationError
from wtforms.validators import InputRequired
from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import DataRequired

from app.models import User


class RegistrationForm(FlaskForm):
    user_name = StringField(
        "Username", validators=[InputRequired(), Length(3, 64)]
    )
    email_address = StringField(
        "Email Address", validators=[InputRequired(), Email(), Length(10, 128)]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(), Length(8, 32)]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            Length(8, 32),
            EqualTo("password", message="Passwords must match"),
        ],
    )

    def validate_email_address(self, field):
        if User.query.filter_by(emailAddress=field.data).first():
            raise ValidationError("Email already registered")

    def validate_user_name(self, field):
        if User.query.filter_by(userName=field.data).first():
            raise ValidationError("Username already in use")


class EditUserProfileForm(FlaskForm):
    firstName = StringField("First Name", validators=[Length(1, 50)])
    middleName = StringField("Middle Name", validators=[Length(1, 50)])
    lastName = StringField("Last Name", validators=[Length(1, 50)])

    phoneNumber = StringField("Phone Number", validators=[Length(1, 50)])
    gender = SelectField("Gender")

    locationAddress = StringField(
        "Residential Address", validators=[DataRequired(), Length(1, 128)]
    )
    about_me = TextAreaField("About Me", validators=[Length(1, 192)])


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Enter New Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )


class ResetUsernameForm(FlaskForm):
    user_name = StringField(
        "Enter New Username", validators=[InputRequired(), Length(3, 64)]
    )


class ResetEmailForm(FlaskForm):
    email_address = StringField(
        "Enter New Email Address",
        validators=[InputRequired(), Email(), Length(10, 128)],
    )
