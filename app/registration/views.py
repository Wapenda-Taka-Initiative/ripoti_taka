import flask
from . import registration
from .forms import RegistrationForm
from .. import db
from ..models import User


@registration.route('/register', methods = ['GET', 'POST'])
def register_user():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
                emailAddress = form.email_address.data,
                userName = form.user_name.data,
                password = form.password.data)
        db.session.add(user)
        db.session.commit()
        flask.flash("Registration successful. Welcome to the revolution!!!")
        return flask.redirect(flask.url_for('authentication.login'))

    return flask.render_template('registration/register_user.html', form = form)
