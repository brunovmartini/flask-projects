from datetime import datetime, timezone
from typing import Any

from flask_login import current_user

from helpers.pagination import create_pagination_response
from models.task import Task
from repositories.task_repository import TaskRepository
from resources.request.task_request import TaskRequest
from resources.response.task_response import TaskResponse


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, project_id: int, body: TaskRequest) -> dict[str, Any] | None:
        task = self.repository.create(
            Task(
                name=body.name,
                description=body.description,
                start_date=body.start_date,
                due_date=body.due_date,
                project_id=project_id,
                created_at=datetime.now(timezone.utc),
                created_by=current_user.id
            )
        )
        return TaskResponse.model_validate(task).model_dump()

    def get_tasks_by_project(self, project_id: int, page: int = 1, page_size: int = 10) -> dict[str, Any]:
        tasks, total = self.repository.get_all_tasks_by_project(project_id=project_id, page=page, page_size=page_size)

        return create_pagination_response(
            items=[TaskResponse.model_validate(task).model_dump() for task in tasks],
            total=total,
            page=page,
            page_size=page_size
        )
