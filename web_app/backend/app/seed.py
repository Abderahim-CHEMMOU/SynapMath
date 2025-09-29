from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Exercise, Skill
from app.schemas import Difficulty


def load_exercise_seed(path: Path | None = None) -> Iterable[dict]:
    target = path or settings.exercises_seed_path
    if not target.exists():
        return []
    with open(target, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    if isinstance(data, dict):
        data = [data]
    return data


def seed_skills_and_exercises(session: Session) -> None:
    existing = session.execute(select(Skill)).scalars().first()
    if existing:
        return

    for record in load_exercise_seed():
        skill_name = record.get("skill_name")
        external_id = record.get("skill_id")
        skill = session.execute(select(Skill).where(Skill.name == skill_name)).scalar_one_or_none()
        if not skill:
            skill = Skill(name=skill_name, external_id=str(external_id) if external_id is not None else None)
            session.add(skill)
            session.flush()
        options = record.get("options")
        difficulty_value = record.get("difficulty", Difficulty.easy)
        if isinstance(difficulty_value, str):
            difficulty_value = Difficulty(difficulty_value)

        existing_ex = session.execute(
            select(Exercise).where(Exercise.exercise_id == record.get("exercise_id"))
        ).scalar_one_or_none()
        if existing_ex:
            continue

        exercise = Exercise(
            exercise_id=record.get("exercise_id"),
            skill=skill,
            prompt=record.get("prompt", ""),
            difficulty=difficulty_value,
            options=json.dumps(options) if options else None,
            answer=record.get("answer", ""),
            solution=record.get("solution"),
        )
        session.add(exercise)
    session.commit()
