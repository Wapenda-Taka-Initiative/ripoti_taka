import flask
from . import registration
from .. import db
from ..models import User


@registration.route('/register', methods = ['GET', 'POST'])
def register_user():
    return flask.render_template('registration/register_user.html')
