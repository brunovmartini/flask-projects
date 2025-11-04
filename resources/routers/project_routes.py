from flask import Blueprint, current_app, request
from flask_login import login_required
from flask_pydantic import validate
from werkzeug.exceptions import NotFound

from decorators.decorators import manager_required
from helpers.pagination import validate_pagination
from repositories.project_repository import ProjectRepository
from repositories.task_repository import TaskRepository
from resources.request.project_request import ProjectRequest
from resources.request.task_request import TaskRequest
from services.project.project_service import ProjectService
from services.task.task_service import TaskService
from settings.database import db

project_apis = Blueprint('project_apis', __name__)


@project_apis.route('/', methods=['POST'])
@validate()
@manager_required
def create_project(body: ProjectRequest):
    """
    Create a new project. Only accessible by managers.

    :param body: ProjectRequest object containing project details
    :type body: ProjectRequest
    :return: JSON representation of the created project
    :rtype: dict
    :raises BadRequest: if request body is invalid
    """
    current_app.logger.info(f"Create project: name={body.name}")
    return ProjectService(repository=ProjectRepository(db_session=db.session)).create_project(body=body)


@project_apis.route('/', methods=['GET'])
@login_required
def get_projects():
    page, page_size = validate_pagination(request.args)
    return ProjectService(repository=ProjectRepository(db_session=db.session)).get_projects(page=page,
                                                                                            page_size=page_size)


@project_apis.route('/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id: int):
    """
    Retrieve a single project by ID.

    :param project_id: ID of the project
    :type project_id: int
    :return: Project details in JSON format
    :rtype: dict
    :raises NotFound: if project with given ID does not exist
    """
    return ProjectService(repository=ProjectRepository(db_session=db.session)).get_project(project_id=project_id)


@project_apis.route('/<int:project_id>', methods=['PUT'])
@validate()
@manager_required
def update_project(project_id: int, body: ProjectRequest):
    """
    Update an existing project. Only accessible by managers.

    :param project_id: ID of the project to update
    :type project_id: int
    :param body: ProjectRequest object with updated project data
    :type body: ProjectRequest
    :return: Updated project details in JSON format
    :rtype: dict
    :raises NotFound: if project with given ID does not exist
    :raises BadRequest: if request body is invalid
    """
    current_app.logger.info(f"Update project: project_id={project_id}")
    return ProjectService(
        repository=ProjectRepository(db_session=db.session)
    ).update_project(project_id=project_id, body=body)


@project_apis.route('/<int:project_id>', methods=['DELETE'])
@manager_required
def delete_project(project_id: int):
    """
    Delete a project by ID. Only accessible by managers.

    :param project_id: ID of the project to delete
    :type project_id: int
    :return: Response with deletion confirmation
    :rtype: flask.Response
    :raises NotFound: if project with given ID does not exist
    """
    current_app.logger.info(f"Delete project: project_id={project_id}")
    return ProjectService(repository=ProjectRepository(db_session=db.session)).delete_project(project_id=project_id)


@project_apis.route('/<int:project_id>/tasks', methods=['POST'])
@validate()
@manager_required
def create_task(project_id: int, body: TaskRequest):
    """
    Create a new task under a project. Only accessible by managers.

    :param project_id: ID of the parent project
    :type project_id: int
    :param body: TaskRequest object with task details
    :type body: TaskRequest
    :return: JSON representation of the created task
    :rtype: dict
    :raises NotFound: if parent project does not exist
    :raises BadRequest: if request body is invalid
    """
    if not ProjectService(repository=ProjectRepository(db_session=db.session)).get_project(project_id=project_id):
        raise NotFound(f'Not found project with id={project_id}.')
    current_app.logger.info(f"Create task: name={body.name}, project_id={project_id}")
    return TaskService(repository=TaskRepository(db_session=db.session)).create_task(project_id=project_id, body=body)


@project_apis.route('/<int:project_id>/tasks', methods=['GET'])
@login_required
def get_tasks_by_project(project_id: int):
    if not ProjectService(repository=ProjectRepository(db_session=db.session)).get_project(project_id=project_id):
        raise NotFound(f'Not found project with id={project_id}.')

    page, page_size = validate_pagination(request.args)
    return TaskService(repository=TaskRepository(db_session=db.session)).get_tasks_by_project(
        project_id=project_id, page=page, page_size=page_size
    )
