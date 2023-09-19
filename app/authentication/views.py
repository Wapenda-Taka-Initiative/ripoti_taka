import flask
from flask_login import login_user, logout_user, login_required, current_user
from . import authentication
from .forms import LoginForm
from .. import db
from ..models import User
from ..email import send_email


@authentication.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed \
            and flask.request.blueprint != 'authentication' \
            and flask.request.blueprint != 'static':
                return flask.redirect(flask.url_for('authentication.unconfirmed'))


@authentication.route('/logout')
@login_required
def logout():
    logout_user()
    flask.flash("You've been logged out.")
    return flask.redirect(flask.url_for('authentication.login'))


@authentication.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    
    # Check whether the user logged in by submitting to a form
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


@authentication.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous:
        return flask.redirect(flask.url_for('main.index'))

    elif current_user.confirmed:
        return flask.redirect(flask.url_for('profiles.dashboard'))

    return flask.render_template('authentication/unconfirmed.html')


@authentication.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return flask.redirect(flask.url_for('main.index'))

    if current_user.confirm():
        db.session.commit()
        flask.flash("You have confirmed your account successfully. Welcome!!!")

    else:
        flask.flash("The confirmation link is invalid or has expired")
    
    return flask.redirect(flask.url_for('main.index'))


@authentication.route('/confirm')
@login_required
def resend_confirmation_link():
    token = current_user.generate_confirmation_token()
    send_email(to = [current_user.emailAddress], 
            subject = "Welcome to the Ripoti Taka Program!", 
            template = "confirm_account", user = current_user, token = token)
    flask.flash("A new confirmation email has been sent to you by email")
    return flask.redirect(flask.url_for('main.index'))
