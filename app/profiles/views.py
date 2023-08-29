import os
import flask
import glob
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from geopy.geocoders import ArcGIS
from . import profiles
from .forms import CreateReportForm, CreateCategoryForm
from .. import db
from ..models import User, Report, Category


@profiles.route('/dashboard')
@login_required
def dashboard():
    reports = Report.query.order_by(Report.reportId.desc()).all()
    return flask.render_template('profiles/dashboard.html', reports = reports)


@profiles.route('/create_report', methods = ['GET', 'POST'])
@login_required
def create_report():
    form = CreateReportForm()

    # Populate options for the category_id field of the form
    categories = Category.query.all()
    category_choices = [(category.categoryId, category.name)
            for category in categories]
    form.category_id.choices = category_choices

    if form.validate_on_submit():
        # Create a new Report object
        report = Report(
                location = form.location.data,
                categoryId = form.category_id.data,
                description = form.description.data,
                userId = current_user.userId)

        # Retrieve longitude and latitude using geocoding
        geolocator = ArcGIS()
        location = form.location.data + ' ,Kenya'
        try:
            location_info = geolocator.geocode(location)
            if location_info:
                report.latitude = location_info.latitude
                report.longitude = location_info.longitude
        except Exception as e:
            flask.flash("Attempt to locate coordinates for provided location failed!", "failure")
        db.session.add(report)
        db.session.commit()

        # Create a folder for the report's images
        report_folder = os.path.join(
                flask.current_app.config['REPORT_IMAGES_UPLOAD_PATH'],
                str(report.reportId))
        os.makedirs(report_folder, exist_ok = True)

        # Handle image upload
        if form.images.data:
            # Get the number of existing images in the report folder
            existing_images = glob.glob(os.path.join(report_folder, '*.jpg'))
            image_counter = len(existing_images) + 1

            for image in form.images.data:
                # Generate image filename using the report ID and the image counter
                filename = f"{report.reportId}_{image_counter}.jpg"
                image_path = os.path.join(report_folder, filename)
                image.save(image_path)

                image_counter += 1

        flask.flash("Report submitted successfully!", "success")
        return flask.redirect(flask.url_for('profiles.create_report'))

    return flask.render_template('profiles/create_report.html', form = form)


@profiles.route('/edit_report', methods = ['GET', 'POST'])
@login_required
def edit_report():
    return flask.render_template('profiles/edit_report.html')


@profiles.route('/analytics')
@login_required
def analytics():
    return flask.render_template('profiles/analytics.html')


@profiles.route('/explore')
@login_required
def explore():
    return flask.render_template('profiles/explore.html')


@profiles.route('/geographics')
@login_required
def geographics():
    return flask.render_template('profiles/geographics.html')


@profiles.route('/latest_reports')
@login_required
def latest_reports():
    return flask.render_template('profiles/latest_reports.html')


@profiles.route('/manage_categories', methods = ['GET', 'POST'])
@login_required
def manage_categories():
    # Query all categories for display on table
    categories = Category.query.all()

    form = CreateCategoryForm()
    if form.validate_on_submit():
        category = Category(
                name = form.name.data,
                description = form.description.data)
        db.session.add(category)
        db.session.commit()

        flask.flash("Category created successfully", "success")
        return flask.redirect(flask.url_for('profiles.manage_categories'))

    return flask.render_template('profiles/manage_categories.html', form = form,
            categories = categories)


@profiles.route('/report_details/<int:report_id>')
@login_required
def report_details(report_id):
    report = Report.query.filter_by(reportId = report_id).first_or_404()
    report_folder = os.path.join(
            flask.current_app.config['REPORT_IMAGES_UPLOAD_PATH'],
            str(report.reportId))
    existing_images = glob.glob(os.path.join(report_folder, '*.jpg'))
    return flask.render_template('profiles/report_details.html',
            existing_images = existing_images, report = report)


@profiles.route('/manage_reports')
@login_required
def manage_reports():
    return flask.render_template('profiles/manage_reports.html')


@profiles.route('/manage_rewards')
@login_required
def manage_rewards():
    return flask.render_template('profiles/manage_rewards.html')


@profiles.route('/manage_users')
@login_required
def manage_users():
    return flask.render_template('profiles/manage_users.html')


@profiles.route('/personal_analytics')
@login_required
def personal_analytics():
    return flask.render_template('profiles/personal_analytics.html')
