import os
import glob

import flask
from flask_login import current_user
from flask_login import login_required

from . import profiles

from .forms import CreateReportForm
from .forms import RegisterCategoryForm

from app import db
from ..models import Handler
from ..models import Report
from ..models import User
from ..models import Comment
from ..models import Category

from utilities.authentication import user_type_validator


@profiles.route("/dashboard")
@login_required
def dashboard():
    reports = Report.query.order_by(Report.reportId.desc()).all()
    return flask.render_template("profiles/dashboard.html", reports=reports)


@profiles.route("/create_report", methods=["GET", "POST"])
@login_required
def create_report():
    form = CreateReportForm()

    # Populate options for the category_id field of the form
    categories = Category.query.all()
    category_choices = [
        (category.categoryId, category.name) for category in categories
    ]
    form.categories.choices = category_choices

    if form.validate_on_submit():
        # Create a new Report object
        details = {
            "userId": current_user.userId,
            "locationAddress": form.locationAddress.data,
            "latitude": form.latitude.data,
            "longitude": form.longitude.data,
            "wasteType": form.wasteType.data,
            "description": form.description.data,
            "severityLevel": form.severityLevel.data,
            "periodOfOccurrence": form.periodOfOccurrence.data,
            "status": "Pending",
        }
        report = Report.create(details)

        if report:
            # Assign categories to the report
            for category_id in form.categories.data:
                report.assignCategory(category_id)

        # Create a folder for the report's images
        report_folder = os.path.join(
            flask.current_app.config["REPORT_IMAGES_UPLOAD_PATH"],
            str(report.reportId),
        )
        os.makedirs(report_folder, exist_ok=True)

        # Handle image upload
        if form.images.data:
            # Get the number of existing images in the report folder
            existing_images = glob.glob(os.path.join(report_folder, "*.jpg"))
            image_counter = len(existing_images) + 1

            for image in form.images.data:
                # Generate image filename using the report ID and the image
                # counter
                filename = f"{report.reportId}_{image_counter}.jpg"
                image_path = os.path.join(report_folder, filename)
                image.save(image_path)

                image_counter += 1

        flask.flash("Report submitted successfully!", "success")
        return flask.redirect(flask.url_for("profiles.dashboard"))

    return flask.render_template("profiles/create_report.html", form=form)


@profiles.route("/reports/<int:report_id>", methods=["GET", "POST"])
@login_required
@user_type_validator("user")
def report_details(report_id):
    report = Report.query.filter_by(reportId=report_id).first_or_404()

    if flask.request.method == "POST":
        comment_content = flask.request.form.get("comment-input")
        details = {
            "content": comment_content,
            "userId": current_user.userId,
            "reportId": report.reportId,
        }

        if comment_content:
            Comment.create(details)

            return flask.redirect(
                flask.url_for("profiles.report_details", report_id=report_id)
                + "#comments"
            )

    # retrieve image files associated with the report
    report_folder = os.path.join(
        flask.current_app.config["REPORT_IMAGES_UPLOAD_PATH"],
        str(report.reportId),
    )
    report_images = glob.glob(os.path.join(report_folder, "*.jpg"))
    report_images = [image.rsplit("/")[-1] for image in report_images]

    return flask.render_template(
        "profiles/report_details.html",
        report_images=report_images,
        report=report,
    )


@profiles.route("/users/<int:user_id>/reports", methods=["GET", "POST"])
@login_required
@user_type_validator("user")
def user_reports(user_id):
    user = User.query.filter_by(userId=user_id).first_or_404()
    return flask.render_template("profiles/user_reports.html", user=user)


@profiles.route("/reports/my-reports", methods=["GET", "POST"])
@login_required
@user_type_validator("user")
def my_reports():
    return flask.render_template("profiles/my_reports.html")


@profiles.route("/reports/latest-reports", methods=["GET"])
@login_required
@user_type_validator("user")
def latest_reports():
    reports = Report.query.limit(50)
    return flask.render_template(
        "profiles/latest_reports.html", reports=reports
    )


@profiles.route("/manage_categories", methods=["GET", "POST"])
@login_required
@user_type_validator("user")
def manage_categories():
    # Query all categories for display on table
    categories = Category.query.all()

    form = RegisterCategoryForm()
    if form.validate_on_submit():
        Category.create(
            {"name": form.name.data, "description": form.description.data}
        )

        flask.flash("Category created successfully", "success")
        return flask.redirect(flask.url_for("profiles.manage_categories"))

    return flask.render_template(
        "profiles/manage_categories.html", form=form, categories=categories
    )


@profiles.route("/manage_users")
@login_required
@user_type_validator("user")
def manage_users():
    contributors = User.query.all()
    return flask.render_template(
        "profiles/manage_users.html", contributors=contributors
    )


@profiles.route("/manage_handlers")
@login_required
@user_type_validator("user")
def manage_handlers():
    handlers = Handler.query.all()
    return flask.render_template(
        "profiles/manage_handlers.html", handlers=handlers
    )


@profiles.route("/manage_reports")
@login_required
@user_type_validator("user")
def manage_reports():
    reports = Handler.query.all()
    return flask.render_template(
        "profiles/manage_reports.html", reports=reports
    )


@profiles.route("/handlers/<int:handler_id>/reports", methods=["GET", "POST"])
@login_required
@user_type_validator("user")
def handler_reports(handler_id):
    handler = Handler.query.filter_by(handlerId=handler_id).first_or_404()
    return flask.render_template(
        "profiles/handler_reports.html", handler=handler
    )


@profiles.route("/handlers/<int:handler_id>/activate", methods=["GET", "POST"])
@login_required
@user_type_validator("user")
def activate_handler(handler_id):
    handler = Handler.query.filter_by(handlerId=handler_id).first_or_404()

    handler.isApproved = True
    db.session.add(handler)
    db.session.commit()

    flask.flash("Handler activated successfully", "success")
    return flask.redirect(flask.url_for("profiles.manage_handlers"))


@profiles.route(
    "/handlers/<int:handler_id>/deactivate", methods=["GET", "POST"]
)
@login_required
@user_type_validator("user")
def deactivate_handler(handler_id):
    handler = Handler.query.filter_by(handlerId=handler_id).first_or_404()

    handler.isApproved = False
    db.session.add(handler)
    db.session.commit()

    flask.flash("Handler deactivated successfully", "success")
    return flask.redirect(flask.url_for("profiles.manage_handlers"))
