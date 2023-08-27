import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
            'Fighting poverty, ignorance and diseases'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ORGANISATION_NAME = os.environ.get('ORGANISATION_NAME') or\
            'Ripoti Taka Program'

    REPORT_IMAGES_UPLOAD_PATH = os.path.join(basedir + 
            '/app/static/images/reports/')
    USER_IMAGES_UPLOAD_PATH = os.path.join(basedir + 
            '/app/static/images/profiles/')
    UPLOAD_EXTENSIONS = ['.jpg', '.gif', '.jpeg', '.png']


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


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
            or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
        'development' : DevelopmentConfig,
        'testing' : TestingConfig,
        'production' : ProductionConfig,
        'default' : DevelopmentConfig
        }
