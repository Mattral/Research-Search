from typing import List, Optional, Dict, Any
from neo4j import Session as Neo4jSession
import logging

logger = logging.getLogger(__name__)


def search_papers(
    session: Neo4jSession,
    title: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Search papers in Neo4j by title, author, or year"""
    if session is None:
        return []
    
    conditions = []
    params = {"limit": limit}
    
    # Build dynamic query based on search parameters
    base_query = "MATCH (p:Paper)"
    
    if author:
        base_query = "MATCH (a:Author)-[:WROTE]->(p:Paper)"
        conditions.append("toLower(a.name) CONTAINS toLower($author)")
        params["author"] = author
    
    if title:
        conditions.append("toLower(p.title) CONTAINS toLower($title)")
        params["title"] = title
    
    if year:
        conditions.append("p.year = $year")
        params["year"] = year
    
    where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    
    # Get authors for each paper
    query = f"""
    {base_query}
    {where_clause}
    OPTIONAL MATCH (auth:Author)-[:WROTE]->(p)
    OPTIONAL MATCH (p)-[:PUBLISHED_IN]->(v:Venue)
    OPTIONAL MATCH (cited:Paper)-[:CITES]->(p)
    WITH p, collect(DISTINCT auth.name) as authors, v.name as venue, count(DISTINCT cited) as citationCount
    RETURN p.id as paper_id, 
           p.title as title, 
           p.abstract as abstract,
           p.year as year,
           authors,
           venue,
           citationCount,
           p.url as url
    ORDER BY citationCount DESC
    LIMIT $limit
    """
    
    try:
        result = session.run(query, params)
        papers = []
        for record in result:
            papers.append({
                "paper_id": record["paper_id"],
                "title": record["title"],
                "abstract": record["abstract"],
                "year": record["year"],
                "authors": record["authors"] if record["authors"] else [],
                "venue": record["venue"],
                "citation_count": record["citationCount"],
                "url": record["url"]
            })
        return papers
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []


def get_paper_by_id(session: Neo4jSession, paper_id: str) -> Optional[Dict[str, Any]]:
    """Get a single paper by ID with full details"""
    if session is None:
        return None
    
    query = """
    MATCH (p:Paper {id: $paper_id})
    OPTIONAL MATCH (auth:Author)-[:WROTE]->(p)
    OPTIONAL MATCH (p)-[:PUBLISHED_IN]->(v:Venue)
    OPTIONAL MATCH (cited:Paper)-[:CITES]->(p)
    OPTIONAL MATCH (p)-[:CITES]->(ref:Paper)
    WITH p, 
         collect(DISTINCT auth.name) as authors, 
         v.name as venue, 
         count(DISTINCT cited) as citationCount,
         collect(DISTINCT ref.id) as references,
         collect(DISTINCT cited.id) as citedBy
    RETURN p.id as paper_id, 
           p.title as title, 
           p.abstract as abstract,
           p.year as year,
           authors,
           venue,
           citationCount,
           p.url as url,
           references,
           citedBy
    """
    
    try:
        result = session.run(query, {"paper_id": paper_id})
        record = result.single()
        if record:
            return {
                "paper_id": record["paper_id"],
                "title": record["title"],
                "abstract": record["abstract"],
                "year": record["year"],
                "authors": record["authors"] if record["authors"] else [],
                "venue": record["venue"],
                "citation_count": record["citationCount"],
                "url": record["url"],
                "references": record["references"][:20] if record["references"] else [],
                "cited_by": record["citedBy"][:20] if record["citedBy"] else []
            }
        return None
    except Exception as e:
        logger.error(f"Get paper error: {e}")
        return None


def get_all_papers(session: Neo4jSession, limit: int = 50) -> List[Dict[str, Any]]:
    """Get all papers (for browsing)"""
    if session is None:
        return []
    
    query = """
    MATCH (p:Paper)
    OPTIONAL MATCH (auth:Author)-[:WROTE]->(p)
    OPTIONAL MATCH (p)-[:PUBLISHED_IN]->(v:Venue)
    OPTIONAL MATCH (cited:Paper)-[:CITES]->(p)
    WITH p, collect(DISTINCT auth.name) as authors, v.name as venue, count(DISTINCT cited) as citationCount
    RETURN p.id as paper_id, 
           p.title as title, 
           p.abstract as abstract,
           p.year as year,
           authors,
           venue,
           citationCount,
           p.url as url
    ORDER BY citationCount DESC
    LIMIT $limit
    """
    
    try:
        result = session.run(query, {"limit": limit})
        papers = []
        for record in result:
            papers.append({
                "paper_id": record["paper_id"],
                "title": record["title"],
                "abstract": record["abstract"],
                "year": record["year"],
                "authors": record["authors"] if record["authors"] else [],
                "venue": record["venue"],
                "citation_count": record["citationCount"],
                "url": record["url"]
            })
        return papers
    except Exception as e:
        logger.error(f"Get all papers error: {e}")
        return []


def track_paper_view(session: Neo4jSession, user_id: int, paper_id: str) -> bool:
    """Track paper view in Neo4j (create User-VIEWED-Paper relationship)"""
    if session is None:
        return False
    
    query = """
    MERGE (u:User {id: $user_id})
    WITH u
    MATCH (p:Paper {id: $paper_id})
    MERGE (u)-[r:VIEWED]->(p)
    SET r.timestamp = datetime()
    RETURN r
    """
    
    try:
        session.run(query, {"user_id": user_id, "paper_id": paper_id})
        return True
    except Exception as e:
        logger.error(f"Track view error: {e}")
        return False


def track_paper_like(session: Neo4jSession, user_id: int, paper_id: str, liked: bool = True) -> bool:
    """Track paper like in Neo4j (create/delete User-LIKED-Paper relationship)"""
    if session is None:
        return False
    
    if liked:
        query = """
        MERGE (u:User {id: $user_id})
        WITH u
        MATCH (p:Paper {id: $paper_id})
        MERGE (u)-[r:LIKED]->(p)
        SET r.timestamp = datetime()
        RETURN r
        """
    else:
        query = """
        MATCH (u:User {id: $user_id})-[r:LIKED]->(p:Paper {id: $paper_id})
        DELETE r
        RETURN true as deleted
        """
    
    try:
        session.run(query, {"user_id": user_id, "paper_id": paper_id})
        return True
    except Exception as e:
        logger.error(f"Track like error: {e}")
        return False
