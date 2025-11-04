from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from flask import Response
from models.user import User
from resources.request.user_request import CreateUserRequest
from resources.response.user_response import UserResponse
from resources.response.user_type_response import UserTypeResponse
from services.user.user_service import UserService
from werkzeug.exceptions import (
    BadRequest,
    NotFound,
    Unauthorized,
    UnprocessableEntity,
)


@pytest.fixture
def service(mock_repository):
    return UserService(repository=mock_repository)


@pytest.fixture
def fake_user():
    user = User(
        id=1,
        email="test@example.com",
        password="hashed_pw",
        username="tester",
        name="Test User",
        user_type=1,
        created_at=datetime.now(timezone.utc),
        created_by=1,
    )
    user.update = Mock()
    return user


@pytest.fixture
def fake_request():
    return CreateUserRequest(
        email="new@example.com",
        password="plain_password",
        username="newuser",
        name="New User",
        user_type=1,
    )


def test_get_user_by_id_success(service, mock_repository, fake_user):
    mock_repository.get_by_id.return_value = fake_user
    result = service.get_user_by_id(1)
    assert result == fake_user
    mock_repository.get_by_id.assert_called_once_with(id=1)


def test_get_user_by_id_not_found(service, mock_repository):
    mock_repository.get_by_id.return_value = None
    with pytest.raises(NotFound):
        service.get_user_by_id(999)


def test_get_user_by_email_success(service, mock_repository, fake_user):
    mock_repository.get_by_email.return_value = fake_user
    result = service.get_user_by_email("test@example.com")
    assert result == fake_user
    mock_repository.get_by_email.assert_called_once_with(email="test@example.com")


@patch("services.user.user_service.login_user")
@patch("services.user.user_service.check_password_hash", return_value=True)
def test_login_success(mock_check, mock_login, service, fake_user):
    with patch.object(service, "get_user_by_email", return_value=fake_user):
        req = {"email": "test@example.com", "password": "123"}
        response = service.login(req)
        assert isinstance(response, Response)
        assert response.status_code == 200
        mock_login.assert_called_once_with(fake_user)
        mock_check.assert_called_once_with(fake_user.password, "123")


def test_login_missing_fields(service):
    with pytest.raises(BadRequest):
        service.login({"email": "test@example.com"})


@patch("services.user.user_service.check_password_hash", return_value=False)
def test_login_invalid_password(mock_check, service, fake_user):
    with patch.object(service, "get_user_by_email", return_value=fake_user):
        with pytest.raises(Unauthorized):
            service.login({"email": "test@example.com", "password": "wrong"})


def test_login_user_not_found(service):
    with patch.object(service, "get_user_by_email", return_value=None):
        with pytest.raises(Unauthorized):
            service.login({"email": "notfound@example.com", "password": "123"})


@patch("services.user.user_service.generate_password_hash", return_value="hashed_pw")
def test_create_user_success(
    mock_hash, service, mock_repository, fake_user, fake_request
):
    mock_repository.create.return_value = fake_user
    with patch("services.user.user_service.current_user") as mock_current_user:
        mock_current_user.id = 2
        with patch.object(service, "get_user_by_email", return_value=None), patch(
            "services.user.user_service.UserResponse.model_validate",
            return_value=UserResponse.model_validate(
                {
                    "id": 1,
                    "email": fake_user.email,
                    "name": fake_user.name,
                    "username": fake_user.username,
                    "type": UserTypeResponse(id=1, user_type="manager"),
                    "created_by": 2,
                    "updated_by": None,
                }
            ),
        ) as mock_response:

            result = service.create_user(fake_request)
            assert result == {
                "id": 1,
                "email": fake_user.email,
                "name": fake_user.name,
                "username": fake_user.username,
                "type": {"id": 1, "user_type": "manager"},
                "created_by": 2,
                "updated_by": None,
            }
            mock_repository.create.assert_called_once()
            mock_hash.assert_called_once_with(fake_request.password)
            mock_response.assert_called_once()


def test_get_users_success(service, mock_repository, fake_user):
    mock_repository.get_all.return_value = [fake_user]
    with patch("services.user.user_service.current_user") as mock_current_user:
        mock_current_user.id = 2
        with patch(
            "services.user.user_service.UserResponse.model_validate",
            return_value=UserResponse.model_validate(
                {
                    "id": 1,
                    "email": fake_user.email,
                    "name": fake_user.name,
                    "username": fake_user.username,
                    "type": UserTypeResponse(id=1, user_type="manager"),
                    "created_by": 2,
                    "updated_by": None,
                }
            ),
        ) as mock_response:
            result = service.get_users()

            assert len(result) == 1
            assert result[0]["id"] == 1
            mock_response.assert_called_once()
            mock_repository.get_all.assert_called_once()


def test_get_user_success(service, fake_user):
    with patch.object(service, "get_user_by_id", return_value=fake_user), patch(
        "services.user.user_service.UserResponse.model_validate",
        return_value=UserResponse.model_validate(
            {
                "id": 1,
                "email": fake_user.email,
                "name": fake_user.name,
                "username": fake_user.username,
                "type": UserTypeResponse(id=1, user_type="manager"),
                "created_by": 2,
                "updated_by": None,
            }
        ),
    ) as mock_response:
        result = service.get_user(1)
        assert result["id"] == 1
        service.get_user_by_id.assert_called_once_with(user_id=1)
        mock_response.assert_called_once()


def test_update_user_success(
    service, mock_repository, fake_user, fake_request
):
    mock_repository.update.return_value = fake_user
    with patch("services.user.user_service.current_user") as mock_current_user:
        mock_current_user.id = 2
        with patch.object(service, "get_user_by_id", return_value=fake_user), patch(
            "services.user.user_service.UserResponse.model_validate",
            return_value=UserResponse.model_validate(
                {
                    "id": 1,
                    "email": fake_user.email,
                    "name": fake_user.name,
                    "username": fake_user.username,
                    "type": UserTypeResponse(id=1, user_type="manager"),
                    "created_by": 1,
                    "updated_by": 2,
                }
            ),
        ) as mock_response:
            result = service.update_user(1, fake_request)
            assert result["id"] == 1
            assert result["updated_by"] == 2
            fake_user.update.assert_called_once_with(fake_request.__dict__)
            mock_repository.update.assert_called_once_with(fake_user)
            mock_response.assert_called_once()


def test_delete_user_success(service, mock_repository, fake_user):
    current_user = Mock(id=99)
    with patch("services.user.user_service.current_user", current_user), patch.object(
        service, "get_user_by_id", return_value=fake_user
    ):
        result = service.delete_user(1)
        assert isinstance(result, Response)
        assert result.status_code == 200
        mock_repository.delete.assert_called_once_with(fake_user)


def test_delete_user_self_delete(service, fake_user):
    current_user = Mock(id=1)
    with patch("services.user.user_service.current_user", current_user), patch.object(
        service, "get_user_by_id", return_value=fake_user
    ):
        with pytest.raises(UnprocessableEntity):
            service.delete_user(1)
