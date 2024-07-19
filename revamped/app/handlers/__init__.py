from flask import Blueprint, current_app

handlers = Blueprint("handlers", __name__, url_prefix="/handlers")
from . import views, errors


@handlers.app_context_processor
def global_variables():
    """
    Provides global variables that can be accessed directly within templates
    belonging to the 'handlers' blueprint.

    :return: Dict - A dictionary containing global variables to be injected
        into templates.
    """
    return dict(app_name=current_app.config["ORGANIZATION_NAME"])
