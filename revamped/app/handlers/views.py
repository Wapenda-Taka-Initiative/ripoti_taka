import flask
from flask_login import current_user
from flask_login import login_required

from . import handlers

from .forms import ReportResolutionForm
from .forms import AssignReportResolutionForm

from app import db
from ..models import Report
from ..models import ReportResolution

from utilities.authentication import user_type_validator


@handlers.route("/dashboard")
@login_required
@user_type_validator("handler")
def dashboard():
    reports = Report.query.order_by(Report.reportId.desc()).all()
    return flask.render_template("handlers/dashboard.html", reports=reports)


@handlers.route("/add-report-resolution", methods=["GET", "POST"])
@login_required
@user_type_validator("handler")
def report_resolution():
    form = ReportResolutionForm()

    if flask.request.method == "POST":
        # Create a new Report object
        details = {
            "userId": current_user.handlerId,
            "severityLevel": form.severityLevel.data,
            "initialSituationDescription": form.initialSituationDescription.data,
            "stepsTaken": form.stepsTaken.data,
            "recommendations": form.recommendations.data,
            "potentialCauses": form.potentialCauses.data,
            "manPowerDetails": form.manPowerDetails.data,
            "financialCosts": form.financialCosts.data,
            "dateCompleted": form.dateCompleted.data,
            "status": "Completed",
        }
        ReportResolution.create(details)

        flask.flash("Resolution submitted successfully!", "success")
        return flask.redirect(flask.url_for("handlers.dashboard"))

    return flask.render_template("handlers/report_resolution.html", form=form)


@handlers.route("/reports/<int:report_id>", methods=["GET", "POST"])
@login_required
@user_type_validator("handler")
def report_details(report_id):
    report = Report.query.filter_by(reportId=report_id).first_or_404()
    form = AssignReportResolutionForm()

    form.reportResolutionId.choices = [
        (resolution.reportResolutionId, resolution.reportResolutionId)
        for resolution in ReportResolution.query.all()
    ]

    if flask.request.method == "POST":
        report_assignment = report.reportAssignments[-1]
        report_assignment.reportResolutionId = form.reportResolutionId.data
        report.status = "Resolved"

        db.session.add(report)
        db.session.add(report_assignment)
        db.session.commit()

        flask.flash("Report marked as resolved successfully", "success")
        return flask.redirect(
            flask.url_for("handlers.report_details", report_id=report_id)
            + "#comments"
        )

    return flask.render_template(
        "handlers/report_details.html",
        report=report,
        form=form,
    )


@handlers.route("/reports/my-reports", methods=["GET", "POST"])
@login_required
@user_type_validator("handler")
def my_reports():
    return flask.render_template("handlers/my_reports.html")


@handlers.route("/reports/latest-reports", methods=["GET"])
@login_required
@user_type_validator("handler")
def latest_reports():
    reports = Report.query.limit(50)
    return flask.render_template(
        "handlers/latest_reports.html", reports=reports
    )


@handlers.route("/reports/<int:report_id>/handle", methods=["GET"])
@login_required
@user_type_validator("handler")
def handle_report(report_id):
    report = Report.query.filter_by(reportId=report_id).first_or_404()
    current_user.acceptHandling(report)
    flask.flash("Report assigned to you successfully", "success")
    return flask.redirect(
        flask.url_for("handlers.report_details", report_id=report.reportId)
    )
