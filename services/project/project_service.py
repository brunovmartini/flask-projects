from datetime import datetime, timezone
from typing import Any

from flask import Response
from flask_login import current_user
from werkzeug.exceptions import NotFound

from helpers.pagination import create_pagination_response
from models.project import Project
from repositories.project_repository import ProjectRepository
from resources.request.project_request import ProjectRequest
from resources.response.project_response import ProjectResponse


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def get_project_by_id(self, project_id: int) -> Project | None:
        project = self.repository.get_by_id(id=project_id)
        if not project:
            raise NotFound(f'Not found project with id={project_id}.')
        return project

    def create_project(self, body: ProjectRequest) -> dict[str, Any] | None:
        project = self.repository.create(
            Project(
                name=body.name,
                subject=body.subject,
                start_date=body.start_date,
                due_date=body.due_date,
                created_at=datetime.now(timezone.utc),
                created_by=current_user.id
            )
        )
        return ProjectResponse.model_validate(project).model_dump()

    def get_projects(self, page: int = 1, page_size: int = 10) -> dict[str, Any]:
        projects, total = self.repository.get_all(page=page, page_size=page_size)

        return create_pagination_response(
            items=[ProjectResponse.model_validate(project).model_dump() for project in projects],
            total=total,
            page=page,
            page_size=page_size
        )

    def get_project(self, project_id: int) -> dict[str, Any] | None:
        project = self.get_project_by_id(project_id=project_id)
        return ProjectResponse.model_validate(project).model_dump()

    def update_project(self, project_id: int, body: ProjectRequest) -> dict[str, Any] | None:
        project = self.get_project_by_id(project_id=project_id)

        project.update(body.model_dump(exclude_unset=True))
        project.updated_at = datetime.now(timezone.utc)
        project.updated_by = current_user.id

        project = self.repository.update(project)
        return ProjectResponse.model_validate(project).model_dump()

    def delete_project(self, project_id: int) -> Response | None:
        project = self.get_project_by_id(project_id=project_id)

        self.repository.delete(project)
        return Response(f'Project with id={project_id} deleted.', status=200)
