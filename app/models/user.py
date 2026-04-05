from __future__ import annotations

from datetime import datetime, UTC

from flask_login import UserMixin

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    vk_settings = db.relationship(
        "VKSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    generated_posts = db.relationship(
        "GeneratedPost",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    if not user_id:
        return None
    return db.session.get(User, int(user_id))
