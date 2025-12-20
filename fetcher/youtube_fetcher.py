import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

from app.database import SessionLocal
from app.scoring import calculate_pcs, generate_explanation
from app.crud import upsert_workflow

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"
TIMEOUT = 10

if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not found in environment")

# --------------------------------------------------
# SEARCH QUERIES
# --------------------------------------------------
QUERIES = [
    "n8n whatsapp automation",
    "n8n whatsapp ai",
    "n8n slack automation",
    "n8n slack ai",
    "n8n google sheets automation",
    "n8n google sheets ai",
    "n8n gmail automation",
    "n8n gmail ai",
    "n8n notion workflow",
    "n8n webhook automation",
    "n8n api integration",
]

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def utcnow():
    return datetime.now(timezone.utc)


def parse_iso_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def normalize_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def extract_workflow_name(title: str) -> str:
    title = title.lower()

    mapping = {
        "whatsapp": "WhatsApp",
        "slack": "Slack",
        "google sheets": "Google Sheets",
        "gmail": "Gmail",
        "notion": "Notion",
        "ai": "AI",
    }

    found = [v for k, v in mapping.items() if k in title]

    if len(found) >= 2:
        return f"{found[0]} → {found[1]} Automation"
    elif found:
        return f"{found[0]} Automation"

    return "General n8n Automation"


# --------------------------------------------------
# YOUTUBE API
# --------------------------------------------------
def search_videos(query: str, country: str, max_results: int):
    r = requests.get(
        f"{BASE_URL}/search",
        params={
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "regionCode": country,
            "key": YOUTUBE_API_KEY,
        },
        timeout=TIMEOUT,
        
    )
    if r.status_code in (403, 429):
            print("YouTube quota exceeded or access denied. Skipping YouTube ingestion.")
            return []
        
    r.raise_for_status()
    return r.json().get("items", [])


def get_video_stats(video_ids):
    if not video_ids:
        return []

    r = requests.get(
        f"{BASE_URL}/videos",
        params={
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
            "key": YOUTUBE_API_KEY,
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("items", [])


# --------------------------------------------------
# INGESTION
# --------------------------------------------------
def ingest_youtube_workflows(country="US", max_results=10):
    db = SessionLocal()

    try:
        for query in QUERIES:
            search_results = search_videos(query, country, max_results)

            video_ids = [
                v["id"]["videoId"]
                for v in search_results
                if v.get("id", {}).get("videoId")
            ]

            videos = get_video_stats(video_ids)

            for video in videos:
                stats = video.get("statistics", {})
                snippet = video.get("snippet", {})

                views = normalize_int(stats.get("viewCount"))
                likes = normalize_int(stats.get("likeCount"))
                comments = normalize_int(stats.get("commentCount"))

                workflow_name = extract_workflow_name(snippet.get("title", ""))

                # ✅ FIX: scores WAS MISSING
                scores = calculate_pcs(
                    views,
                    likes,
                    comments,
                    workflow_name,
                    country,
                )

                # Google Trends disabled (non-blocking)
                trend = {
                    "trend_score": None,
                    "trend_direction": "unknown",
                    "avg_interest": None,
                    "samples": 0,
                }

                workflow_data = {
                    # Core
                    "name": workflow_name,
                    "entity_type": "video",
                    "platform": "YouTube",
                    "country": country,

                    # Source
                    "source_type": "youtube",
                    "source_id": video["id"],
                    "source_url": f"https://www.youtube.com/watch?v={video['id']}",
                    "source_title": snippet.get("title"),
                    "channel_name": snippet.get("channelTitle"),
                    "published_at": parse_iso_datetime(
                        snippet.get("publishedAt")
                    ),

                    # Metrics
                    "views": views,
                    "likes": likes,
                    "comments": comments,

                    # Ratios
                    "like_to_view_ratio": round(likes / views, 4) if views else 0.0,
                    "comment_to_view_ratio": round(comments / views, 4) if views else 0.0,

                    # Scores
                    "popularity_score": scores["popularity_score"],
                    "engagement_score": scores["engagement_score"],
                    "volume_score": scores["volume_score"],
                    "trend_score": trend["trend_score"],

                    # Trends
                    "trend_direction": trend["trend_direction"],
                    "trend_avg_interest": trend["avg_interest"],
                    "trend_samples": trend["samples"],

                    # Metadata
                    "explanation": generate_explanation(
                        views, likes, comments, trend["trend_direction"]
                    ),
                    "fetched_at": utcnow(),
                }

                upsert_workflow(db, workflow_data)

    finally:
        db.close()


# --------------------------------------------------
# ENTRYPOINT
# --------------------------------------------------
if __name__ == "__main__":
    ingest_youtube_workflows(country="US", max_results=10)
    ingest_youtube_workflows(country="IN", max_results=10)

