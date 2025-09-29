from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine, SessionLocal
from app.dependencies import get_dkt_service
from app.seed import seed_skills_and_exercises
from app.routers import auth, exercises, interactions, recommendations, students


app = FastAPI(title="Adaptive Learning Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(exercises.router)
app.include_router(interactions.router)
app.include_router(recommendations.router)


@app.on_event("startup")
async def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_skills_and_exercises(session)
    get_dkt_service()


@app.get("/")
def root() -> dict:
    return {"status": "ok", "message": "Adaptive learning backend pret"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
