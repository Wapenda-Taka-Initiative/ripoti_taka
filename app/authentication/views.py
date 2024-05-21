import flask
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from . import authentication
from .. import db

from .forms import LoginForm
from .forms import UnlockScreenForm
from .forms import ResetPasswordForm
from .forms import ForgotPasswordForm

from app.models import User


@authentication.before_app_request
def before_request():
    if (
        current_user.is_authenticated
        and not current_user.confirmed
        and flask.request.blueprint != "authentication"
        and flask.request.blueprint != "static"
    ):
        return flask.redirect(flask.url_for("authentication.unconfirmed"))


@authentication.route("/logout")
@login_required
def logout():
    logout_user()
    flask.flash("You've been logged out.")
    return flask.redirect(flask.url_for("authentication.login"))


@authentication.route("/login", methods=["GET", "POST"])
def login():
    # Ensure only unauthenticated users can login
    if current_user.is_authenticated:
        flask.flash("You are already logged in", "warning")
        return flask.redirect(flask.url_for("profiles.dashboard"))

    # Initialize login form
    form = LoginForm()

    # Set session as unlocked
    flask.session.permanent = True
    flask.session["locked"] = False

    # Check whether the user logged in by submitting to a form
    if form.validate_on_submit():
        user = User.query.filter_by(
            emailAddress=form.email_address.data
        ).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)

            # Set session as unlocked
            flask.session.permanent = True
            flask.session["locked"] = False

            next = flask.request.args.get("next")
            if next is None or not next.startswith("/"):
                next = flask.url_for("profiles.dashboard")
            return flask.redirect(next)

        flask.flash("Invalid username or password")
    return flask.render_template("authentication/login.html", form=form)


@authentication.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    # Ensure only unauthenticated users can access this
    if current_user.is_authenticated:
        flask.flash("You are already authenticated")
        return flask.redirect(flask.url_for("profiles.dashboard"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            emailAddress=form.email_address.data
        ).first()
        if user:
            user.sendPasswordResetEmail()

            # Render success message
            flask.flash("Password reset email sent successfully")
            return flask.redirect(
                flask.url_for("authentication.forgot_password")
            )

    return flask.render_template(
        "authentication/forgotten_password.html", form=form
    )


@authentication.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous:
        return flask.redirect(flask.url_for("main.index"))

    elif current_user.confirmed:
        return flask.redirect(flask.url_for("profiles.dashboard"))

    return flask.render_template("authentication/unconfirmed.html")


@authentication.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return flask.redirect(flask.url_for("main.index"))

    if current_user.confirm(token):
        db.session.commit()
        flask.flash("You have confirmed your account successfully. Welcome!!!")

    else:
        flask.flash("The confirmation link is invalid or has expired")

    return flask.redirect(flask.url_for("profiles.dashboard"))


@authentication.route("/confirm")
@login_required
def resend_confirmation_link():
    current_user.sendConfirmationEmail()
    flask.flash("A new confirmation email has been sent to you by email")
    return flask.redirect(flask.url_for("main.index"))


@authentication.route("/user/password-reset/<token>", methods=["GET", "POST"])
def user_password_reset(token):
    # Functionality limited to stranded users
    if not current_user.is_anonymous:
        return flask.redirect(flask.url_for("profiles.dashboard"))

    # Handle form rendering and submission
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Reset user's password
        successful = User.resetPassword(token, form.password.data)

        # Handle successful reset
        if successful:
            flask.flash("Password updated successfully")
            return flask.redirect(flask.url_for("authentication.login"))

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")
    return flask.render_template(
        "authentication/password_reset.html", form=form
    )


@authentication.route("/screen/lock", methods=["GET"])
@login_required
def lock_screen():
    # Ensure that unlocked sessions can do this
    if flask.session["locked"]:
        flask.flash("This session is already locked")
        return flask.redirect(flask.url_for("authentication.unlock_screen"))

    # Mark the session as locked
    flask.session.permanent = True
    flask.session["locked"] = True

    # Render success message
    flask.flash("Screen locked successfully. ")

    # Redirect to unlock screen
    return flask.redirect(flask.url_for("authentication.unlock_screen"))


@authentication.route("/screen/unlock", methods=["GET", "POST"])
@login_required
def unlock_screen():
    # Ensure only locked sessions can do this
    if not flask.session["locked"]:
        flask.flash("This session is not locked", "warning")
        return flask.redirect(flask.url_for("profiles.dashboard"))

    # Initialize unlock screen form
    form = UnlockScreenForm()

    if form.validate_on_submit():
        # Validate user password
        success = current_user.verify_password(form.password.data)
        if success:
            flask.session.permanent = True
            flask.session["locked"] = False

            # Render success message
            flask.flash("Screen unlocked successfully.", "success")
            return flask.redirect(flask.url_for("profiles.dashboard"))

        # Render failure message
        flask.flash(
            "You provided an invalid password. Please try again!", "critical"
        )

    return flask.render_template(
        "authentication/unlock_screen.html", form=form
    )
