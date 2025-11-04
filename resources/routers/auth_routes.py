from flask import Blueprint, request, Response, current_app
from flask_login import logout_user, login_required

from repositories.user_repository import UserRepository
from services.user.user_service import UserService
from settings.database import db

auth_apis = Blueprint('auth_apis', __name__)


@auth_apis.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and log them in.

    Expects a JSON payload with:
        - email (str): User email
        - password (str): User password

    :return: Response object with status 200 on success
    :rtype: flask.Response
    :raises BadRequest: if request body is invalid
    :raises Unauthorized: if email or password is incorrect
    """
    current_app.logger.info(f"User login with email: {request.get_json().get('email')}")
    return UserService(repository=UserRepository(db_session=db.session)).login(data=request.get_json())


@auth_apis.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Log out the currently authenticated user.

    :return: Response object with status 200 on successful logout
    :rtype: flask.Response
    """
    logout_user()
    return Response('Logged out successfully.', status=200)
