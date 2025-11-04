from datetime import datetime, timezone
from typing import List, Any

from flask import Response
from flask_login import login_user, current_user
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized, UnprocessableEntity
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from models.user import User
from repositories.user_repository import UserRepository
from resources.request.auth_request import LoginRequest
from resources.request.user_request import CreateUserRequest, UpdateUserRequest
from resources.response.user_response import UserResponse


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user_by_id(self, user_id: int) -> User | None:
        user = self.repository.get_by_id(id=user_id)
        if not user:
            raise NotFound(f'Not found user with id={user_id}.')
        return user

    def get_user_by_email(self, email: str) -> User | None:
        return self.repository.get_by_email(email=email)

    def login(self, data: LoginRequest) -> Response | None:
        if not data or "email" not in data or "password" not in data:
            raise BadRequest()

        user = self.get_user_by_email(email=data.get('email'))
        if not user or not check_password_hash(user.password, data.get('password')):
            raise Unauthorized('Invalid email or password.')

        login_user(user)

        return Response('Login successful.', status=200)

    def create_user(self, body: CreateUserRequest) -> dict[str, Any] | None:
        user = self.repository.create(
            User(
                email=body.email,
                password=generate_password_hash(body.password),
                username=body.username,
                name=body.name,
                user_type=body.user_type,
                created_at=datetime.now(timezone.utc),
                created_by=current_user.id
            )
        )
        return UserResponse.model_validate(user).model_dump()

    def get_users(self) -> List[dict[str, Any] | None]:
        return [UserResponse.model_validate(user).model_dump() for user in self.repository.get_all()]

    def get_user(self, user_id: int) -> dict[str, Any] | None:
        user = self.get_user_by_id(user_id=user_id)
        return UserResponse.model_validate(user).model_dump()

    def update_user(self, user_id: int, body: UpdateUserRequest) -> dict[str, Any] | None:
        user = self.get_user_by_id(user_id=user_id)

        user.update(body.__dict__)
        user.updated_at = datetime.now(timezone.utc)
        user.updated_by = current_user.id

        user = self.repository.update(user)
        return UserResponse.model_validate(user).model_dump()

    def delete_user(self, user_id: int) -> Response | None:
        user = self.get_user_by_id(user_id=user_id)

        if current_user.id == user.id:
            raise UnprocessableEntity()

        self.repository.delete(user)
        return Response(f'User with id={user_id} deleted.', status=200)
