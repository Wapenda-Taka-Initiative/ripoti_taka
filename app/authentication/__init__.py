from flask import Blueprint, current_app

authentication = Blueprint('authentication', __name__, 
        url_prefix = '/authentication')
from . import views, errors

@authentication.app_context_processor
def global_variables():
    """
    Provides global variables that can be accessed directly within templates
    belonging to the 'authentication' blueprint.

    Returns:
        dict: A dictionary containing global variables to be injected into 
        templates.
    """
    return dict(app_name = current_app.config['ORGANIZATION_NAME'])
