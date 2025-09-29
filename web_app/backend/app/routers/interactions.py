from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.dependencies import (
    get_current_user,
    get_interaction_service,
)

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/", response_model=schemas.Interaction)
def record_interaction(
    payload: schemas.InteractionCreate,
    interaction_service=Depends(get_interaction_service),
    current_user: schemas.UserProfile = Depends(get_current_user),
):
    payload = payload.model_copy(update={"user_id": current_user.user_id})
    try:
        return interaction_service.record(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
