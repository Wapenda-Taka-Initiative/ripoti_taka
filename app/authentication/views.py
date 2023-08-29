import flask
from flask_login import login_user, logout_user, login_required
from . import authentication
from .forms import LoginForm
from .. import db
from ..models import User

@authentication.route('/logout')
@login_required
def logout():
    logout_user()
    flask.flash("You've been logged out.")
    return flask.redirect(flask.url_for('authentication.login'))


@authentication.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(userName = form.user_name.data).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)

            next = flask.request.args.get('next')
            if next is None or not next.startswith('/'):
                next = flask.url_for('profiles.dashboard')
            return flask.redirect(next)

        flask.flash("Invalid username or password")
    return flask.render_template('authentication/login.html', form = form)


@authentication.route('/forgot_password')
def forgot_password():
    return flask.render_template('authentication/forgot_password.html')
