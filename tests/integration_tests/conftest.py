import pytest
from flask import Flask
from werkzeug.security import generate_password_hash
from models.user import User

from resources.routers.auth_routes import auth_apis
from resources.routers.project_routes import project_apis
from resources.routers.user_routes import user_apis


@pytest.fixture
def client():
    import flask_login

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "testing-key"

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return None

    app.register_blueprint(auth_apis, url_prefix="/auth")
    app.register_blueprint(project_apis, url_prefix="/projects")
    app.register_blueprint(user_apis, url_prefix="/users")

    return app.test_client()


@pytest.fixture
def user():
    return User(
        id = 1,
        name="Auth Test User",
        username="authtest",
        email="authtest@example.com",
        password=generate_password_hash("password123"),
        user_type=1,
        created_by=1
    )


@pytest.fixture
def user_employee():
    return User(
        id=2,
        name="Employee Test User",
        username="employee",
        email="employee@example.com",
        password=generate_password_hash("employee123"),
        user_type=2,
        created_by=1
    )


def login_as(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True
