from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from app import schemas


@dataclass
class MemoryRepository:
    users: Dict[str, schemas.UserProfile] = field(default_factory=dict)
    skills: Dict[str, schemas.Skill] = field(default_factory=dict)
    exercises: Dict[str, schemas.Exercise] = field(default_factory=dict)
    interactions: Dict[str, schemas.Interaction] = field(default_factory=dict)

    def seed_defaults(self) -> None:
        if self.skills:
            return
        algebra1 = schemas.Skill(id="algebra1", name="Algebra 1")
        algebra2 = schemas.Skill(id="algebra2", name="Algebra 2")
        self.skills = {algebra1.id: algebra1, algebra2.id: algebra2}

        defaults = [
            schemas.Exercise(
                id="alg1_easy_1",
                skill_id=algebra1.id,
                prompt="Resoudre 2x + 3 = 9",
                difficulty=schemas.Difficulty.easy,
                solution="x = 3"
            ),
            schemas.Exercise(
                id="alg1_easy_2",
                skill_id=algebra1.id,
                prompt="Calculer 5 - 2",
                difficulty=schemas.Difficulty.easy,
                solution="3"
            ),
            schemas.Exercise(
                id="alg2_medium_1",
                skill_id=algebra2.id,
                prompt="Resoudre x^2 - 5x + 6 = 0",
                difficulty=schemas.Difficulty.medium,
                solution="x = 2 ou x = 3"
            ),
            schemas.Exercise(
                id="alg2_medium_2",
                skill_id=algebra2.id,
                prompt="Factoriser x^2 - 9",
                difficulty=schemas.Difficulty.medium,
                solution="(x - 3)(x + 3)"
            ),
            schemas.Exercise(
                id="alg2_hard_1",
                skill_id=algebra2.id,
                prompt="Resoudre x^2 + x - 12 = 0",
                difficulty=schemas.Difficulty.hard,
                solution="x = 3 ou x = -4"
            ),
        ]
        self.exercises = {ex.id: ex for ex in defaults}

    def upsert_user(self, user_id: str, name: str, level: Optional[str] = None) -> schemas.UserProfile:
        existing = self.users.get(user_id)
        if existing:
            if level:
                existing.level = level
            if name:
                existing.name = name
            return existing
        profile = schemas.UserProfile(
            id=user_id,
            name=name,
            level=level,
            created_at=datetime.utcnow()
        )
        self.users[user_id] = profile
        return profile

    def get_user(self, user_id: str) -> Optional[schemas.UserProfile]:
        return self.users.get(user_id)

    def list_skills(self) -> List[schemas.Skill]:
        return list(self.skills.values())

    def list_exercises(self, *, difficulty: Optional[schemas.Difficulty] = None,
                       skill_id: Optional[str] = None) -> List[schemas.Exercise]:
        values = self.exercises.values()
        if difficulty:
            values = [ex for ex in values if ex.difficulty == difficulty]
        if skill_id:
            values = [ex for ex in values if ex.skill_id == skill_id]
        return list(values)

    def add_exercise(self, data: schemas.ExerciseCreate) -> schemas.Exercise:
        ex_id = f"ex_{uuid.uuid4().hex[:8]}"
        exercise = schemas.Exercise(id=ex_id, **data.dict())
        self.exercises[exercise.id] = exercise
        return exercise

    def get_exercise(self, exercise_id: str) -> Optional[schemas.Exercise]:
        return self.exercises.get(exercise_id)

    def add_interaction(self, payload: schemas.InteractionCreate,
                        probability_before: Optional[float],
                        probability_after: Optional[float]) -> schemas.Interaction:
        inter_id = f"it_{uuid.uuid4().hex[:8]}"
        timestamp = payload.timestamp or datetime.utcnow()
        interaction = schemas.Interaction(
            id=inter_id,
            user_id=payload.user_id,
            exercise_id=payload.exercise_id,
            skill_id=payload.skill_id,
            correct=payload.correct,
            timestamp=timestamp,
            probability_before=probability_before,
            probability_after=probability_after
        )
        self.interactions[interaction.id] = interaction
        return interaction

    def list_interactions(self, user_id: str) -> List[schemas.Interaction]:
        return [i for i in self.interactions.values() if i.user_id == user_id]
