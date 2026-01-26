def calculate_score(paper):
    score = 0.0
    reasons = []

    if paper.get("is_cited"):
        score += 0.4
        reasons.append("Cited by a paper you liked")

    if paper.get("same_author"):
        score += 0.25
        reasons.append("Same author")

    if paper.get("same_venue"):
        score += 0.25
        reasons.append("Same venue")

    score += 0.1 * paper.get("popularity", 0)

    return round(score, 2), reasons
