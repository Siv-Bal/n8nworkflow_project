def calculate_pcs(views, likes, comments, workflow_name, country):
    """
    PCS = Popularity / Engagement / Volume scoring
    Trend score is OPTIONAL and defaults safely
    """

    # --------------------
    # Normalize inputs
    # --------------------
    views = views or 0
    likes = likes or 0
    comments = comments or 0

    # --------------------
    # Engagement
    # --------------------
    engagement_score = min(
        100,
        int((likes * 0.7 + comments * 1.2) / max(views, 1) * 1000)
    )

    # --------------------
    # Volume
    # --------------------
    volume_score = min(100, int(views / 10_000))

    # --------------------
    # Trend (DISABLED / OPTIONAL)
    # --------------------
    trend_score = 0  # <-- IMPORTANT FIX

    # --------------------
    # Popularity
    # --------------------
    popularity_score = min(
        100,
        int(engagement_score * 0.5 + volume_score * 0.5 + trend_score)
    )

    return {
        "popularity_score": popularity_score,
        "engagement_score": engagement_score,
        "volume_score": volume_score,
    }


def generate_explanation(views, likes, comments, trend_direction):
    return (
        f"This workflow has {views} views with "
        f"{likes} likes and {comments} comments. "
        f"Trend direction is {trend_direction}."
    )
