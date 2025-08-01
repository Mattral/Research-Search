from typing import List, Dict, Any
from neo4j import Session as Neo4jSession
from sqlalchemy.orm import Session
from models.user_models import UserFavorite, UserRecentView
import logging

logger = logging.getLogger(__name__)

# Import from existing recommendation module
from recommendation.scoring import calculate_score

# Neo4j Queries (from the original queries.py)
CITATION_BASED = """
MATCH (u:User {id: $userId})-[:LIKED|VIEWED]->(liked:Paper)
MATCH (liked)-[:CITES]->(rec:Paper)
WHERE NOT (u)-[:LIKED|VIEWED]->(rec)
WITH rec, COUNT(DISTINCT liked) as relevance
RETURN rec.id as paperId, rec.title as title, rec.year as year,
       relevance, 'citation' as source
ORDER BY relevance DESC
LIMIT 15
"""

AUTHOR_BASED = """
MATCH (u:User {id: $userId})-[:LIKED|VIEWED]->(liked:Paper)
MATCH (a:Author)-[:WROTE]->(liked)
MATCH (a)-[:WROTE]->(rec:Paper)
WHERE NOT (u)-[:LIKED|VIEWED]->(rec) AND liked <> rec
WITH rec, COUNT(DISTINCT a) as authorRelevance, collect(DISTINCT a.name)[0..3] as commonAuthors
RETURN rec.id as paperId, rec.title as title, rec.year as year,
       authorRelevance, 'author' as source, commonAuthors
ORDER BY authorRelevance DESC
LIMIT 15
"""

VENUE_BASED = """
MATCH (u:User {id: $userId})-[:LIKED|VIEWED]->(liked:Paper)
MATCH (liked)-[:PUBLISHED_IN]->(v:Venue)
MATCH (rec:Paper)-[:PUBLISHED_IN]->(v)
WHERE NOT (u)-[:LIKED|VIEWED]->(rec) AND liked <> rec
WITH rec, COUNT(DISTINCT v) as venueRelevance, collect(DISTINCT v.name)[0..3] as venues
RETURN rec.id as paperId, rec.title as title, rec.year as year,
       venueRelevance, 'venue' as source, venues
ORDER BY venueRelevance DESC
LIMIT 15
"""

POPULARITY_QUERY = """
MATCH (rec:Paper)<-[:CITES]-(citing:Paper)
WHERE NOT EXISTS {
    MATCH (u:User {id: $userId})-[:LIKED|VIEWED]->(rec)
}
WITH rec, COUNT(citing) as popularity
RETURN rec.id as paperId, rec.title as title, rec.year as year,
       popularity, 'popularity' as source
ORDER BY popularity DESC
LIMIT 10
"""


def get_recommendations(
    neo4j_session: Neo4jSession,
    db: Session,
    user_id: int,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Generate personalized recommendations using the existing scoring logic
    but with real Neo4j data instead of mocked data.
    """
    if neo4j_session is None:
        return []
    
    candidates = {}
    
    # Fetch citation-based candidates
    try:
        result = neo4j_session.run(CITATION_BASED, {"userId": user_id})
        for record in result:
            paper_id = record["paperId"]
            if paper_id not in candidates:
                candidates[paper_id] = {
                    "paperId": paper_id,
                    "title": record["title"],
                    "year": record["year"],
                    "is_cited": True,
                    "same_author": False,
                    "same_venue": False,
                    "popularity": 0,
                    "sources": ["citation"]
                }
    except Exception as e:
        logger.error(f"Citation query error: {e}")
    
    # Fetch author-based candidates
    try:
        result = neo4j_session.run(AUTHOR_BASED, {"userId": user_id})
        for record in result:
            paper_id = record["paperId"]
            if paper_id in candidates:
                candidates[paper_id]["same_author"] = True
                candidates[paper_id]["sources"].append("author")
                candidates[paper_id]["commonAuthors"] = record.get("commonAuthors", [])
            else:
                candidates[paper_id] = {
                    "paperId": paper_id,
                    "title": record["title"],
                    "year": record["year"],
                    "is_cited": False,
                    "same_author": True,
                    "same_venue": False,
                    "popularity": 0,
                    "sources": ["author"],
                    "commonAuthors": record.get("commonAuthors", [])
                }
    except Exception as e:
        logger.error(f"Author query error: {e}")
    
    # Fetch venue-based candidates
    try:
        result = neo4j_session.run(VENUE_BASED, {"userId": user_id})
        for record in result:
            paper_id = record["paperId"]
            if paper_id in candidates:
                candidates[paper_id]["same_venue"] = True
                candidates[paper_id]["sources"].append("venue")
                candidates[paper_id]["venues"] = record.get("venues", [])
            else:
                candidates[paper_id] = {
                    "paperId": paper_id,
                    "title": record["title"],
                    "year": record["year"],
                    "is_cited": False,
                    "same_author": False,
                    "same_venue": True,
                    "popularity": 0,
                    "sources": ["venue"],
                    "venues": record.get("venues", [])
                }
    except Exception as e:
        logger.error(f"Venue query error: {e}")
    
    # Fetch popularity data and add popular papers if not enough candidates
    try:
        result = neo4j_session.run(POPULARITY_QUERY, {"userId": user_id})
        for record in result:
            paper_id = record["paperId"]
            popularity_normalized = min(record["popularity"] / 100.0, 1.0)  # Normalize
            if paper_id in candidates:
                candidates[paper_id]["popularity"] = popularity_normalized
            else:
                candidates[paper_id] = {
                    "paperId": paper_id,
                    "title": record["title"],
                    "year": record["year"],
                    "is_cited": False,
                    "same_author": False,
                    "same_venue": False,
                    "popularity": popularity_normalized,
                    "sources": ["popularity"]
                }
    except Exception as e:
        logger.error(f"Popularity query error: {e}")
    
    # If no candidates from user history, get popular papers
    if not candidates:
        try:
            fallback_query = """
            MATCH (p:Paper)<-[:CITES]-(citing:Paper)
            WITH p, COUNT(citing) as popularity
            OPTIONAL MATCH (a:Author)-[:WROTE]->(p)
            OPTIONAL MATCH (p)-[:PUBLISHED_IN]->(v:Venue)
            RETURN p.id as paperId, p.title as title, p.year as year,
                   popularity, collect(DISTINCT a.name)[0..3] as authors,
                   v.name as venue
            ORDER BY popularity DESC
            LIMIT 20
            """
            result = neo4j_session.run(fallback_query)
            for record in result:
                paper_id = record["paperId"]
                candidates[paper_id] = {
                    "paperId": paper_id,
                    "title": record["title"],
                    "year": record["year"],
                    "is_cited": False,
                    "same_author": False,
                    "same_venue": False,
                    "popularity": min(record["popularity"] / 100.0, 1.0),
                    "sources": ["trending"],
                    "authors": record.get("authors", []),
                    "venue": record.get("venue")
                }
        except Exception as e:
            logger.error(f"Fallback query error: {e}")
    
    # Score and rank candidates using existing scoring function
    recommendations = []
    for paper_id, paper in candidates.items():
        score, reasons = calculate_score(paper)
        recommendations.append({
            "paper_id": paper_id,
            "title": paper["title"],
            "score": score,
            "reason": "; ".join(reasons) if reasons else "Trending in your field",
            "year": paper.get("year"),
            "authors": paper.get("authors", paper.get("commonAuthors", [])),
            "venue": paper.get("venue", paper.get("venues", [""])[0] if paper.get("venues") else None)
        })
    
    # Sort by score and return top results
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations[:limit]


def get_user_history_paper_ids(db: Session, user_id: int) -> Dict[str, List[str]]:
    """Get user's liked and viewed paper IDs from PostgreSQL"""
    favorites = db.query(UserFavorite).filter(UserFavorite.user_id == user_id).all()
    recent_views = db.query(UserRecentView).filter(UserRecentView.user_id == user_id).all()
    
    return {
        "liked": [f.paper_id for f in favorites],
        "viewed": [v.paper_id for v in recent_views]
    }
