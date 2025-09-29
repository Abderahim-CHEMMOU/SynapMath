from __future__ import annotations

from typing import List, Tuple

from app.repositories.database import DatabaseRepository
from app.services.dkt import DKTService
from app import schemas


class InteractionService:
    def __init__(self, repository: DatabaseRepository, dkt: DKTService) -> None:
        self.repo = repository
        self.dkt = dkt

    def _history_sequences(self, user_id: str) -> Tuple[List[int], List[int]]:
        interactions = sorted(
            self.repo.list_interactions(user_id),
            key=lambda x: x.timestamp
        )
        skill_indices: List[int] = []
        responses: List[int] = []
        for inter in interactions:
            idx = self.dkt.skill_to_idx(inter.skill_id)
            if idx is None:
                continue
            skill_indices.append(idx)
            responses.append(int(inter.correct))
        return skill_indices, responses

    def record(self, payload: schemas.InteractionCreate) -> schemas.Interaction:
        target_idx = self.dkt.skill_to_idx(payload.skill_id)
        skills, responses = self._history_sequences(payload.user_id)

        prob_before = None
        if target_idx is not None:
            prob_before = self.dkt.predict_probability(skills, responses, target_idx)

        if target_idx is not None:
            skills_after = skills + [target_idx]
            responses_after = responses + [int(payload.correct)]
            prob_after = self.dkt.predict_probability(skills_after, responses_after, target_idx)
        else:
            prob_after = None

        interaction = self.repo.add_interaction(
            payload,
            probability_before=prob_before,
            probability_after=prob_after
        )
        return interaction

    def list_for_user(self, user_id: str) -> List[schemas.Interaction]:
        return self.repo.list_interactions(user_id)
