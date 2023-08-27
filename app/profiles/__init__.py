from flask import Blueprint, current_app

profiles = Blueprint('profiles', __name__, url_prefix = '/profiles')
from . import views, errors

@profiles.app_context_processor
def global_variables():
    """
    Provides global variables that can be accessed directly within templates
    belonging to the 'profiles' blueprint.

    Returns:
        dict: A dictionary containing global variables to be injected into 
        templates.
    """
    return dict(app_name = current_app.config['ORGANIZATION_NAME'])
