from __future__ import annotations

import json
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app import schemas
from app.models import Exercise, Interaction, Skill, User, UserCredential, AuthToken


class DatabaseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # Users
    def upsert_user(self, user_id: str, name: str, level: Optional[str] = None) -> schemas.UserProfile:
        stmt = select(User).where(User.user_id == user_id)
        user = self.session.execute(stmt).scalar_one_or_none()
        if user:
            if level:
                user.level = level
            if name:
                user.name = name
        else:
            user = User(user_id=user_id, name=name, level=level)
            self.session.add(user)
            self.session.flush()
        return schemas.UserProfile(
            id=str(user.user_id),
            user_id=user.user_id,
            name=user.name,
            level=user.level,
            created_at=user.created_at,
        )

    def get_user(self, user_id: str) -> Optional[schemas.UserProfile]:
        stmt = select(User).where(User.user_id == user_id)
        user = self.session.execute(stmt).scalar_one_or_none()
        if not user:
            return None
        return schemas.UserProfile(
            id=str(user.user_id),
            user_id=user.user_id,
            name=user.name,
            level=user.level,
            created_at=user.created_at,
        )

    def get_user_model(self, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.user_id == user_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_user_account(self, user_id: str, name: str, password_hash: str,
                             level: Optional[str] = None) -> schemas.UserProfile:
        user = self.get_user_model(user_id)
        if user:
            if user.credential:
                raise ValueError("L'utilisateur existe déjà")
            user.name = name
            user.level = level
        else:
            user = User(user_id=user_id, name=name, level=level)
            self.session.add(user)
            self.session.flush()
        credential = UserCredential(user=user, password_hash=password_hash)
        self.session.add(credential)
        self.session.flush()
        return schemas.UserProfile(
            id=str(user.user_id),
            user_id=user.user_id,
            name=user.name,
            level=user.level,
            created_at=user.created_at,
        )

    def get_credentials(self, user_id: str) -> Optional[tuple[User, UserCredential]]:
        stmt = select(User, UserCredential).join(UserCredential).where(User.user_id == user_id)
        result = self.session.execute(stmt).first()
        if not result:
            return None
        return result

    def store_token(self, user: User, token: str) -> str:
        auth_token = AuthToken(user=user, token=token)
        self.session.add(auth_token)
        self.session.flush()
        return token

    def revoke_token(self, token: str) -> None:
        stmt = delete(AuthToken).where(AuthToken.token == token)
        self.session.execute(stmt)

    def get_user_by_token(self, token: str) -> Optional[User]:
        stmt = select(AuthToken).where(AuthToken.token == token)
        auth_token = self.session.execute(stmt).scalar_one_or_none()
        if not auth_token:
            return None
        return auth_token.user

    # Skills
    def list_skills(self) -> List[schemas.Skill]:
        stmt = select(Skill)
        results = self.session.execute(stmt).scalars().all()
        return [
            schemas.Skill(
                id=str(skill.id),
                name=skill.name,
                description=skill.description,
            )
            for skill in results
        ]

    def ensure_skill(self, name: str, external_id: Optional[str] = None) -> Skill:
        stmt = select(Skill).where(Skill.name == name)
        skill = self.session.execute(stmt).scalar_one_or_none()
        if skill:
            if external_id:
                skill.external_id = external_id
            return skill
        skill = Skill(name=name, external_id=external_id)
        self.session.add(skill)
        self.session.flush()
        return skill

    # Exercises
    def list_exercises(self, *, difficulty: Optional[schemas.Difficulty] = None,
                       skill_id: Optional[str] = None) -> List[schemas.Exercise]:
        stmt = select(Exercise).order_by(Exercise.id)
        if difficulty:
            stmt = stmt.where(Exercise.difficulty == difficulty)
        if skill_id:
            stmt = stmt.join(Skill)
            if skill_id.isdigit():
                stmt = stmt.where((Skill.external_id == skill_id) | (Skill.id == int(skill_id)))
            else:
                stmt = stmt.where(Skill.name == skill_id)
        results = self.session.execute(stmt).scalars().all()
        return [self._to_exercise_schema(ex) for ex in results]

    def add_exercise(self, data: schemas.ExerciseCreate) -> schemas.Exercise:
        skill = None
        if data.skill_id:
            skill_stmt = select(Skill).where(Skill.name == data.skill_id)
            skill = self.session.execute(skill_stmt).scalar_one_or_none()
        if not skill and data.skill_external_id:
            skill_stmt = select(Skill).where(Skill.external_id == data.skill_external_id)
            skill = self.session.execute(skill_stmt).scalar_one_or_none()
        if not skill:
            # Create the skill lazily if it does not exist
            skill = Skill(
                name=data.skill_id,
                external_id=data.skill_external_id or (data.skill_id if data.skill_id.isdigit() else None),
            )
            self.session.add(skill)
            self.session.flush()
        exercise_identifier = data.exercise_id or f"ex_{skill.id}_{len(skill.exercises) + 1}"

        exercise = Exercise(
            exercise_id=exercise_identifier,
            skill=skill,
            prompt=data.prompt,
            difficulty=data.difficulty,
            options=json.dumps(data.options) if data.options else None,
            answer=data.answer or "",
            solution=data.solution,
        )
        self.session.add(exercise)
        self.session.flush()
        return self._to_exercise_schema(exercise)

    def get_exercise(self, exercise_id: str) -> Optional[schemas.Exercise]:
        stmt = select(Exercise).where(Exercise.exercise_id == exercise_id)
        exercise = self.session.execute(stmt).scalar_one_or_none()
        if not exercise:
            return None
        return self._to_exercise_schema(exercise)

    # Interactions
    def add_interaction(
        self,
        payload: schemas.InteractionCreate,
        probability_before: Optional[float],
        probability_after: Optional[float],
    ) -> schemas.Interaction:
        user_stmt = select(User).where(User.user_id == payload.user_id)
        user = self.session.execute(user_stmt).scalar_one_or_none()
        if not user:
            raise ValueError("Utilisateur inconnu")

        ex_stmt = select(Exercise).where(Exercise.exercise_id == payload.exercise_id)
        exercise = self.session.execute(ex_stmt).scalar_one_or_none()
        if not exercise:
            raise ValueError("Exercice introuvable")

        interaction = Interaction(
            user=user,
            exercise=exercise,
            correct=payload.correct,
            probability_before=probability_before,
            probability_after=probability_after,
            timestamp=payload.timestamp,
        )
        self.session.add(interaction)
        self.session.flush()
        return schemas.Interaction(
            id=str(interaction.id),
            user_id=user.user_id,
            exercise_id=exercise.exercise_id,
            skill_id=exercise.skill.name,
            correct=interaction.correct,
            timestamp=interaction.timestamp,
            probability_before=probability_before,
            probability_after=probability_after,
        )

    def list_interactions(self, user_id: str) -> List[schemas.Interaction]:
        user_stmt = select(User).where(User.user_id == user_id)
        user = self.session.execute(user_stmt).scalar_one_or_none()
        if not user:
            return []
        stmt = (
            select(Interaction)
            .where(Interaction.user_id == user.id)
            .order_by(Interaction.timestamp)
        )
        interactions = self.session.execute(stmt).scalars().all()
        results = []
        for inter in interactions:
            results.append(
                schemas.Interaction(
                    id=str(inter.id),
                    user_id=user.user_id,
                    exercise_id=inter.exercise.exercise_id,
                    skill_id=inter.exercise.skill.name,
                    correct=inter.correct,
                    timestamp=inter.timestamp,
                    probability_before=inter.probability_before,
                    probability_after=inter.probability_after,
                )
            )
        return results

    # Helpers
    @staticmethod
    def _to_exercise_schema(exercise: Exercise) -> schemas.Exercise:
        options = json.loads(exercise.options) if exercise.options else None
        return schemas.Exercise(
            id=exercise.exercise_id,
            skill_id=exercise.skill.name,
            skill_external_id=exercise.skill.external_id,
            prompt=exercise.prompt,
            difficulty=exercise.difficulty,
            options=options,
            answer=exercise.answer,
            solution=exercise.solution,
        )
