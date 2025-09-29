from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.dependencies import (
    get_current_user,
    get_interaction_service,
    get_user_service,
)

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/{user_id}/profile", response_model=schemas.UserProfile)
def get_profile(
    user_id: str,
    current_user: schemas.UserProfile = Depends(get_current_user),
    user_service=Depends(get_user_service)
):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    profile = user_service.get_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Utilisateur inconnu")
    return profile


@router.get("/{user_id}/progress", response_model=schemas.ProgressSnapshot)
def get_progress(
    user_id: str,
    current_user: schemas.UserProfile = Depends(get_current_user),
    user_service=Depends(get_user_service)
):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    profile = user_service.get_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Utilisateur inconnu")
    return user_service.build_progress(user_id)


@router.get("/{user_id}/history", response_model=List[schemas.Interaction])
def get_history(
    user_id: str,
    current_user: schemas.UserProfile = Depends(get_current_user),
    interaction_service=Depends(get_interaction_service)
):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return interaction_service.list_for_user(user_id)
