import flask

from . import administration


@administration.route("/shutdown")
def server_shutdown():
    if not flask.current_app.testing:
        flask.abort(404)

    shutdown = flask.request.environ.get("werkzeug.server.shutdown")
    if not shutdown:
        flask.abort(500)

    shutdown()
    return "Shutting down..."
