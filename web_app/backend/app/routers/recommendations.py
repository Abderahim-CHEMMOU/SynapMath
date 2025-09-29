from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.dependencies import get_current_user, get_recommendation_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/next", response_model=schemas.RecommendationResponse)
def next_exercise(
    user_id: str | None = None,
    service=Depends(get_recommendation_service),
    current_user: schemas.UserProfile = Depends(get_current_user),
):
    target_user = user_id or current_user.user_id
    if user_id and user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    recommendation = service.recommend_next(target_user)
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Aucune recommandation disponible")
    return recommendation
