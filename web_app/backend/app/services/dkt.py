from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Iterable, Optional

try:
    import torch
except ImportError:  # pragma: no cover - torch is optional at runtime
    torch = None

from app.config import settings


class DKTService:
    """Thin wrapper around the trained DKT checkpoint."""

    def __init__(self,
                 ckpt_dir: Optional[Path] = None,
                 mappings_dir: Optional[Path] = None) -> None:
        self.ckpt_dir = ckpt_dir or settings.ckpt_dir
        self.mappings_dir = mappings_dir or settings.mappings_dir
        self.model = None
        self.q2idx = {}
        self.device = torch.device("cuda" if torch and torch.cuda.is_available() else "cpu") if torch else None
        self._load_assets()

    def _load_assets(self) -> None:
        ckpt_path = self.ckpt_dir / "model.ckpt"
        mapping_path = self.mappings_dir / "q2idx.pkl"
        if torch is None:
            return
        try:
            if ckpt_path.exists():
                from models.dkt import DKT  # type: ignore

                with open(self.mappings_dir / "q_list.pkl", "rb") as f:
                    q_list = pickle.load(f)
                num_q = len(q_list)

                config_path = self.ckpt_dir / "model_config.json"
                with open(config_path, "r", encoding="utf-8") as jf:
                    config = json.load(jf)

                self.model = DKT(num_q, **config)
                state = torch.load(ckpt_path, map_location=self.device)
                self.model.load_state_dict(state)
                self.model.to(self.device)
                self.model.eval()
        except Exception:
            self.model = None
        if mapping_path.exists():
            with open(mapping_path, "rb") as f:
                self.q2idx = pickle.load(f)

    def skill_to_idx(self, skill_name: str) -> Optional[int]:
        return self.q2idx.get(skill_name)

    def predict_probability(self,
                            skill_indices: Iterable[int],
                            responses: Iterable[bool],
                            target_skill_idx: int) -> float:
        if not self.model or torch is None or self.device is None:
            return 0.5
        skills = list(skill_indices)
        answers = [int(r) for r in responses]
        if not skills or len(skills) != len(answers):
            return 0.5
        q_tensor = torch.tensor(skills, dtype=torch.long, device=self.device).unsqueeze(0)
        r_tensor = torch.tensor(answers, dtype=torch.long, device=self.device).unsqueeze(0)
        with torch.no_grad():
            preds = self.model(q_tensor, r_tensor)
        target = preds[0, -1, target_skill_idx].item()
        return float(target)


dkt_service = DKTService()
