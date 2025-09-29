from typing import List, Optional

from app.repositories.database import DatabaseRepository
from app.config import settings
from app import schemas


class ExerciseService:
    def __init__(self, repository: DatabaseRepository) -> None:
        self.repo = repository

    def list_by_filters(self,
                        difficulty: Optional[schemas.Difficulty] = None,
                        skill_id: Optional[str] = None) -> List[schemas.Exercise]:
        return self.repo.list_exercises(difficulty=difficulty, skill_id=skill_id)

    def create(self, data: schemas.ExerciseCreate) -> schemas.Exercise:
        # Allow passing either skill name or external id.
        try:
            return self.repo.add_exercise(data)
        except ValueError as exc:
            raise ValueError(str(exc))

    def get(self, exercise_id: str) -> Optional[schemas.Exercise]:
        return self.repo.get_exercise(exercise_id)

    def initial_set(self) -> List[schemas.Exercise]:
        easy = self.list_by_filters(difficulty=schemas.Difficulty.easy)
        medium = self.list_by_filters(difficulty=schemas.Difficulty.medium)
        hard = self.list_by_filters(difficulty=schemas.Difficulty.hard)
        bundle = (
            easy[: settings.initial_easy_count]
            + medium[: settings.initial_medium_count]
            + hard[: settings.initial_hard_count]
        )
        return bundle
