# Backend Deployment Guide

## Local development

1. Ensure PostgreSQL is running and accessible (default `postgres/postgres` on `localhost:5432` with database `knowledge_tracing`).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create tables and load seeded exercises:
   ```bash
   python ../../scripts/seed_db.py
   ```
4. Start the API:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Docker / Docker Compose

Build and run the backend together with PostgreSQL:
```bash
docker compose up --build
```

By default the API is available at `http://127.0.0.1:8000` and the database on `localhost:5432`.

## Environment variables

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` — database connection settings.
- `DKT_CKPT_DIR`, `DKT_MAPPINGS_DIR` — location of the trained checkpoint and mapping files (overridden in Docker).
- `EXERCISES_SEED_PATH` — path to the JSON seed file (defaults to `app/data/exercices.json`).

## API authentication

The main routes (`/students`, `/interactions`, `/recommendations`) require a Bearer token.

1. **Création d’un compte** : `POST /auth/register` avec un JSON `{ "user_id": "...", "name": "...", "password": "..." }`.
2. **Connexion** : `POST /auth/login` (même payload que ci-dessus) renvoie `{ "access_token": "..." }`.
3. Inclure `Authorization: Bearer <access_token>` dans les requêtes suivantes.
4. `POST /auth/logout` supprime le token courant et `GET /auth/me` retourne le profil authentifié.
