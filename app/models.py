from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Workflow(Base):
    __tablename__ = "workflows"

    # --------------------
    # Primary Identity
    # --------------------
    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, default="video")  # video / topic
    platform = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False, index=True)

    # --------------------
    # Source Evidence
    # --------------------
    source_type = Column(String, nullable=False)  # youtube / forum
    source_id = Column(String, nullable=False, index=True, unique=True)
    source_url = Column(String, nullable=False)
    source_title = Column(String)
    channel_name = Column(String)

    published_at = Column(DateTime(timezone=True))

    # --------------------
    # Raw Metrics
    # --------------------
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)

    # --------------------
    # Ratios
    # --------------------
    like_to_view_ratio = Column(Float)
    comment_to_view_ratio = Column(Float)

    # --------------------
    # Scores (Normalized 0–100)
    # --------------------
    popularity_score = Column(Integer)
    engagement_score = Column(Integer)
    volume_score = Column(Integer)
    trend_score = Column(Integer)

    # --------------------
    # Google Trends
    # --------------------
    trend_direction = Column(String)  # rising / falling / stable
    trend_avg_interest = Column(Float)
    trend_samples = Column(Integer)

    # --------------------
    # Metadata
    # --------------------
    explanation = Column(String)

    fetched_at = Column(DateTime(timezone=True), default=utcnow)
    last_updated = Column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow
    )
