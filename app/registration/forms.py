from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms import ValidationError
from wtforms.validators import InputRequired, Email, Length, EqualTo
from ..models import User

class RegistrationForm(FlaskForm):
    user_name = StringField("Username", validators = [InputRequired(), 
        Length(3, 64)])
    email_address = StringField("Email Address", validators = [InputRequired(), 
        Email(), Length(10, 128)])
    password = PasswordField("Password", validators = [InputRequired(), 
        Length(8, 32)])
    confirm_password = PasswordField("Confirm Password", validators = [
        InputRequired(), Length(8, 32), EqualTo("password", 
        message = "Passwords must match")])


    def validate_email_address(self, field):
        if User.query.filter_by(emailAddress = field.data).first():
            raise ValidationError("Email already registered")
   

    def validate_user_name(self, field):
        if User.query.filter_by(userName = field.data).first():
            raise ValidationError("Username already in use")
