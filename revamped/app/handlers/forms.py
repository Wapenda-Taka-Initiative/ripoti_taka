
from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SelectField
from wtforms import SubmitField
from wtforms import DateField

from wtforms.validators import DataRequired


class ReportResolutionForm(FlaskForm):
    severityLevel = SelectField(
        "Severity Level",
        choices=[("low", "Low"), ("moderate", "Moderate"), ("high", "High")],
        validators=[DataRequired()],
    )
    initialSituationDescription = TextAreaField(
        "Initial Situation Description", validators=[DataRequired()]
    )
    stepsTaken = TextAreaField("Steps Taken", validators=[DataRequired()])
    recommendations = TextAreaField(
        "Recommendations", validators=[DataRequired()]
    )
    potentialCauses = TextAreaField(
        "Potential Causes", validators=[DataRequired()]
    )
    manPowerDetails = TextAreaField(
        "Manpower Details", validators=[DataRequired()]
    )
    financialCosts = TextAreaField(
        "Financial Costs", validators=[DataRequired()]
    )
    dateCompleted = DateField(
        "Date Completed",
    )
    submit = SubmitField("Submit")


class AssignReportResolutionForm(FlaskForm):
    reportResolutionId = SelectField(
        "Select resolution instance", validators=[DataRequired()],
    )
    submit = SubmitField("Create Report")
