import flask
from flask_login import login_user, logout_user, login_required
from . import authentication
#from .forms import LoginUserForm
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
    return flask.render_template('authentication/login.html')


@authentication.route('/forgot_password')
def forgot_password():
    return flask.render_template('authentication/forgot_password.html')
