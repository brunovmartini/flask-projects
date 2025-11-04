from sqlalchemy.orm import Session
from typing_extensions import override

from models.project import Project
from repositories.i_repository import IRepository


class ProjectRepository(IRepository[Project, int]):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @override
    def create(self, data: Project) -> Project:
        self.db_session.add(data)
        self.db_session.commit()
        self.db_session.refresh(data)
        return data

    def get_all(self, page: int = 1, page_size: int = 10) -> tuple[list[Project], int]:
        query = self.db_session.query(Project)
        total = query.count()
        offset = (page - 1) * page_size
        projects = query.offset(offset).limit(page_size).all()
        return projects, total

    @override
    def get_by_id(self, id: int) -> Project | None:
        return self.db_session.query(Project).filter(Project.id == id).first()

    @override
    def update(self, data: Project) -> Project | None:
        self.db_session.commit()
        self.db_session.refresh(data)
        return data

    @override
    def delete(self, data: Project) -> None:
        self.db_session.delete(data)
        self.db_session.commit()
