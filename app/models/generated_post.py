from __future__ import annotations

from datetime import datetime, UTC

from app.extensions import db


class GeneratedPost(db.Model):
    __tablename__ = "generated_posts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    tone = db.Column(db.String(128), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    generated_text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=True)

    generate_image_requested = db.Column(db.Boolean, default=False, nullable=False)
    auto_post_vk_requested = db.Column(db.Boolean, default=False, nullable=False)

    vk_publish_status = db.Column(db.String(32), default="not_requested", nullable=False)
    vk_publish_message = db.Column(db.String(255), nullable=True)
    vk_post_id = db.Column(db.BigInteger, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    user = db.relationship("User", back_populates="generated_posts")
