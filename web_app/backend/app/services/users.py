from datetime import datetime
from typing import Optional

from app.repositories.database import DatabaseRepository
from app import schemas


class UserService:
    def __init__(self, repository: DatabaseRepository) -> None:
        self.repo = repository

    def ensure_user(self, user_id: str, name: Optional[str] = None,
                    level: Optional[str] = None) -> schemas.UserProfile:
        display_name = name or f"Etudiant {user_id}"
        return self.repo.upsert_user(user_id=user_id, name=display_name, level=level)

    def get_profile(self, user_id: str) -> Optional[schemas.UserProfile]:
        return self.repo.get_user(user_id)

    def build_progress(self, user_id: str) -> schemas.ProgressSnapshot:
        interactions = self.repo.list_interactions(user_id)
        mastered = []
        struggling = []
        scores = {}
        for inter in interactions:
            if inter.probability_after is None:
                continue
            scores.setdefault(inter.skill_id, []).append(inter.probability_after)
        for skill_id, values in scores.items():
            avg = sum(values) / len(values)
            if avg >= 0.75:
                mastered.append(skill_id)
            elif avg <= 0.5:
                struggling.append(skill_id)
        return schemas.ProgressSnapshot(
            user_id=user_id,
            mastered_skills=mastered,
            struggling_skills=struggling,
            last_updated=datetime.utcnow()
        )
