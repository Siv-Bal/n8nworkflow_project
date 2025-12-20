from app.scoring import calculate_pcs, generate_explanation

scores = calculate_pcs(
    views=469959,
    likes=8445,
    comments=199
)

scores, generate_explanation(scores)
