"""Create database schema and load seed exercises into PostgreSQL."""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
 
backend_candidates = [
    PROJECT_ROOT / "web_app" / "backend",
    PROJECT_ROOT / "app",
]

for candidate in backend_candidates:
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.append(str(candidate))
        break

from app.config import settings
from app.db import Base, engine, SessionLocal
from app.seed import seed_skills_and_exercises


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_skills_and_exercises(session)
    print("Database initialised using", settings.database_url)


if __name__ == "__main__":
    main()
