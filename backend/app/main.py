import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app.routers import ai, exercises, progress, topics, users
from app.schemas import HealthResponse
from app.seed import seed_database

app = FastAPI(title="Python Refresh Trainer", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", python_version=sys.version.split()[0])
