import os

from dotenv import load_dotenv
from flask_migrate import upgrade
from flask_migrate import Migrate

from app import db
from app import create_app
from app.models import Role


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, app=app)


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # Migrate the database to the latest version
    upgrade()

    # Create or update user roles
    Role.insert_roles()


if __name__ == "__main__":
    app.run()
