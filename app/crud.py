from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Workflow


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def parse_iso_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def compute_trend(previous_views: int | None, current_views: int):
    """
    Derive trend direction and score from historical view delta.
    """
    if previous_views is None:
        return None, "unknown"

    delta = current_views - previous_views

    if delta > 0:
        return min(100, delta // 1000), "rising"
    elif delta < 0:
        return min(100, abs(delta) // 1000), "falling"
    else:
        return 0, "stable"


# --------------------------------------------------
# Upsert Logic (WITH HISTORICAL TREND)
# --------------------------------------------------
def upsert_workflow(db: Session, data: dict) -> Workflow:
    workflow = (
        db.query(Workflow)
        .filter(
            Workflow.source_type == data["source_type"],
            Workflow.source_id == data["source_id"],
        )
        .first()
    )

    previous_views = workflow.views if workflow else None

    if not workflow:
        workflow = Workflow(
            source_type=data["source_type"],
            source_id=data["source_id"],
        )
        db.add(workflow)

    # --------------------
    # Core Identity
    # --------------------
    workflow.name = data["name"]
    workflow.entity_type = data["entity_type"]
    workflow.platform = data["platform"]
    workflow.country = data["country"]

    # --------------------
    # Source Evidence
    # --------------------
    workflow.source_url = data["source_url"]
    workflow.source_title = data.get("source_title")
    workflow.channel_name = data.get("channel_name")
    workflow.published_at = parse_iso_datetime(data.get("published_at"))

    # --------------------
    # Raw Metrics
    # --------------------
    current_views = data.get("views", 0)
    workflow.views = current_views
    workflow.likes = data.get("likes", 0)
    workflow.comments = data.get("comments", 0)

    # --------------------
    # Ratios
    # --------------------
    workflow.like_to_view_ratio = data.get("like_to_view_ratio", 0.0)
    workflow.comment_to_view_ratio = data.get("comment_to_view_ratio", 0.0)

    # --------------------
    # Scores
    # --------------------
    workflow.popularity_score = data.get("popularity_score")
    workflow.engagement_score = data.get("engagement_score")
    workflow.volume_score = data.get("volume_score")

    # --------------------
    # 🔥 HISTORICAL TREND (DERIVED HERE)
    # --------------------
    trend_score, trend_direction = compute_trend(
        previous_views,
        current_views
    )

    workflow.trend_score = trend_score
    workflow.trend_direction = trend_direction

    # External / optional
    workflow.trend_avg_interest = data.get("trend_avg_interest")
    workflow.trend_samples = data.get("trend_samples")

    # --------------------
    # Metadata
    # --------------------
    workflow.explanation = data.get("explanation")
    workflow.fetched_at = data.get("fetched_at")

    db.commit()
    db.refresh(workflow)

    return workflow


# --------------------------------------------------
# Read Logic
# --------------------------------------------------
def get_workflows(
    db: Session,
    platform: str | None = None,
    country: str | None = None,
    limit: int = 50,
):
    query = db.query(Workflow)

    if platform:
        query = query.filter(Workflow.platform == platform)

    if country:
        query = query.filter(Workflow.country == country)

    return (
        query
        .order_by(Workflow.popularity_score.desc())
        .limit(limit)
        .all()
    )
