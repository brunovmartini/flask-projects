from flask import Blueprint, current_app
from flask_pydantic import validate
from flask_login import login_required

from decorators.decorators import manager_required
from repositories.user_repository import UserRepository
from resources.request.user_request import CreateUserRequest, UpdateUserRequest
from services.user.user_service import UserService
from settings.database import db

user_apis = Blueprint('user_apis', __name__)


@user_apis.route('/', methods=['POST'])
@validate()
@manager_required
def create_user(body: CreateUserRequest):
    """
    Create a new user. Only accessible by managers.

    :param body: CreateUserRequest object containing user data
    :type body: CreateUserRequest
    :return: JSON representation of the created user
    :rtype: dict
    :raises BadRequest: if request body is invalid
    :raises Conflict: if user email already exists
    """
    current_app.logger.info(f"Create user with email={body.email}")
    return UserService(repository=UserRepository(db_session=db.session)).create_user(body=body)


@user_apis.route('/', methods=['GET'])
@login_required
def get_users():
    """
    Retrieve all users.

    :return: List of users in JSON format
    :rtype: list[dict]
    """
    return UserService(repository=UserRepository(db_session=db.session)).get_users()


@user_apis.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id: int):
    """
    Retrieve a single user by ID.

    :param user_id: ID of the user
    :type user_id: int
    :return: User details in JSON format
    :rtype: dict
    :raises NotFound: if user with given ID does not exist
    """
    return UserService(repository=UserRepository(db_session=db.session)).get_user(user_id=user_id)


@user_apis.route('/<int:user_id>', methods=['PUT'])
@validate()
@manager_required
def update_user(user_id: int, body: UpdateUserRequest):
    """
    Update an existing user. Only accessible by managers.

    :param user_id: ID of the user to update
    :type user_id: int
    :param body: UpdateUserRequest object with updated user data
    :type body: UpdateUserRequest
    :return: Updated user details in JSON format
    :rtype: dict
    :raises BadRequest: if request body is invalid
    :raises NotFound: if user with given ID does not exist
    :raises Conflict: if user email already exists
    """
    current_app.logger.info(f"Update user: user_id={user_id}")
    return UserService(repository=UserRepository(db_session=db.session)).update_user(user_id=user_id, body=body)


@user_apis.route('/<int:user_id>', methods=['DELETE'])
@manager_required
def delete_user(user_id: int):
    """
    Delete a user by ID. Only accessible by managers.

    :param user_id: ID of the user to delete
    :type user_id: int
    :return: Response with deletion confirmation
    :rtype: flask.Response
    :raises NotFound: if user with given ID does not exist
    :raises Conflict: if trying to delete the currently logged-in user
    """
    current_app.logger.info(f"Delete user: user_id={user_id}")
    return UserService(repository=UserRepository(db_session=db.session)).delete_user(user_id=user_id)
