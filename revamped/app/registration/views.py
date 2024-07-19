import flask

from . import registration
from .forms import RegistrationForm
from .forms import HandlerRegistrationForm

from ..models import User
from ..models import Handler


# ------------------------------------------------------------------------------
#                                REGISTRATION
# ------------------------------------------------------------------------------
@registration.route("/handler/register", methods=["GET", "POST"])
def handler_registration():
    form = HandlerRegistrationForm()

    if form.validate_on_submit():
        details = {
            "name": form.name.data,
            "handlerType": form.handlerType.data,
            "resourceAvailability": form.resourceAvailability.data,
            "emailAddress": form.emailAddress.data.lower(),
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }
        Handler.registerAccount(details)

        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("authentication.handler_login"))

    return flask.render_template(
        "registration/handler_registration.html", form=form
    )


@registration.route("/user/register", methods=["GET", "POST"])
def user_registration():
    form = RegistrationForm()

    if form.validate_on_submit():
        details = {
            "emailAddress": form.emailAddress.data.lower(),
            "username": form.username.data,
            "phoneNumber": form.phoneNumber.data,
            "password": form.password.data,
        }
        User.registerAccount(details)

        flask.flash("Registration successful. Feel free to login.", "success")
        return flask.redirect(flask.url_for("authentication.user_login"))

    return flask.render_template(
        "registration/user_registration.html", form=form
    )
