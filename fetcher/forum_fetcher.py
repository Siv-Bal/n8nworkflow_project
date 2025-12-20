"""
Forum workflow ingestion
Source: n8n Community (Discourse)
"""

import requests
from datetime import datetime, timezone

from app.database import SessionLocal
from app.crud import upsert_workflow
from app.scoring import calculate_pcs, generate_explanation

BASE_URL = "https://community.n8n.io"
REQUEST_TIMEOUT = 10


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def extract_workflow_name(title: str) -> str:
    title_lower = title.lower()

    keywords = {
        "google sheets": "Google Sheets",
        "gmail": "Gmail",
        "slack": "Slack",
        "whatsapp": "WhatsApp",
        "notion": "Notion",
        "telegram": "Telegram",
        "ai": "AI",
    }

    found = [v for k, v in keywords.items() if k in title_lower]

    if len(found) >= 2:
        return f"{found[0]} → {found[1]} Workflow"
    elif found:
        return f"{found[0]} Workflow"
    return "General n8n Workflow"


def fetch_latest_topics(limit=50):
    r = requests.get(
        f"{BASE_URL}/latest.json",
        timeout=REQUEST_TIMEOUT
    )
    r.raise_for_status()
    return r.json()["topic_list"]["topics"][:limit]


def utcnow():
    return datetime.now(timezone.utc)


# -------------------------------------------------
# INGESTION
# -------------------------------------------------
def ingest_forum_workflows(country="US", limit=50):
    db = SessionLocal()

    try:
        topics = fetch_latest_topics(limit)

        for topic in topics:
            title = topic.get("title", "")
            workflow_name = extract_workflow_name(title)

            views = topic.get("views", 0)
            likes = topic.get("like_count", 0)
            replies = max(topic.get("posts_count", 1) - 1, 0)

            # PCS (forum = engagement driven)
            scores = calculate_pcs(
                views,
                likes,
                replies,
                workflow_name,
                country
            )

            explanation = generate_explanation(
                views,
                likes,
                replies,
                "unknown"
            )

            workflow_data = {
                # Core
                "name": workflow_name,
                "entity_type": "forum_topic",
                "platform": "Forum",
                "country": country,

                # Source
                "source_type": "forum",
                "source_id": f"n8n_forum_{topic['id']}",
                "source_url": f"{BASE_URL}/t/{topic['slug']}/{topic['id']}",

                # Metrics
                "views": views,
                "likes": likes,
                "comments": replies,

                "like_to_view_ratio": (likes / views) if views else 0,
                "comment_to_view_ratio": (replies / views) if views else 0,

                # Scores
                "popularity_score": scores["popularity_score"],
                "engagement_score": scores["engagement_score"],
                "volume_score": scores["volume_score"],
                "trend_score": None,

                # Metadata
                "explanation": explanation,
                "fetched_at": utcnow(),
            }

            upsert_workflow(db, workflow_data)

    finally:
        db.close()


# -------------------------------------------------
# MANUAL RUN
# -------------------------------------------------
if __name__ == "__main__":
    ingest_forum_workflows(country="US", limit=50)
    ingest_forum_workflows(country="IN", limit=50)
    print("Forum workflows ingested successfully.")
