from datetime import datetime, timezone

from sqlalchemy import ForeignKey
from settings.database import db


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    start_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, ForeignKey("project.id"))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, ForeignKey("user.id"))

    project = db.relationship("Project", backref="tasks", lazy="joined")

    def update(self, data: dict[str, str]):
        for key, value in data.items():
            setattr(self, key, value)
