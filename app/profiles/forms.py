from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SelectField
from wtforms import IntegerField
from wtforms import TextAreaField
from wtforms import MultipleFileField
from wtforms.validators import Length
from wtforms.validators import DataRequired


class CreateReportForm(FlaskForm):
    location = StringField(
        "Location", validators=[DataRequired(), Length(1, 255)]
    )
    category_id = SelectField("Category", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    images = MultipleFileField("Upload Images")


class CreateCategoryForm(FlaskForm):
    name = StringField(
        "Category Name", validators=[DataRequired(), Length(1, 50)]
    )
    description = TextAreaField(
        "Description", validators=[DataRequired(), Length(1, 800)]
    )


class CreateRewardForm(FlaskForm):
    name = StringField(
        "Reward Name", validators=[DataRequired(), Length(1, 50)]
    )
    pointsRequired = IntegerField(
        "Points Required", validators=[DataRequired()]
    )
