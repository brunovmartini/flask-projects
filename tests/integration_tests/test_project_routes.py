from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from flask import Response
from models.project import Project
from models.task import Task
from tests.integration_tests.conftest import login_as
from resources.request.project_request import ProjectRequest


@pytest.fixture
def project():
    project = Project(
        name="Test Project",
        subject="Test Subject",
        start_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=10),
        created_at=datetime.now(),
        created_by=1,
    )
    return project


@pytest.fixture
def task(project):
    task = Task(
        name="Existing Task",
        description="Task description",
        start_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=2),
        project_id=project.id,
        created_at=datetime.now(),
        created_by=1,
    )
    return task


@pytest.fixture
def project_request():
    return {
        "name": "New Project",
        "subject": "Testing",
        "start_date": "2025-10-30T00:00:00Z",
        "due_date": "2025-11-05T00:00:00Z",
    }


@pytest.fixture
def invalid_request():
    return {
        "subject": "New Subject",
        "start_date": "2025-10-29 14:22:11.949",
        "due_date": "2026-10-29 14:22:11.949"
    }


@pytest.fixture
def task_request():
    return {
        "name": "Task 1",
        "description": "Task description",
        "start_date": "2025-10-30T00:00:00Z",
        "due_date": "2025-11-02T00:00:00Z",
    }


@patch("services.project.project_service.ProjectService.create_project")
@patch("flask_login.utils._get_user")
def test_create_project_as_manager(mock__get_user, mock_create_project, client, user, project_request):
    login_as(client, user)
    mock__get_user.return_value = user

    mock_create_project.return_value = {
        "id": 1,
        "name": "New Project",
        "subject": "Testing",
        "start_date": "2025-10-30T00:00:00Z",
        "due_date": "2025-11-05T00:00:00Z",
    }

    response = client.post("/projects/", json=project_request)

    assert response.status_code == 200
    assert "name" in response.json
    assert response.json["name"] == "New Project"


@patch("services.project.project_service.ProjectService.create_project")
@patch("flask_login.utils._get_user")
def test_create_project_as_employee_forbidden(
    mock__get_user, mock_create_project, client, user_employee, project_request
):
    login_as(client, user_employee)
    mock__get_user.return_value = user_employee

    mock_create_project.side_effect = PermissionError("Forbidden")
    response = client.post("/projects/", json=project_request)
    assert response.status_code == 403


@patch("services.project.project_service.ProjectService.get_projects")
def test_get_projects(mock_get_all_projects, client):
    mock_get_all_projects.return_value = [
        {"id": 1, "name": "Test Project", "subject": "X"}
    ]
    response = client.get("/projects/")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0


@patch("services.project.project_service.ProjectService.get_project")
def test_get_project_by_id(mock_get_project_by_id, client):
    mock_get_project_by_id.return_value = {
        "id": 123,
        "name": "Project X",
        "subject": "Testing",
    }
    response = client.get("/projects/123")
    assert response.status_code == 200
    assert response.json["id"] == 123


@patch("repositories.project_repository.ProjectRepository.get_by_id")
def test_get_project_not_found(mock_get_project_by_id_repo, client):
    mock_get_project_by_id_repo.return_value = None
    response = client.get("/projects/9999")
    assert response.status_code == 404


@patch("services.project.project_service.ProjectService.update_project")
@patch("flask_login.utils._get_user")
def test_update_project_as_manager(mock__get_user, mock_update_project, client, user, project_request):
    login_as(client, user)
    mock__get_user.return_value = user
    mock_update_project.return_value = {
        "id": 1,
        "name": "Project",
        "subject": "Subject",
        "start_date": "2025-10-30T00:00:00Z",
        "due_date": "2025-11-10T00:00:00Z",
    }

    response = client.put("/projects/1", json=project_request)
    assert response.status_code == 200
    assert response.json["name"] == "Project"


@patch("repositories.project_repository.ProjectRepository.get_by_id")
@patch("flask_login.utils._get_user")
def test_update_project_not_found(mock__get_user, mock_update_project, client, user, project_request):
    login_as(client, user)
    mock__get_user.return_value = user
    mock_update_project.return_value = None

    response = client.put("/projects/9999", json=project_request)
    assert response.status_code == 404


@patch("services.project.project_service.ProjectService.delete_project")
@patch("flask_login.utils._get_user")
def test_delete_project_as_manager(mock__get_user, mock_delete_project, client, user):
    login_as(client, user)
    mock__get_user.return_value = user
    mock_delete_project.return_value = Response(f"Project deleted.", status=200)

    response = client.delete("/projects/1")
    assert response.status_code == 200


@patch("resources.routers.project_routes.delete_project")
@patch("flask_login.utils._get_user")
def test_delete_project_as_employee_forbidden(
    mock__get_user, mock_delete_project, client, user_employee
):
    login_as(client, user_employee)
    mock__get_user.return_value = user_employee
    mock_delete_project.side_effect = PermissionError("Forbidden")

    response = client.delete("/projects/1")
    assert response.status_code == 403


@patch("repositories.project_repository.ProjectRepository.get_by_id")
@patch("services.task.task_service.TaskService.create_task")
@patch("flask_login.utils._get_user")
def test_create_task_for_project(
    mock__get_user, mock_create_task, mock_get_project, client, user, project, task_request
):
    login_as(client, user)
    mock_get_project.return_value = project
    mock__get_user.return_value = user
    mock_create_task.return_value = {
        "id": 1,
        "name": "Task 1",
        "description": "Task description",
        "start_date": "2025-10-30T00:00:00Z",
        "due_date": "2025-11-02T00:00:00Z",
    }

    response = client.post("/projects/1/tasks", json=task_request)
    assert response.status_code == 200
    assert response.json["name"] == "Task 1"


@patch("repositories.project_repository.ProjectRepository.get_by_id")
@patch("flask_login.utils._get_user")
def test_create_task_for_nonexistent_project(
    mock__get_user, mock_create_task, client, user, task_request
):
    login_as(client, user)
    mock__get_user.return_value = user
    mock_create_task.return_value = None

    response = client.post("/projects/9999/tasks", json=task_request)
    assert response.status_code == 404


@patch("services.project.project_service.ProjectService.get_project_by_id")
@patch("services.task.task_service.TaskService.get_tasks_by_project")
def test_get_tasks_by_project(
    mock_get_tasks_by_project_id, mock_get_project_by_id, client, project
):
    mock_get_project_by_id.return_value = project
    mock_get_tasks_by_project_id.return_value = [{"id": 1, "name": "Task 1"}]
    response = client.get("/projects/1/tasks")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0


@patch("services.project.project_service.ProjectService.get_project")
@patch("services.task.task_service.TaskService.get_tasks_by_project")
def test_get_tasks_for_nonexistent_project(
    mock_get_tasks_by_project_id, mock_get_project_by_id, client
):
    mock_get_project_by_id.return_value = None
    mock_get_tasks_by_project_id.return_value = []
    response = client.get("/projects/9999/tasks")
    assert response.status_code == 404


def test_create_project_bad_request(
    client, user, invalid_request
):
    login_as(client, user)

    response = client.post("/projects/", json=invalid_request)
    assert response.status_code == 400


def test_update_project_bad_request(
    client, user, invalid_request
):
    login_as(client, user)

    response = client.put("/projects/1", json=invalid_request)
    assert response.status_code == 400


def test_create_task_bad_request(
    client, user
):
    login_as(client, user)

    payload = {
        "description": "Task description",
        "start_date": "2025-10-30T00:00:00Z",
        "due_date": "2025-11-02T00:00:00Z",
    }

    response = client.post("/projects/1/tasks", json=payload)
    assert response.status_code == 400
