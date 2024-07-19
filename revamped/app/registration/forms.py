from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import SelectField
from wtforms import SubmitField
from wtforms import PasswordField
from wtforms import ValidationError
from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed

from wtforms.validators import Email
from wtforms.validators import Length
from wtforms.validators import EqualTo
from wtforms.validators import DataRequired

from app.models import User
from app.models import Handler


class HandlerRegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=255)])
    handlerType = StringField(
        "Type", validators=[DataRequired(), Length(max=255)]
    )
    resourceAvailability = TextAreaField("Resource Availability")
    emailAddress = StringField(
        "Email", validators=[DataRequired(), Email(), Length(max=255)]
    )
    phoneNumber = StringField(
        "Phone Number", validators=[DataRequired(), Length(min=10, max=15)]
    )
    imageUrl = FileField(
        "Profile Image",
        validators=[
            FileAllowed(["avif", "webp", "jpg", "jpeg", "png"], "Images only!")
        ],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6)]
    )
    confirmPassword = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Register")

    def validate_emailAddress(self, field):
        if Handler.query.filter_by(emailAddress=field.data).first():
            raise ValidationError("Email is already registered.")


class RegistrationForm(FlaskForm):
    emailAddress = StringField(
        "Email", validators=[DataRequired(), Email(), Length(max=255)]
    )
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=255)]
    )
    phoneNumber = StringField(
        "Phone Number", validators=[DataRequired(), Length(min=10, max=15)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6)]
    )
    confirmPassword = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Register")

    def validate_emailAddress(self, field):
        if User.query.filter_by(emailAddress=field.data).first():
            raise ValidationError("Email is already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username is already taken.")


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
