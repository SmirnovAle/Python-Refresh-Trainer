import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.migrations import run_migrations
from app.routers import ai, auth, exercises, progress, topics, users
from app.schemas import HealthResponse
from app.seed import seed_database, sync_exercise_explanations, sync_topic_content
from app.services.auth_service import cleanup_inactive_accounts

app = FastAPI(title="Python Refresh Trainer", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(topics.router, prefix="/api")
app.include_router(exercises.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    data_dir = Path("./data")
    data_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    run_migrations()

    db = SessionLocal()
    try:
        seed_database(db)
        sync_topic_content(db)
        sync_exercise_explanations(db)
        cleanup_inactive_accounts(db)
    finally:
        db.close()


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", python_version=sys.version.split()[0])
