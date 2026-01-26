from recommendation.scoring import calculate_score

def recommend_papers(user_id: int):
    candidates = [
        {
            "paperId": "P101",
            "title": "Graph-Based Recommendation Systems",
            "is_cited": True,
            "same_author": True,
            "same_venue": False,
            "popularity": 0.8
        },
        {
            "paperId": "P202",
            "title": "Neo4j for Research Networks",
            "is_cited": False,
            "same_author": True,
            "same_venue": True,
            "popularity": 0.6
        }
    ]

    recommendations = []

    for p in candidates:
        score, reasons = calculate_score(p)
        recommendations.append({
            "paperId": p["paperId"],
            "title": p["title"],
            "score": score,
            "reason": "; ".join(reasons)
        })

    # Rank papers by score
    recommendations.sort(key=lambda x: x["score"], reverse=True)

    result = {
        "userId": user_id,
        "recommendations": recommendations
    }

    print("DEBUG: recommend_papers output:", result)  # <-- debug print
    return result

