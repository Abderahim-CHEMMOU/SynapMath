from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.repositories.database import DatabaseRepository
from app.services.dkt import dkt_service, DKTService
from app.services.exercises import ExerciseService
from app.services.interactions import InteractionService
from app.services.recommendation import RecommendationService
from app.services.users import UserService
from app.services.auth import AuthService
from app import schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_repository(db: Session = Depends(get_db)) -> DatabaseRepository:
    return DatabaseRepository(db)


def get_dkt_service() -> DKTService:
    return dkt_service


def get_user_service(repo: DatabaseRepository = Depends(get_repository)) -> UserService:
    return UserService(repo)


def get_exercise_service(repo: DatabaseRepository = Depends(get_repository)) -> ExerciseService:
    return ExerciseService(repo)


def get_interaction_service(
    repo: DatabaseRepository = Depends(get_repository),
    dkt: DKTService = Depends(get_dkt_service),
) -> InteractionService:
    return InteractionService(repo, dkt)


def get_recommendation_service(
    repo: DatabaseRepository = Depends(get_repository),
    dkt: DKTService = Depends(get_dkt_service),
    exercises: ExerciseService = Depends(get_exercise_service),
) -> RecommendationService:
    return RecommendationService(repo, dkt, exercises)


def get_auth_service(repo: DatabaseRepository = Depends(get_repository)) -> AuthService:
    return AuthService(repo)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> schemas.UserProfile:
    profile = auth_service.resolve_user(token)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return profile
