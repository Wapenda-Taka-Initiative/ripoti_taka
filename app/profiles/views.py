import os
import glob
from datetime import datetime
from datetime import timedelta

import flask
from sqlalchemy import or_
from sqlalchemy import func
from geopy.geocoders import ArcGIS
from flask_login import current_user
from flask_login import login_required

from . import profiles
from .. import db

from .forms import CreateRewardForm
from .forms import CreateReportForm
from .forms import CreateCategoryForm

from app.models import User
from app.models import Report
from app.models import Reward
from app.models import Category
from app.models import Comment
from app.models import UserReward


@profiles.route("/user_profile")
@login_required
def user_profile():
    return flask.render_template(
        "profiles/user_profile.html", user=current_user
    )


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
    form.category_id.choices = category_choices

    if form.validate_on_submit():
        # Create a new Report object
        report = Report(
            location=form.location.data,
            categoryId=form.category_id.data,
            description=form.description.data,
            userId=current_user.userId,
        )

        # Retrieve longitude and latitude using geocoding
        geolocator = ArcGIS()
        location = form.location.data + " ,Kenya"
        try:
            location_info = geolocator.geocode(location)
            if location_info:
                report.latitude = location_info.latitude
                report.longitude = location_info.longitude
        except Exception:
            flask.flash(
                "Attempt to locate coordinates for provided location failed!",
                "failure",
            )
        db.session.add(report)
        db.session.commit()

        # Create a folder for the report's images
        report_folder = os.path.join(
            flask.current_profiles.config["REPORT_IMAGES_UPLOAD_PATH"],
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


@profiles.route("/edit_report", methods=["GET", "POST"])
@login_required
def edit_report():
    return flask.render_template("profiles/edit_report.html")


@profiles.route("/analytics")
@login_required
def analytics():
    reports = (
        Report.query.join(User)
        .join(Category)
        .outerjoin(Comment)
        .with_entities(
            Report.reportId,
            Report.dateCreated,
            User.userName.label("reporter"),
            Category.name.label("category"),
            Report.location,
            func.count(Comment.commentId).label("reactions"),
        )
        .group_by(Report.reportId)
        .order_by(Report.dateCreated.desc())
        .all()
    )

    count_by_date = [
        (report.dateCreated, report.reactions) for report in reports
    ]
    dates, counts = zip(*count_by_date)

    # Distribution of reports by category
    categories = (
        db.session.query(Category.name, func.count(Report.reportId))
        .join(Report)
        .group_by(Category.name)
        .all()
    )

    category_names = [row[0] for row in categories]
    report_counts = [row[1] for row in categories]

    # User engagement activity
    user_activity = (
        db.session.query(
            User.userName,
            func.count(Report.reportId),
            func.count(Comment.commentId),
            func.count(UserReward.userRewardId),
        )
        .outerjoin(Report, User.userId == Report.userId)
        .outerjoin(Comment, Report.reportId == Comment.reportId)
        .outerjoin(UserReward, User.userId == User_Reward.userId)
        .group_by(User.userName)
        .all()
    )

    usernames = [row[0] for row in user_activity]
    activity_report_counts = [row[1] for row in user_activity]
    comment_counts = [row[2] for row in user_activity]
    reward_counts = [row[3] for row in user_activity]

    # Top contributors and Rewards
    top_contributors = (
        db.session.query(User.userName, func.count(Report.reportId))
        .join(Report)
        .group_by(User.userName)
        .order_by(func.count(Report.reportId).desc())
        .limit(10)
        .all()
    )

    top_rewards = (
        db.session.query(Reward.name, func.count(UserReward.userRewardId))
        .join(UserReward)
        .group_by(Reward.name)
        .order_by(func.count(UserReward.userRewardId).desc())
        .limit(10)
        .all()
    )

    contributor_usernames = [row[0] for row in top_contributors]
    contributor_report_counts = [row[1] for row in top_contributors]

    reward_names = [row[0] for row in top_rewards]
    top_reward_counts = [row[1] for row in top_rewards]

    return flask.render_template(
        "profiles/analytics.html",
        dates=dates,
        counts=counts,
        category_names=category_names,
        activity_report_counts=activity_report_counts,
        usernames=usernames,
        report_counts=report_counts,
        comment_counts=comment_counts,
        reward_counts=reward_counts,
        contributor_usernames=contributor_usernames,
        contributor_report_counts=contributor_report_counts,
        reward_names=reward_names,
        top_reward_counts=top_reward_counts,
    )


@profiles.route("/explore")
@login_required
def explore():
    top_contributors = (
        db.session.query(
            User, func.count(Report.reportId).label("report_count")
        )
        .join(Report, User.userId == Report.userId)
        .group_by(User)
        .order_by(func.count(Report.reportId).desc())
        .limit(4)
    )
    new_members = User.query.filter(
        User.dateCreated >= (datetime.utcnow() - timedelta(days=7))
    ).all()

    members = User.query.order_by(User.userName).all()
    return flask.render_template(
        "profiles/explore.html",
        members=members,
        new_members=new_members,
        top_contributors=top_contributors,
    )


@profiles.route("/latest_reports")
@login_required
def latest_reports():
    reports = Report.query.order_by(Report.reportId.desc()).limit(12)
    return flask.render_template(
        "profiles/latest_reports.html", reports=reports
    )


@profiles.route("/manage_categories", methods=["GET", "POST"])
@login_required
def manage_categories():
    # Query all categories for display on table
    categories = Category.query.all()

    form = CreateCategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data, description=form.description.data
        )
        db.session.add(category)
        db.session.commit()

        flask.flash("Category created successfully", "success")
        return flask.redirect(flask.url_for("profiles.manage_categories"))

    return flask.render_template(
        "profiles/manage_categories.html", form=form, categories=categories
    )


@profiles.route("/report_details/<int:report_id>", methods=["GET", "POST"])
@login_required
def report_details(report_id):
    report = Report.query.filter_by(reportId=report_id).first_or_404()

    if flask.request.method == "POST":
        comment_content = flask.request.form.get("comment-input")

        if comment_content:
            new_comment = Comment(content=comment_content, report=report)
            db.session.add(new_comment)
            db.session.commit()

            return flask.redirect(
                flask.url_for("profiles.report_details", report_id=report_id)
            )

    # retrieve image files associated with the report
    report_folder = os.path.join(
        flask.current_app.config["REPORT_IMAGES_UPLOAD_PATH"],
        str(report.reportId),
    )
    report_images = glob.glob(os.path.join(report_folder, "*.jpg"))
    report_images = [image.rsplit("/")[-1] for image in report_images]

    # fetch comments associated with the report
    comments = (
        Comment.query.filter_by(reportId=report_id)
        .order_by(Comment.dateCreated.desc())
        .all()
    )

    return flask.render_template(
        "profiles/report_details.html",
        report_images=report_images,
        report=report,
        comments=comments,
    )


@profiles.route("/manage_reports")
@login_required
def manage_reports():
    return flask.render_template("profiles/manage_reports.html")


@profiles.route("/manage_rewards", methods=["GET", "POST"])
@login_required
def manage_rewards():
    # Query all rewards for display on table
    rewards = Reward.query.all()

    form = CreateRewardForm()
    if form.validate_on_submit():
        reward = Reward(
            name=form.name.data, pointsRequired=form.pointsRequired.data
        )
        db.session.add(reward)
        db.session.commit()

        flask.flash("Reward created successfully", "success")
        return flask.redirect(flask.url_for("profiles.manage_rewards"))

    return flask.render_template(
        "profiles/manage_rewards.html", rewards=rewards, form=form
    )


@profiles.route("/manage_users")
@login_required
def manage_users():
    contributors = (
        User.query.with_entities(
            User.userId,
            User.userName,
            User.emailAddress,
            func.count(Report.reportId).label("numReports"),
        )
        .join(Report, User.userId == Report.userId)
        .group_by(User.userId)
        .all()
    )
    return flask.render_template(
        "profiles/manage_users.html", contributors=contributors
    )


@profiles.route("/personal_analytics")
@login_required
def personal_analytics():
    assigned_rewards = UserReward.query.filter(
        User.userId == current_user.userId
    ).all()
    claimed_rewards = UserReward.query.filter(
        User.userId == current_user.userId
    ).all()
    rewards_eligible = Reward.query.filter(
        Reward.pointsRequired <= int(current_user.pointsAcquired)
    ).all()
    rewards = Reward.query.all()
    return flask.render_template(
        "profiles/personal_analytics.html",
        claimed_rewards=claimed_rewards,
        assigned_rewards=assigned_rewards,
        rewards=rewards,
        rewards_eligible=rewards_eligible,
    )


@profiles.route("/user_profile/<int:user_id>")
@login_required
def contributor_profile(user_id):
    user = User.query.get(user_id)
    return flask.render_template("profiles/user_profile.html", user=user)


@profiles.route("/search_reports", methods=["GET", "POST"])
@login_required
def search_reports():
    search_term = flask.request.form["search-term"]
    reports = (
        db.session.query(Report)
        .filter(
            or_(
                Report.location.like(f"%{search_term}%"),
                Report.description.like(f"%{search_term}%"),
                Category.name.like(f"%{search_term}%"),
            )
        )
        .all()
    )
    return flask.render_template(
        "profiles/latest_reports.html", reports=reports
    )
