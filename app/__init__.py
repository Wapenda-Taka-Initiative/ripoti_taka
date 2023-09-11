import flask
import flask_sqlalchemy
import flask_bootstrap
import flask_mail
import flask_moment
from flask_login import LoginManager
from config import config

#set endpoint for the login page
login_manager = LoginManager()
login_manager.login_view = 'authentication.login'

mail = flask_mail.Mail()
db = flask_sqlalchemy.SQLAlchemy()
moment = flask_moment.Moment()
bootstrap = flask_bootstrap.Bootstrap()

def create_app(config_name):
    """
    Application initialization.
    Takes as an argument one of the configuration classes defined in config.py
    """

    app = flask.Flask(__name__)
    app.config.from_object(config[config_name])

    mail.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

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
    
    return app
