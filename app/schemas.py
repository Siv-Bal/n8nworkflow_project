from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WorkflowOut(BaseModel):
    id: int

    name: str
    entity_type: str
    platform: str
    country: str

    source_type: str
    source_id: str
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    channel_name: Optional[str] = None

    views: int
    likes: int
    comments: int

    like_to_view_ratio: float
    comment_to_view_ratio: float

    popularity_score: int
    engagement_score: int
    volume_score: int

    # 🔥 FIX IS HERE
    trend_score: Optional[int] = None
    trend_direction: Optional[str] = None
    trend_avg_interest: Optional[float] = None
    trend_samples: Optional[int] = None

    explanation: Optional[str] = None
    fetched_at: Optional[datetime] = None

    class Config:
        from_attributes = True
