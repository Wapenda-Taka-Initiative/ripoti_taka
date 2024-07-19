import flask
from flask_login import current_user
from flask_login import login_required


from . import authentication
from .forms import HandlerLoginForm
from .forms import UserLoginForm
from .forms import PasswordResetForm

from ..models import db
from ..models import Handler
from ..models import User

from utilities.authentication import user_type_validator


# ------------------------------------------------------------------------------
#                                 SIGNING IN                                  -
# ------------------------------------------------------------------------------
@authentication.route("/handler/login", methods=["GET", "POST"])
def handler_login():
    # Limit functionality to Anonymous Handlers
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("handlers.dashboard"))

    form = HandlerLoginForm()

    if form.validate_on_submit():
        # Find handler with given email address
        handler = Handler.query.filter_by(
            emailAddress=form.emailAddress.data.lower()
        ).first()

        # Login handler if found
        details = {
            "password": form.password.data,
            "remember_me": form.remember_me.data,
        }

        if handler:
            success, message = handler.login(details)

            if success:
                next = flask.request.args.get("next")
                if not next or not next.startswith("/"):
                    next = flask.url_for("handlers.dashboard")

                flask.flash(
                    f"Hello {current_user.name}. Welcome back!", "success"
                )
                return flask.redirect(next)

        # Notify handler of invalid credentials
        flask.flash(
            "You provided invalid credentials. Please try again.", "warning"
        )

    return flask.render_template(
        "authentication/handler_login.html", form=form
    )


@authentication.route("/user/login", methods=["GET", "POST"])
def user_login():
    # Limit functionality to Anonymous Handlers
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for("profiles.dashboard"))

    form = UserLoginForm()

    if form.validate_on_submit():
        details = {
            "password": form.password.data,
            "remember_me": form.remember_me.data,
        }

        # Find handler with given email address
        user = User.query.filter_by(
            emailAddress=form.emailAddress.data.lower()
        ).first()

        # Login handler if found
        if user:
            success, message = user.login(details)

            if success:
                next = flask.request.args.get("next")
                if not next or not next.startswith("/"):
                    next = flask.url_for("profiles.dashboard")

                flask.flash(f"Hello {current_user.username}. Welcome back!")
                return flask.redirect(next)

        # Notify handler of invalid credentials
        flask.flash(
            "You provided invalid credentials. Please try again.", "warning"
        )

    return flask.render_template("authentication/user_login.html", form=form)


# ------------------------------------------------------------------------------
#                                SIGNING OUT                                  -
# ------------------------------------------------------------------------------
@authentication.route("/user/logout")
@login_required
@user_type_validator("user")
def user_logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.", "success")
    return flask.redirect(flask.url_for("authentication.user_login"))


@authentication.route("/handler/logout")
@login_required
@user_type_validator("handler")
def handler_logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.", "success")
    return flask.redirect(flask.url_for("authentication.handler_login"))


@authentication.route("/expert/logout")
@login_required
@user_type_validator("expert")
def expert_logout():
    current_user.logout()
    flask.flash("You have been logged out successfully.")
    return flask.redirect(flask.url_for("authentication.expert_login"))


# ------------------------------------------------------------------------------
#                           PASSWORD RESET REQUEST                            -
# ------------------------------------------------------------------------------
@authentication.route("/user/password-reset-request", methods=["GET", "POST"])
def user_password_reset_request():
    if flask.request.method == "POST":
        # Retrieve user
        email_address = flask.request.form["email"]
        user = User.query.filter_by(emailAddress=email_address).first()

        # Check if user exists
        if user:
            # Send password reset email
            user.sendPasswordResetEmail()

            # Flash success message
            flask.flash("Password reset email sent successfully")
            return flask.redirect(
                flask.url_for("authentication.user_password_reset_request")
            )

        # Flash error message
        flask.flash("The provided email address is invalid", "failure")

    return flask.render_template("authentication/password_reset_request.html")


@authentication.route(
    "/handler/password-reset-request", methods=["GET", "POST"]
)
def handler_password_reset_request():
    if flask.request.method == "POST":
        # Retrieve handler
        email_address = flask.request.form["email"]
        handler = Handler.query.filter_by(emailAddress=email_address).first()

        # Check if handler exists
        if handler:
            # Send password reset email
            handler.sendPasswordResetEmail()

            # Flash success message
            flask.flash("Password reset email sent successfully")
            return flask.redirect(
                flask.url_for("authentication.handler_password_reset_request")
            )

        # Flash error message
        flask.flash("The provided email address is invalid", "failure")

    return flask.render_template("authentication/password_reset_request.html")


# -----------------------------------------------------------------------------
#                               PASSWORD RESET                              -
# -----------------------------------------------------------------------------
@authentication.route("/user/password-reset/<token>", methods=["GET", "POST"])
def user_password_reset(token):
    # Functionality limited to stranded users
    if not current_user.is_anonymous:
        return flask.redirect(flask.url_for("profiles.dashboard"))

    # Handle form rendering and submission
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Reset user's password
        successful = User.resetPassword(token, form.password.data)

        # Handle successful reset
        if successful:
            flask.flash("Password updated successfully")
            return flask.redirect(flask.url_for("authentication.user_login"))

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")

    return flask.render_template(
        "authentication/password_reset.html", form=form
    )


@authentication.route(
    "/handler/password-reset/<token>", methods=["GET", "POST"]
)
def handler_password_reset(token):
    # Functionality limited to stranded handlers
    if not current_user.is_anonymous:
        return flask.redirect(flask.url_for("handlers.dashboard"))

    # Handle form rendering and submission
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Reset handler's password
        successful = Handler.resetPassword(token, form.password.data)

        # Handle successful reset
        if successful:
            flask.flash("Password updated successfully")
            return flask.redirect(
                flask.url_for("authentication.handler_login")
            )

        # Flash failure message
        flask.flash("The link you used is either expired or corrupted")
    return flask.render_template(
        "authentication/password_reset.html", form=form
    )


# -----------------------------------------------------------------------------
#                           ACCOUNT CONFIRMATION                              -
# -----------------------------------------------------------------------------
@authentication.route("/user/confirm/<int:user_id>/<token>")
def user_confirm(user_id, token):
    """Confirms email address of registered user"""
    template = "authentication/confirmation.html"

    # Retrieve specified user
    current_user = User.query.get(user_id)
    if not current_user:
        return flask.render_template(template, invalid_token=True)

    if current_user.isConfirmed:
        return flask.render_template(template, handler_already_confirmed=True)

    confirmation_result = current_user.confirm(token)

    if confirmation_result:
        db.session.commit()
        return flask.render_template(template, success=True)
    else:
        return flask.render_template(template, invalid_token=True)


@authentication.route("/handler/confirm/<int:handler_id>/<token>")
def handler_confirm(handler_id, token):
    """Confirms email address of registered handler"""
    template = "authentication/confirmation.html"

    # Retrieve specified expert
    current_user = Handler.query.get(handler_id)
    if not current_user:
        return flask.render_template(template, invalid_token=True)

    if current_user.isConfirmed:
        return flask.render_template(template, handler_already_confirmed=True)

    confirmation_result = current_user.confirm(token)

    if confirmation_result:
        db.session.commit()
        return flask.render_template(template, success=True)
    else:
        return flask.render_template(template, invalid_token=True)


@authentication.route("/resend-confirmation-link/expert")
@login_required
@user_type_validator("expert")
def resend_confirmation_link_expert():
    current_user.sendConfirmationEmail()
    flask.flash("A new confirmation email has been sent to you via email")
    return flask.redirect(flask.url_for("authentication.unconfirmed_expert"))


@authentication.route("/unconfirmed/expert")
@login_required
@user_type_validator("expert")
def unconfirmed_expert():
    if current_user.is_anonymous:
        return flask.redirect(flask.url_for("main.index"))

    elif current_user.isConfirmed:
        return flask.redirect(flask.url_for("experts.dashboard"))

    return flask.render_template("authentication/unconfirmed.html")


# ---------------------------------------------------------------------------
#                          HANDLE STALE SESSIONS                            -
# ---------------------------------------------------------------------------
@authentication.route("/reauthenticate")
@login_required
def reauthenticate():
    handler = flask.session["user_type"]
    return flask.redirect(flask.url_for(f"authentication.{handler}_logout"))
