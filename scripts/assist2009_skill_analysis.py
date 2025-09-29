"""Utility to inspect ASSIST2009 skill statistics and build mapping templates.

Run from repository root:
    python scripts/assist2009_skill_analysis.py \
        --dataset-path datasets/ASSIST2009/skill_builder_data.csv \
        --top-n 20 --export-json assets/assist2009_skill_summary.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


@dataclass
class SkillSummary:
    skill_name: str
    skill_id: str
    interactions: int
    students: int
    accuracy: float
    avg_attempts: float

    def difficulty_bucket(self) -> str:
        if self.accuracy >= 0.8:
            return "easy"
        if self.accuracy >= 0.6:
            return "medium"
        return "hard"

    def to_mapping_row(self) -> Dict[str, object]:
        data = asdict(self)
        data["difficulty_bucket"] = self.difficulty_bucket()
        return data


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")
    df = pd.read_csv(path, encoding="latin1", low_memory=False)
    df = df.dropna(subset=["skill_name"])
    df = df.drop_duplicates(subset=["user_id", "order_id", "skill_name"])
    return df


def compute_skill_stats(df: pd.DataFrame) -> List[SkillSummary]:
    grouped = df.groupby("skill_name")
    stats: List[SkillSummary] = []
    for skill_name, group in grouped:
        interactions = len(group)
        students = group["user_id"].nunique()
        accuracy = float(group["correct"].mean()) if interactions else 0.0
        avg_attempts = float(group["attempt_count"].mean()) if interactions else 0.0
        skill_ids = group["skill_id"].dropna().unique()
        if len(skill_ids):
            raw_skill_id = skill_ids[0]
            if isinstance(raw_skill_id, (int, float)) and not pd.isna(raw_skill_id):
                if float(raw_skill_id).is_integer():
                    skill_id = str(int(raw_skill_id))
                else:
                    skill_id = str(raw_skill_id)
            else:
                skill_id = str(raw_skill_id)
        else:
            skill_id = ""
        stats.append(
            SkillSummary(
                skill_name=skill_name,
                skill_id=skill_id,
                interactions=interactions,
                students=students,
                accuracy=accuracy,
                avg_attempts=avg_attempts,
            )
        )
    stats.sort(key=lambda item: item.interactions, reverse=True)
    return stats


def summarize(stats: List[SkillSummary], top_n: int) -> None:
    print(f"Total skills: {len(stats)}")
    print(f"Top {top_n} skills by interaction count:\n")
    header = "{:<6} {:<10} {:<40} {:>10} {:>10} {:>10} {:>10}".format(
        "Rank", "SkillID", "Skill", "Interacts", "Students", "Accuracy", "Attempts"
    )
    print(header)
    print("-" * len(header))
    for idx, item in enumerate(stats[:top_n], start=1):
        print(
            "{:<6} {:<10} {:<40} {:>10} {:>10} {:>10.3f} {:>10.2f}".format(
                idx,
                item.skill_id[:10],
                item.skill_name[:40],
                item.interactions,
                item.students,
                item.accuracy,
                item.avg_attempts,
            )
        )


def export_json(stats: List[SkillSummary], output_path: Path, top_n: Optional[int]) -> None:
    payload = [item.to_mapping_row() for item in stats[:top_n] if item.interactions]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, ensure_ascii=False)
    print(f"Saved summary to {output_path}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyse ASSIST2009 skills and suggest difficulty buckets."
    )
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=Path("datasets/ASSIST2009/skill_builder_data.csv"),
        help="Path to skill_builder_data.csv",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of top skills to display/export",
    )
    parser.add_argument(
        "--export-json",
        type=Path,
        default=None,
        help="Optional path to save the summary JSON",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    df = load_dataset(args.dataset_path)
    stats = compute_skill_stats(df)
    summarize(stats, args.top_n)

    if args.export_json:
        export_json(stats, args.export_json, args.top_n)


if __name__ == "__main__":
    main()
