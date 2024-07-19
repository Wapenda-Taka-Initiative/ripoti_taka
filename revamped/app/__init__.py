import flask
import flask_login
import flask_moment
import flask_mailman
import flask_bootstrap
import flask_sqlalchemy

from config import config

# Set endpoint for the login page
login_manager = flask_login.LoginManager()
login_manager.blueprint_login_views = {
    "administrators": "authentication.user_login",
    "handlers": "authentication.handler_login",
    "profiles": "profiles.user_login",
    "authentication": "authentication.user_login",
    "registration": "registration.user_login",
    "main": "authentication.user_login",
}

# Handle stale sessions
login_manager.refresh_view = "authentication.reauthenticate"
login_manager.needs_refresh_message = (
    "To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    from .models import Handler

    user_type = flask.session.get("user_type")
    if user_type == "user":
        user = User.query.get(int(user_id))

    elif user_type == "handler":
        user = Handler.query.get(int(user_id))

    else:
        user = None

    return user


db = flask_sqlalchemy.SQLAlchemy()
mail = flask_mailman.Mail()
bootstrap = flask_bootstrap.Bootstrap()
moment = flask_moment.Moment()


def create_app(config_name="default"):
    """
    Initialize and configure the Flask application.

    :param config_name: str - The name of the configuration class defined in
        config.py.

    :return app: Flask - The configured Flask application instance.
    """
    app = flask.Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    # Enable SSL redirection if configured
    if app.config["SSL_REDIRECT"]:
        from flask_sslify import SSLify

        SSLify(app)

    # Register blueprints for different parts of the application
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .authentication import authentication as authentication_blueprint

    app.register_blueprint(authentication_blueprint)

    from .registration import registration as registration_blueprint

    app.register_blueprint(registration_blueprint)

    from .administration import administration as administration_blueprint

    app.register_blueprint(administration_blueprint)

    from .profiles import profiles as profiles_blueprint

    app.register_blueprint(profiles_blueprint)

    from .handlers import handlers as handlers_blueprint

    app.register_blueprint(handlers_blueprint)

    return app
