from __future__ import annotations

from typing import Dict, List, Optional

from app.repositories.database import DatabaseRepository
from app.services.dkt import DKTService
from app.services.exercises import ExerciseService
from app import schemas


class RecommendationService:
    def __init__(self,
                 repository: DatabaseRepository,
                 dkt: DKTService,
                 exercises: ExerciseService) -> None:
        self.repo = repository
        self.dkt = dkt
        self.exercises = exercises

    MASTERY_THRESHOLD = 0.71

    def _history_sequences(self, user_id: str) -> tuple[list[int], list[int]]:
        interactions = sorted(
            self.repo.list_interactions(user_id),
            key=lambda x: x.timestamp
        )
        skills: list[int] = []
        responses: list[int] = []
        for inter in interactions:
            idx = self.dkt.skill_to_idx(inter.skill_id)
            if idx is None:
                continue
            skills.append(idx)
            responses.append(int(inter.correct))
        return skills, responses

    def _not_attempted(self, user_id: str) -> set[str]:
        return {inter.exercise_id for inter in self.repo.list_interactions(user_id)}

    def initial_bundle(self) -> List[schemas.Exercise]:
        return self.exercises.initial_set()

    @staticmethod
    def _skill_history(history: List[schemas.Interaction], skill_id: str) -> List[schemas.Interaction]:
        return [inter for inter in history if inter.skill_id == skill_id]

    @classmethod
    def _is_skill_mastered(cls, history: List[schemas.Interaction], probability: float) -> bool:
        if not history:
            return False
        if probability <= cls.MASTERY_THRESHOLD:
            return False
        latest_per_exercise: Dict[str, bool] = {}
        for inter in history:
            latest_per_exercise[inter.exercise_id] = inter.correct
        return all(latest_per_exercise.values())

    @staticmethod
    def _blocked_exercises(history: List[schemas.Interaction]) -> set[str]:
        blocked: set[str] = set()
        if not history:
            return blocked
        # Track unique other exercises answered correctly since last failure
        correct_since_failure: Dict[str, set[str]] = {}
        for inter in history:
            ex_id = inter.exercise_id
            if inter.correct:
                for blocked_ex, successes in list(correct_since_failure.items()):
                    if blocked_ex != ex_id:
                        successes.add(ex_id)
                    if len(successes) >= 3:
                        correct_since_failure.pop(blocked_ex)
                        blocked.discard(blocked_ex)
            else:
                correct_since_failure[ex_id] = set()
                blocked.add(ex_id)
        return blocked

    def _difficulty_from_prob(self, probability: float) -> schemas.Difficulty:
        if probability > 0.7:
            return schemas.Difficulty.hard
        if probability >= 0.4:
            return schemas.Difficulty.medium
        return schemas.Difficulty.easy

    def _select_next_skill(self,
                            current_skill: str,
                            history: List[schemas.Interaction]) -> Optional[str]:
        skills = self.repo.list_skills()
        if not skills:
            return None

        # Prioritise skills without history, otherwise the first not mastered one.
        history_by_skill: Dict[str, List[schemas.Interaction]] = {}
        for inter in history:
            history_by_skill.setdefault(inter.skill_id, []).append(inter)

        for skill in skills:
            if skill.name == current_skill:
                continue
            skill_history = history_by_skill.get(skill.name, [])
            if not skill_history:
                return skill.name
            probability = skill_history[-1].probability_after or 0.0
            if not self._is_skill_mastered(skill_history, probability):
                return skill.name

        # If every other skill is mastered or unavailable, stay on the current one.
        return None

    def _choose_candidate(self,
                          skill_id: str,
                          desired_diff: schemas.Difficulty,
                          blocked: set[str],
                          attempted: set[str],
                          skill_history: List[schemas.Interaction]) -> Optional[schemas.Exercise]:
        all_exercises = self.exercises.list_by_filters(skill_id=skill_id)
        if not all_exercises:
            return None

        attempt_counts: Dict[str, int] = {}
        last_timestamps: Dict[str, float] = {}
        for inter in skill_history:
            attempt_counts[inter.exercise_id] = attempt_counts.get(inter.exercise_id, 0) + 1
            last_timestamps[inter.exercise_id] = inter.timestamp.timestamp()

        last_exercise_id = skill_history[-1].exercise_id if skill_history else None

        def candidates(diff: Optional[schemas.Difficulty] = None,
                       require_new: bool = False) -> List[schemas.Exercise]:
            pool = all_exercises
            if diff is not None:
                pool = [ex for ex in pool if ex.difficulty == diff]
            result = []
            for ex in pool:
                if ex.id in blocked:
                    continue
                if require_new and ex.id in attempted:
                    continue
                result.append(ex)
            return result

        def rank(options: List[schemas.Exercise]) -> Optional[schemas.Exercise]:
            if not options:
                return None
            options_sorted = sorted(
                options,
                key=lambda ex: (
                    attempt_counts.get(ex.id, 0),
                    last_timestamps.get(ex.id, 0),
                    ex.id,
                )
            )
            if last_exercise_id and len(options_sorted) > 1 and options_sorted[0].id == last_exercise_id:
                for candidate in options_sorted[1:]:
                    if candidate.id != last_exercise_id:
                        return candidate
            return options_sorted[0]

        # Preference order: target difficulty & new → target difficulty & any → other difficulties & new → others
        for diff, require_new in [
            (desired_diff, True),
            (desired_diff, False),
            (None, True),
            (None, False),
        ]:
            selected = rank(candidates(diff, require_new))
            if selected:
                return selected
        return None

    def recommend_next(self, user_id: str) -> Optional[schemas.RecommendationResponse]:
        attempted_all = self._not_attempted(user_id)
        history = sorted(self.repo.list_interactions(user_id), key=lambda x: x.timestamp)

        if not history:
            bundle = self.initial_bundle()
            for exercise in bundle:
                if exercise.id not in attempted_all:
                    idx = self.dkt.skill_to_idx(exercise.skill_id) or -1
                    probability = 0.5
                    return schemas.RecommendationResponse(
                        user_id=user_id,
                        exercise_id=exercise.id,
                        skill_id=exercise.skill_id,
                        probability=probability,
                        difficulty=exercise.difficulty
                    )
            return None

        last = history[-1]
        focus_skill = last.skill_id
        original_skill = focus_skill
        skill_history = self._skill_history(history, focus_skill)
        target_prob = skill_history[-1].probability_after or 0.5

        # Enforce mastery logic only after at least 5 interactions sur la compétence
        mastered_current = False
        if len(skill_history) >= 5 and self._is_skill_mastered(skill_history, target_prob):
            mastered_current = True
            next_skill = self._select_next_skill(focus_skill, history)
            if next_skill:
                focus_skill = next_skill
                skill_history = self._skill_history(history, focus_skill)
                if skill_history:
                    target_prob = skill_history[-1].probability_after or 0.5
                else:
                    target_prob = 0.0
                    mastered_current = False

        if mastered_current and focus_skill == original_skill:
            return schemas.RecommendationResponse(
                user_id=user_id,
                exercise_id="",
                skill_id=focus_skill,
                skill_external_id=None,
                prompt="Compétence validée, bravo !",
                options=None,
                answer=None,
                probability=target_prob,
                difficulty=self._difficulty_from_prob(target_prob),
                mastery=True,
            )

        if not skill_history:
            target_prob = 0.0

        desired_diff = self._difficulty_from_prob(target_prob)
        blocked = self._blocked_exercises(skill_history)
        attempted_skill = {inter.exercise_id for inter in skill_history}

        selected = self._choose_candidate(
            focus_skill,
            desired_diff,
            blocked,
            attempted_skill,
            skill_history,
        )

        if not selected:
            # Try another skill if current one cannot supply more exercises
            next_skill = self._select_next_skill(focus_skill, history)
            if next_skill:
                focus_skill = next_skill
                skill_history = self._skill_history(history, focus_skill)
                if skill_history:
                    target_prob = skill_history[-1].probability_after or 0.5
                    mastered_current = len(skill_history) >= 5 and self._is_skill_mastered(skill_history, target_prob)
                else:
                    target_prob = 0.0
                    mastered_current = False
                blocked = self._blocked_exercises(skill_history)
                attempted_skill = {inter.exercise_id for inter in skill_history}
                desired_diff = self._difficulty_from_prob(target_prob)
                selected = self._choose_candidate(
                    focus_skill,
                    desired_diff,
                    blocked,
                    attempted_skill,
                    skill_history,
                )

        if not selected:
            # Plus aucun exercice disponible pour les compétences restantes
            if mastered_current:
                return schemas.RecommendationResponse(
                    user_id=user_id,
                    exercise_id="",
                    skill_id=focus_skill,
                    skill_external_id=None,
                    prompt="Compétence validée, bravo !",
                    options=None,
                    answer=None,
                    probability=target_prob,
                    difficulty=self._difficulty_from_prob(target_prob),
                    mastery=True,
                )
            return None

        idx = self.dkt.skill_to_idx(selected.skill_id)
        skills, responses = self._history_sequences(user_id)
        probability = 0.5
        if idx is not None:
            probability = self.dkt.predict_probability(skills, responses, idx)

        return schemas.RecommendationResponse(
            user_id=user_id,
            exercise_id=selected.id,
            skill_id=selected.skill_id,
            skill_external_id=selected.skill_external_id,
            prompt=selected.prompt,
            options=selected.options,
            answer=selected.answer,
            probability=probability,
            difficulty=selected.difficulty,
            mastery=False,
        )
