from datetime import datetime, timezone

from settings.database import db
from sqlalchemy import ForeignKey


class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255))
    start_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, ForeignKey("user.id"))
    updated_by = db.Column(db.Integer, ForeignKey("user.id"))

    def update(self, data: dict[str, str]):
        allowed_fields = {'name', 'subject', 'start_date', 'due_date'}
        for key, value in data.items():
            if key in allowed_fields:
                setattr(self, key, value)
