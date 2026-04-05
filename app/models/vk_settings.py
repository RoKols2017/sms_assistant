from __future__ import annotations

from datetime import datetime, UTC

from app.extensions import db


class VKSettings(db.Model):
    __tablename__ = "vk_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    vk_api_key = db.Column(db.Text, nullable=False)
    vk_group_id = db.Column(db.BigInteger, nullable=False)

    validation_status = db.Column(db.String(32), default="unknown", nullable=False)
    validation_message = db.Column(db.String(255), nullable=True)
    can_access_group = db.Column(db.Boolean, nullable=True)
    can_post_to_wall = db.Column(db.Boolean, nullable=True)
    can_upload_wall_photo = db.Column(db.Boolean, nullable=True)
    last_validated_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user = db.relationship("User", back_populates="vk_settings")
