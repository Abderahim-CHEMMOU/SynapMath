from __future__ import annotations

import secrets
from typing import Optional

from passlib.context import CryptContext

from app import schemas
from app.repositories.database import DatabaseRepository
from app.models import User


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _user_to_profile(user: User) -> schemas.UserProfile:
    return schemas.UserProfile(
        id=str(user.user_id),
        user_id=user.user_id,
        name=user.name,
        level=user.level,
        created_at=user.created_at,
    )


class AuthService:
    def __init__(self, repo: DatabaseRepository) -> None:
        self.repo = repo

    def register(self, payload: schemas.RegisterRequest) -> schemas.UserProfile:
        password_hash = pwd_context.hash(payload.password)
        return self.repo.create_user_account(
            user_id=payload.user_id,
            name=payload.name,
            password_hash=password_hash,
            level=payload.level,
        )

    def login(self, payload: schemas.LoginRequest) -> str:
        credentials = self.repo.get_credentials(payload.user_id)
        if not credentials:
            raise ValueError("Identifiants invalides")
        user, cred = credentials
        if not pwd_context.verify(payload.password, cred.password_hash):
            raise ValueError("Identifiants invalides")
        token = secrets.token_urlsafe(32)
        self.repo.store_token(user, token)
        return token

    def logout(self, token: str) -> None:
        self.repo.revoke_token(token)

    def resolve_user(self, token: str) -> Optional[schemas.UserProfile]:
        user = self.repo.get_user_by_token(token)
        if not user:
            return None
        return _user_to_profile(user)

    def ensure_user_exists(self, user_id: str) -> Optional[schemas.UserProfile]:
        user = self.repo.get_user_model(user_id)
        if not user:
            return None
        return _user_to_profile(user)
