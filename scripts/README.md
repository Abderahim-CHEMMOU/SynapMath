# Utility scripts

## ASSIST2009 skill analysis

Inspect dataset skills, usage, and suggested difficulty buckets:

```bash
python scripts/assist2009_skill_analysis.py \
  --dataset-path datasets/ASSIST2009/skill_builder_data.csv \
  --top-n 30 \
  --export-json assets/assist2009_skill_summary.json
```

The tool prints the top skills in the console and, when `--export-json` is provided, saves a JSON array with interaction counts, accuracy, and a coarse difficulty bucket. Use the output to align handcrafted exercises with dataset skills and to pre-fill mappings for the backend.

## Database bootstrap

Initialise the PostgreSQL database schema and load the exercise seed file:

```bash
python scripts/seed_db.py
```

The script relies on the same environment variables as the FastAPI app (see `web_app/backend/README.md`).
