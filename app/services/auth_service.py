from __future__ import annotations

import logging

from app.extensions import bcrypt, db
from app.models.user import User


logger = logging.getLogger(__name__)


class AuthService:
    def register_user(self, email: str, password: str) -> User:
        normalized_email = email.strip().lower()
        logger.info("[AuthService.register_user] start extra=%s", {"email": normalized_email})

        existing_user = User.query.filter_by(email=normalized_email).first()
        if existing_user:
            logger.warning(
                "[AuthService.register_user] duplicate email extra=%s",
                {"email": normalized_email},
            )
            raise ValueError("Пользователь с таким email уже существует.")

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(email=normalized_email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()

        logger.info(
            "[AuthService.register_user] completed extra=%s",
            {"user_id": user.id, "email": normalized_email},
        )
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        normalized_email = email.strip().lower()
        logger.info("[AuthService.authenticate] start extra=%s", {"email": normalized_email})

        user = User.query.filter_by(email=normalized_email).first()
        if user is None:
            logger.warning(
                "[AuthService.authenticate] user not found extra=%s",
                {"email": normalized_email},
            )
            return None

        if not bcrypt.check_password_hash(user.password_hash, password):
            logger.warning(
                "[AuthService.authenticate] invalid password extra=%s",
                {"user_id": user.id},
            )
            return None

        logger.info(
            "[AuthService.authenticate] completed extra=%s",
            {"user_id": user.id},
        )
        return user
