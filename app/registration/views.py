import os
import json
import secrets
import requests
from urllib.parse import urlencode

import flask
from flask_login import login_user
from flask_login import current_user
from flask_login import login_required

from . import registration
from .. import db

from .forms import RegistrationForm
from .forms import EditUserProfileForm

from app.models import User
from utilities.email import send_email


@registration.route(
    "/edit_profile_image/<int:user_id>", methods=["GET", "POST"]
)
@login_required
def edit_profile_image(user_id):
    user = User.query.get(user_id)
    image_file = flask.request.files.get("profile-image")
    if image_file:
        filename = f"{user_id}.{image_file.filename.split('.')[-1]}"

        # Save file in local storage
        images_path = flask.current_app.config["USER_IMAGES_UPLOAD_PATH"]
        os.makedirs(images_path, exist_ok=True)
        image_path = os.path.join(images_path, filename)
        image_file.save(image_path)

        # Update user profileUrl in database
        user.imageUrl = filename
        db.session.add(user)
        db.session.commit()
        flask.flash("Profile image updated successfully")

        # Redirect user accordingly
        return flask.redirect(
            flask.url_for("profiles.contributor_profile", user_id=user_id)
        )

    # No image found
    flask.flash("Profile image update failed")
    return flask.redirect(
        flask.url_for("profiles.contributor_profile", user_id=user_id)
    )


@registration.route("/register", methods=["GET", "POST"])
def register_user():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            emailAddress=form.email_address.data,
            userName=form.user_name.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            "Confirm Your Account",
            "authentication/email/confirm",
            user=user,
            token=token,
        )
        flask.flash("A confirmation email has been sent to you.")
        return flask.redirect(flask.url_for("main.index"))

    return flask.render_template("registration/register_user.html", form=form)


@registration.route(
    "/edit_user_profile/<int:user_id>", methods=["GET", "POST"]
)
@login_required
def edit_user_profile(user_id):
    user = User.query.get(user_id)

    form = EditUserProfileForm()
    form.gender.choices = [("Male", "Male"), ("Female", "Female")]
    if form.validate_on_submit():
        user.firstName = form.firstName.data
        user.middleName = form.middleName.data
        user.lastName = form.lastName.data
        user.gender = form.gender.data
        user.phoneNumber = form.phoneNumber.data
        user.locationAddress = form.locationAddress.data
        user.about_me = form.about_me.data

        db.session.add(user)
        db.session.commit()
        flask.flash("User profile updated successfully")

        if user.userId == current_user.userId:
            return flask.redirect(flask.url_for("profiles.user_profile"))
        else:
            return flask.redirect(
                flask.url_for("profiles.contributor_profile", user_id=user_id)
            )

    form.firstName.data = user.firstName
    form.middleName.data = user.middleName
    form.lastName.data = user.lastName
    form.phoneNumber.data = user.phoneNumber
    form.gender.data = user.gender
    form.locationAddress.data = user.locationAddress
    form.about_me.data = user.about_me

    return flask.render_template(
        "registration/edit_user_profile.html", form=form, user_id=user_id
    )


@registration.route("/authorize/<provider>")
def oauth2_authorize(provider):
    # Functionality reserved for anonymous users only
    if not current_user.is_anonymous:
        return flask.redirect(flask.url_for("profiles.dashboard"))

    provider_data = flask.current_app.config["OAUTH2_PROVIDERS"].get(provider)
    # Ensure requested provider is in the configuration
    if provider_data is None:
        flask.abort(404)

    # Generate a random string for the state parameter
    flask.session["oauth2_state"] = secrets.token_urlsafe(16)

    # Create a query string with all the OAuth2 parameters
    query_string = urlencode(
        {
            "client_id": provider_data["client_id"],
            "redirect_uri": flask.url_for(
                "registration.oauth2_callback",
                provider=provider,
                _external=True,
            ),
            "response_type": "code",
            "scope": " ".join(provider_data["scopes"]),
            "state": flask.session["oauth2_state"],
        }
    )
    # Redirect the user to the OAuth2 provider authorization URL
    return flask.redirect(provider_data["authorize_url"] + "?" + query_string)


@registration.route("/callback/<provider>")
def oauth2_callback(provider):
    if not is_user_anonymous():
        return redirect_to_dashboard()

    provider_data = get_provider_data(provider)
    if provider_data is None:
        flask.abort(404)

    if has_authentication_error():
        flash_authentication_errors()
        return redirect_to_main_index()

    if not is_state_valid():
        flask.abort(401)

    if not has_authorization_code():
        flask.abort(401)

    oauth2_token = exchange_code_for_token(provider_data)
    if not oauth2_token:
        flask.abort(401)

    store_token_in_file(oauth2_token)

    email = get_user_email(provider_data, oauth2_token)
    if not email:
        flask.abort(401)

    user = find_or_create_user(email)

    login_user(user)
    return redirect_to_dashboard()


def is_user_anonymous():
    return current_user.is_anonymous


def redirect_to_dashboard():
    return flask.redirect(flask.url_for("profiles.dashboard"))


def redirect_to_main_index():
    return flask.redirect(flask.url_for("main.index"))


def get_provider_data(provider):
    return flask.current_app.config["OAUTH2_PROVIDERS"].get(provider)


def has_authentication_error():
    return "error" in flask.request.args


def flash_authentication_errors():
    for key, value in flask.request.args.items():
        if key.startswith("error"):
            flask.flash(f"{key} : {value}")


def is_state_valid():
    return flask.request.args.get("state") == flask.session.get("oauth2_state")


def has_authorization_code():
    return "code" in flask.request.args


def exchange_code_for_token(provider_data):
    response = requests.post(
        provider_data["token_url"],
        data={
            "client_id": provider_data["client_id"],
            "client_secret": provider_data["client_secret"],
            "code": flask.request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": flask.url_for(
                "registration.oauth2_callback",
                provider=provider_data["name"],
                _external=True,
            ),
        },
        headers={"Accept": "application/json"},
    )

    if response.status_code != 200:
        return None

    return response.json().get("access_token")


def store_token_in_file(oauth2_token):
    token_file = os.path.join(
        flask.current_app.config["SECRETS_PATH"], "token.json"
    )
    with open(token_file, "w") as token:
        json.dump({"access_token": oauth2_token}, token)


def get_user_email(provider_data, oauth2_token):
    response = requests.get(
        provider_data["userinfo"]["url"],
        headers={
            "Authorization": "Bearer " + oauth2_token,
            "Accept": "application/json",
        },
    )

    if response.status_code != 200:
        return None

    return provider_data["userinfo"]["email"](response.json())


def find_or_create_user(email):
    user = db.session.scalar(db.select(User).where(User.emailAddress == email))
    if user is None:
        user = User(
            emailAddress=email,
            userName=email.split("@")[0],
            confirmed=True,
            password="password",
        )
        db.session.add(user)
        db.session.commit()
    return user
