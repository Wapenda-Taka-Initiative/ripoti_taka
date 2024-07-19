import flask

from . import main


@main.route("/")
@main.route("/home")
@main.route("/homepage")
def index():
    return flask.render_template("main/index.html")


@main.route("/get_involved")
def get_involved():
    return flask.render_template("main/get_involved.html")


@main.route("/contact_us")
def contact_us():
    return flask.render_template("main/contact.html")


@main.route("/terms_and_conditions")
def terms_and_conditions():
    return flask.render_template("main/terms_and_conditions.html")


@main.route("/privacy_policy")
def privacy_policy():
    return flask.render_template("main/privacy_policy.html")
