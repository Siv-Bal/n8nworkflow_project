from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.crud import get_workflows
from app.schemas import WorkflowOut
from fetcher.youtube_fetcher import ingest_youtube_workflows
from app.database import engine, Base

# --------------------------------------------------
# App Setup
# --------------------------------------------------
app = FastAPI(
    title="n8n Workflow Intelligence API",
    description=(
        "A multi-source analytics API that tracks popularity, engagement, "
        "and trend signals across the n8n automation ecosystem."
    ),
    version="1.0.0",
)
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# DB Dependency
# --------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------
# System
# --------------------------------------------------
@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Simple health endpoint to verify the API is running.",
)
def health():
    return {"status": "ok"}


# --------------------------------------------------
# Admin / Ingestion
# --------------------------------------------------
@app.post(
    "/admin/ingest",
    tags=["Admin"],
    summary="Refresh workflow data",
    description=(
        "Fetches the latest data from YouTube and forums, updates existing "
        "records, and recalculates popularity and trend signals. "
        "This endpoint is intended for admin or scheduled use only."
    ),
)
def ingest():
    try:
        ingest_youtube_workflows("US", 10)
        ingest_youtube_workflows("IN", 10)
        return {"status": "ingestion completed (YouTube may be skipped if quota exceeded)"}
    except Exception as e:
        return {"status": "partial failure", "error": str(e)}


# --------------------------------------------------
# Public / Read API
# --------------------------------------------------
@app.get(
    "/workflows",
    response_model=list[WorkflowOut],
    tags=["Workflows"],
    summary="List workflows",
    description=(
        "Returns a list of workflows ranked by popularity score. "
        "Supports optional filtering by platform and country."
    ),
)
def list_workflows(
    platform: str | None = None,
    country: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return get_workflows(db, platform, country, limit)


