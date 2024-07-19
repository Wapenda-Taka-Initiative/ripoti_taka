from flask import Blueprint
from flask import current_app

main = Blueprint("main", __name__)
from . import views, errors


@main.app_context_processor
def global_variables():
    """
    Provides global variables that can be accessed directly within templates
    belonging to the 'main' blueprint.

    :return: Dict - A dictionary containing global variables to be injected
        into templates.
    """
    return dict(app_name=current_app.config["ORGANIZATION_NAME"])
