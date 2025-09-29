from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.dependencies import get_exercise_service

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/", response_model=List[schemas.Exercise])
def list_exercises(difficulty: Optional[schemas.Difficulty] = None,
                   skill_id: Optional[str] = None,
                   exercise_service=Depends(get_exercise_service)):
    return exercise_service.list_by_filters(difficulty=difficulty, skill_id=skill_id)


@router.post("/", response_model=schemas.Exercise)
def create_exercise(payload: schemas.ExerciseCreate,
                    exercise_service=Depends(get_exercise_service)):
    try:
        return exercise_service.create(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/initial", response_model=List[schemas.Exercise])
def initial_bundle(exercise_service=Depends(get_exercise_service)):
    return exercise_service.initial_set()
