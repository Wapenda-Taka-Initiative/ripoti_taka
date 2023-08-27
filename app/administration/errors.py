from flask import render_template
from . import administration


@administration.app_errorhandler(403)
def forbidden(e):
    return render_template('administration/403.html'), 403


@administration.app_errorhandler(404)
def page_not_found(e):
    return render_template('administration/404.html'), 404


@administration.app_errorhandler(500)
def internal_server_error(e):
    return render_template('administration/500.html'), 500
