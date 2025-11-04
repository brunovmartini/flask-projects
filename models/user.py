from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import ForeignKey

from settings.database import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), index=True, nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Integer, ForeignKey("user_type.id"))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, ForeignKey("user.id"))
    updated_by = db.Column(db.Integer, ForeignKey("user.id"))

    type = db.relationship("UserType", backref="users", lazy="joined")

    def update(self, data: dict[str, str]):
        allowed_fields = {'email', 'username', 'name', 'user_type'}
        for key, value in data.items():
            if key in allowed_fields:
                setattr(self, key, value)
