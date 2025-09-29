from pathlib import Path
import os


BACKEND_DIR = Path(__file__).resolve().parent
WEB_APP_DIR = BACKEND_DIR.parent
PROJECT_ROOT = WEB_APP_DIR.parent


class Settings:
    """Configuration values used across the backend."""

    project_root: Path = PROJECT_ROOT
    ckpt_dir: Path = Path(
        os.getenv("DKT_CKPT_DIR",
                  PROJECT_ROOT / "ckpts" / "dkt" / "ASSIST2009")
    )
    mappings_dir: Path = Path(
        os.getenv("DKT_MAPPINGS_DIR",
                  PROJECT_ROOT / "datasets" / "ASSIST2009")
    )
    initial_easy_count: int = int(os.getenv("INITIAL_EASY_COUNT", 2))
    initial_medium_count: int = int(os.getenv("INITIAL_MEDIUM_COUNT", 2))
    initial_hard_count: int = int(os.getenv("INITIAL_HARD_COUNT", 1))
    exercises_seed_path: Path = Path(
        os.getenv(
            "EXERCISES_SEED_PATH",
            BACKEND_DIR / "data" / "exercices.json"
        )
    )

    pg_user: str = os.getenv("POSTGRES_USER", "postgres")
    pg_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    pg_host: str = os.getenv("POSTGRES_HOST", "db")
    pg_port: str = os.getenv("POSTGRES_PORT", "5432")
    pg_db: str = os.getenv("POSTGRES_DB", "knowledge_tracing")

    database_url: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
    )


settings = Settings()
