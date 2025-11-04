from unittest.mock import patch

import pytest
from tests.integration_tests.conftest import login_as


@pytest.fixture
def user_data():
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "name": "New User",
        "password": "Password123!",
        "user_type": 2,
    }


@pytest.fixture
def invalid_request():
    return {
        "password": "plain_password",
        "username": "newuser",
        "name": "New User",
        "user_type": 1
    }


@patch("services.user.user_service.UserService.get_users")
def test_get_users(mock_get_users, client):
    mock_get_users.return_value = [
        {"id": 1, "username": "test1"},
        {"id": 2, "username": "test2"},
    ]
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json[0]["username"] == "test1"


@patch("services.user.user_service.UserService.get_user")
def test_get_user_by_id(mock_get_user, client):
    mock_get_user.return_value = {"id": 123, "username": "testuser"}
    response = client.get("/users/123")
    assert response.status_code == 200
    assert response.json["id"] == 123


@patch("repositories.user_repository.UserRepository.get_by_id")
def test_get_user_by_id_not_found(mock_get_user, client):
    mock_get_user.return_value = None
    response = client.get("/users/9999")
    assert response.status_code == 404


@patch("services.user.user_service.UserService.create_user")
@patch("flask_login.utils._get_user")
def test_create_user_as_manager(
    mock__get_user, mock_create_user, client, user, user_data
):
    login_as(client, user)
    mock__get_user.return_value = user
    mock_create_user.return_value = {
        "id": 555,
        "username": user_data["username"],
        "email": user_data["email"],
        "user_type": user_data["user_type"],
        "name": user_data["name"],
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    assert response.json and response.json["username"] == "newuser"


@patch("services.user.user_service.UserService.create_user")
@patch("flask_login.utils._get_user")
def test_create_user_as_employee_forbidden(
    mock__get_user, mock_create_user, client, user_employee, user_data
):
    login_as(client, user_employee)
    user_employee.role = "employee"
    mock__get_user.return_value = user_employee
    mock_create_user.side_effect = PermissionError("Forbidden")

    response = client.post("/users/", json=user_data)
    assert response.status_code == 403


@patch("services.user.user_service.UserService.update_user")
@patch("flask_login.utils._get_user")
def test_update_user_unauthorized(
    mock__get_user, mock_update_user, client, user_employee, user_data
):
    login_as(client, user_employee)
    mock__get_user.return_value = user_employee
    other_user_id = 999
    mock_update_user.side_effect = PermissionError("Forbidden")

    payload = user_data
    response = client.put(f"/users/{other_user_id}", json=payload)
    assert response.status_code == 403


@patch("repositories.user_repository.UserRepository.get_by_id")
@patch("flask_login.utils._get_user")
def test_update_user_not_found(mock__get_user, mock_get_user, client, user, user_data):
    login_as(client, user)
    mock__get_user.return_value = user
    mock_get_user.return_value = None

    payload = user_data
    response = client.put(f"/users/9999", json=payload)
    assert response.status_code == 404


@patch("services.user.user_service.UserService.delete_user")
@patch("flask_login.utils._get_user")
def test_delete_user_as_manager(mock__get_user, mock_delete_user, client, user):
    login_as(client, user)
    mock__get_user.return_value = user

    response = client.delete("/users/123")
    assert response.status_code == 200


@patch("services.user.user_service.UserService.delete_user")
@patch("flask_login.utils._get_user")
def test_delete_user_as_employee_forbidden(
    mock__get_user, mock_delete_user, client, user_employee
):
    login_as(client, user_employee)
    mock__get_user.return_value = user_employee
    user_employee.role = "employee"
    mock_delete_user.side_effect = PermissionError("Forbidden")

    response = client.delete("/users/1")
    assert response.status_code == 403


@patch("repositories.user_repository.UserRepository.get_by_id")
@patch("flask_login.utils._get_user")
def test_delete_user_not_found(mock__get_user, mock_get_user, client, user):
    login_as(client, user)
    mock__get_user.return_value = user
    mock_get_user.return_value = None

    response = client.delete("/users/9999")
    assert response.status_code == 404


def test_create_user_bad_request(
    client, user, invalid_request
):
    login_as(client, user)

    response = client.post("/users/", json=invalid_request)
    assert response.status_code == 400


def test_update_user_bad_request(
    client, user, invalid_request
):
    login_as(client, user)

    response = client.put("/users/1", json=invalid_request)
    assert response.status_code == 400
