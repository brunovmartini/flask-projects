from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from models.task import Task
from resources.request.task_request import TaskRequest
from services.task.task_service import TaskService
from werkzeug.exceptions import BadRequest


@pytest.fixture
def task_service(mock_repository):
    return TaskService(repository=mock_repository)


@pytest.fixture
def sample_task():
    return Task(
        id=1,
        name="Test Task",
        description="Sample description",
        start_date="2025-10-29 14:22:11.949",
        due_date="2026-10-29 14:22:11.949",
        project_id=100,
        created_at=datetime.now(timezone.utc),
        created_by=1,
    )


@pytest.fixture
def sample_request():
    return TaskRequest(
        name="Test Task",
        description="Sample description",
        start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
        due_date=datetime(2025, 1, 10, tzinfo=timezone.utc),
    )


def test_create_task_success(
    task_service, mock_repository, sample_request, sample_task
):
    with patch("services.task.task_service.current_user") as mock_current_user:
        mock_current_user.id = 1
        with patch.object(
            mock_repository, "create", return_value=sample_task
        ) as mock_create:

            result = task_service.create_task(project_id=100, body=sample_request)
            assert result == {
                "id": 1,
                "name": "Test Task",
                "description": "Sample description",
                "start_date": datetime(2025, 10, 29, 14, 22, 11, 949000),
                "due_date": datetime(2026, 10, 29, 14, 22, 11, 949000),
                "created_by": 1,
            }

            mock_create.assert_called_once()


def test_get_tasks_by_project_success(task_service, mock_repository, sample_task):
    mock_repository.get_all_tasks_by_project.return_value = [sample_task]

    fake_response = Mock()
    fake_response.model_dump.return_value = {
        "id": sample_task.id,
        "name": sample_task.name,
        "description": sample_task.description,
        "project_id": sample_task.project_id,
        "created_at": sample_task.created_at.isoformat(),
    }

    with patch(
        "services.task.task_service.TaskResponse.model_validate",
        return_value=fake_response,
    ) as mock_from_orm:
        result = task_service.get_tasks_by_project(project_id=100)

        assert len(result) == 1
        assert result[0]["name"] == "Test Task"
        mock_repository.get_all_tasks_by_project.assert_called_once_with(project_id=100)
        mock_from_orm.assert_called_once_with(sample_task)


def test_get_tasks_by_project_empty(task_service, mock_repository):
    mock_repository.get_all_tasks_by_project.return_value = []

    result = task_service.get_tasks_by_project(project_id=999)
    assert result == []
