from flask import render_template
from . import handlers


@handlers.app_errorhandler(403)
def forbidden(e):
    return render_template('handlers/403.html'), 403


@handlers.app_errorhandler(404)
def page_not_found(e):
    return render_template('handlers/404.html'), 404


@handlers.app_errorhandler(500)
def internal_server_error(e):
    return render_template('handlers/500.html'), 500
