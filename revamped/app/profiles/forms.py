from flask_wtf import FlaskForm
from wtforms import FloatField
from wtforms import StringField
from wtforms import SelectField
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms import ValidationError
from wtforms import MultipleFileField
from wtforms import SelectMultipleField

from wtforms.validators import Length
from wtforms.validators import DataRequired


class CreateReportForm(FlaskForm):
    locationAddress = StringField(
        "Location Address", validators=[DataRequired(), Length(max=255)]
    )
    latitude = FloatField("Latitude", validators=[DataRequired()])
    longitude = FloatField("Longitude", validators=[DataRequired()])
    wasteType = SelectField(
        "Waste Type",
        choices=[
            ("Plastic", "Plastic"),
            ("Glass", "Glass"),
            ("Metal", "Metal"),
            ("Paper", "Paper"),
            ("Organic", "Organic"),
            ("Electronic Waste", "Electronic Waste"),
            ("Construction Waste", "Construction Waste"),
            ("Textile", "Textile"),
            ("Hazardous", "Hazardous"),
            ("Medical Waste", "Medical Waste"),
        ],
        validators=[DataRequired()],
    )
    description = TextAreaField("Description", validators=[DataRequired()])
    severityLevel = SelectField(
        "Severity Level",
        choices=[("low", "Low"), ("moderate", "Moderate"), ("high", "High")],
        validators=[DataRequired()],
    )
    periodOfOccurrence = SelectField(
        "Period of Occurrence",
        choices=[
            ("Last 1 day", "Last 1 day"),
            ("Last 3 days", "Last 3 days"),
            ("Last 1 week", "Last 1 week"),
            ("Last 2 weeks", "Last 2 weeks"),
            ("Last 1 month", "Last 1 month"),
            ("Last 3 months", "Last 3 months"),
        ],
        validators=[DataRequired()],
    )
    categories = SelectMultipleField("Categories", coerce=int)
    images = MultipleFileField("Upload Images")
    submit = SubmitField("Create Report")

    def validate_latitude(self, field):
        if not (-90 <= field.data <= 90):
            raise ValidationError("Latitude must be between -90 and 90.")

    def validate_longitude(self, field):
        if not (-180 <= field.data <= 180):
            raise ValidationError("Longitude must be between -180 and 180.")


class UpdateReportForm(FlaskForm):
    locationAddress = StringField(
        "Location Address", validators=[DataRequired(), Length(max=255)]
    )
    latitude = FloatField("Latitude", validators=[DataRequired()])
    longitude = FloatField("Longitude", validators=[DataRequired()])
    wasteType = StringField(
        "Waste Type", validators=[DataRequired(), Length(max=255)]
    )
    description = TextAreaField("Description", validators=[DataRequired()])
    severityLevel = SelectField(
        "Severity Level",
        choices=[("low", "Low"), ("moderate", "Moderate"), ("high", "High")],
        validators=[DataRequired()],
    )
    periodOfOccurrence = StringField(
        "Period of Occurrence", validators=[DataRequired(), Length(max=255)]
    )
    categories = SelectMultipleField("Categories", coerce=int)
    submit = SubmitField("Update Report")

    def validate_latitude(self, field):
        if not (-90 <= field.data <= 90):
            raise ValidationError("Latitude must be between -90 and 90.")

    def validate_longitude(self, field):
        if not (-180 <= field.data <= 180):
            raise ValidationError("Longitude must be between -180 and 180.")


class RegisterCategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=255)])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Create Category")
