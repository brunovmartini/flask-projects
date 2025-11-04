from sqlalchemy.orm import Session, joinedload
from typing_extensions import override

from models.user import User
from repositories.i_repository import IRepository


class UserRepository(IRepository[User, int]):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_by_email(self, email: str) -> User | None:
        return self.db_session.query(User).options(joinedload(User.type)).filter(User.email == email).first()

    @override
    def create(self, data: User) -> User:
        self.db_session.add(data)
        self.db_session.commit()
        self.db_session.refresh(data)
        return data

    def get_all(self, page: int = 1, page_size: int = 10) -> tuple[list[User], int]:
        query = self.db_session.query(User)
        total = query.count()
        offset = (page - 1) * page_size
        users = query.offset(offset).limit(page_size).all()
        return users, total

    @override
    def get_by_id(self, id: int) -> User | None:
        return self.db_session.query(User).options(joinedload(User.type)).filter(User.id == id).first()

    @override
    def update(self, data: User) -> User | None:
        self.db_session.commit()
        self.db_session.refresh(data)
        return data

    @override
    def delete(self, data: User) -> None:
        self.db_session.delete(data)
        self.db_session.commit()
