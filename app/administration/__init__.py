from flask import Blueprint, current_app

administration = Blueprint('administration', __name__, 
        url_prefix = '/administration')
from . import views, errors

@administration.app_context_processor
def global_variables():
    """
    Provides global variables that can be accessed directly within templates
    belonging to the 'administration' blueprint.

    Returns:
        dict: A dictionary containing global variables to be injected into 
        templates.
    """
    return dict(app_name = current_app.config['ORGANIZATION_NAME'])
