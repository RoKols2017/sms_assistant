"""initial schema

Revision ID: 20260405_0001
Revises:
Create Date: 2026-04-05 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260405_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "generated_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tone", sa.String(length=128), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("generated_text", sa.Text(), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("generate_image_requested", sa.Boolean(), nullable=False),
        sa.Column("auto_post_vk_requested", sa.Boolean(), nullable=False),
        sa.Column("vk_publish_status", sa.String(length=32), nullable=False),
        sa.Column("vk_publish_message", sa.String(length=255), nullable=True),
        sa.Column("vk_post_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_generated_posts_user_id"), "generated_posts", ["user_id"], unique=False)

    op.create_table(
        "vk_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("vk_api_key", sa.Text(), nullable=False),
        sa.Column("vk_group_id", sa.BigInteger(), nullable=False),
        sa.Column("validation_status", sa.String(length=32), nullable=False),
        sa.Column("validation_message", sa.String(length=255), nullable=True),
        sa.Column("can_access_group", sa.Boolean(), nullable=True),
        sa.Column("can_post_to_wall", sa.Boolean(), nullable=True),
        sa.Column("can_upload_wall_photo", sa.Boolean(), nullable=True),
        sa.Column("last_validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade():
    op.drop_table("vk_settings")
    op.drop_index(op.f("ix_generated_posts_user_id"), table_name="generated_posts")
    op.drop_table("generated_posts")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
