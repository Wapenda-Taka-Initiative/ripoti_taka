from flask import Blueprint, current_app

registration = Blueprint('registration', __name__, url_prefix = '/registration')
from . import utilities, views, errors

@registration.app_context_processor
def global_variables():
    """
    Provides global variables that can be accessed directly within templates
    belonging to the 'registration' blueprint.

    Returns:
        dict: A dictionary containing global variables to be injected into 
        templates.
    """
    return dict(app_name = current_app.config['ORGANIZATION_NAME'])
