import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
            'Fighting poverty, ignorance and diseases'

    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.5

    ORGANIZATION_NAME = os.environ.get('ORGANISATION_NAME') or\
            'Ripoti Taka Program'

    # Location for Gmail API credentials
    CREDENTIALS_PATH = os.path.join(basedir + '/secrets/')

    REPORT_IMAGES_UPLOAD_PATH = os.path.join(basedir +
            '/app/static/images/reports/')
    USER_IMAGES_UPLOAD_PATH = os.path.join(basedir +
            '/app/static/images/profiles/')
    UPLOAD_EXTENSIONS = ['.jpg', '.gif', '.jpeg', '.png']

    COMMUNICATIONS_EMAIL = os.environ.get('COMMUNICATIONS_EMAIL') or\
            'ripoti.wapendataka@gmail.com'
    ADMINISTRATOR_EMAIL = os.environ.get('ADMINISTRATOR_EMAIL') or\
            'ripoti.wapendataka@gmail.com'


    OAUTH2_PROVIDERS = {
            'google' : {
                'client_id' : os.environ.get('GOOGLE_CLIENT_ID'),
                'client_secret' : os.environ.get('GOOGLE_CLIENT_SECRET'),
                'authorize_url' : 'https://accounts.google.com/o/oauth2/auth',
                'token_url' : 'https://accounts.google.com/o/oauth2/token',
                'userinfo' : {
                    'url' : 'https://www.googleapis.com/oauth2/v3/userinfo',
                    'email' : lambda json: json['email'],
                    },
                'scopes' : ['https://www.googleapis.com/auth/userinfo.email'],
                },

            'github' : {
                'client_id' : os.environ.get('GITHUB_CLIENT_ID'),
                'client_secret' : os.environ.get('GITHUB_CLIENT_SECRET'),
                'authorize_url' : 'https://github.com/login/oauth/authorize',
                'token_url' : 'https://github.com/login/oauth/access_token',
                'userinfo' : {
                    'url' : 'https://api.github.com/user/emails',
                    'email' : lambda json: json[0]['email'],
                    },
                'scopes' : ['user:email']
                },
            }


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') \
            or 'sqlite:///' + os.path.join(basedir, 'data-dev-sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'
    WTF_CRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
            or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler

        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure()

        mail_handler = SMTPHandler(
                mailhost = (cls.MAIL_SERVER, cls.MAIL_PORT),
                fromaddr = cls.COMMUNICATIONS_EMAIL,
                toaddrs = [cls.ADMINISTRATOR_EMAIL],
                subject = 'Application Error',
                credentials = credentials,
                secure = secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    pass


class DockerConfig(ProductionConfig):
    pass


class UnixConfig(ProductionConfig):
    pass


config = {
        'development' : DevelopmentConfig,
        'testing' : TestingConfig,
        'production' : ProductionConfig,
        'heroku' : HerokuConfig,
        'docker' : DockerConfig,
        'unix' : UnixConfig,
        'default' : DevelopmentConfig
        }
