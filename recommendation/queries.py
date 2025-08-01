CITATION_BASED = """
MATCH (p:Paper)<-[:LIKED]-(u:User {id:$userId})
MATCH (p)-[:CITES]->(rec:Paper)
RETURN rec, COUNT(*) AS score
ORDER BY score DESC
LIMIT 10
"""

AUTHOR_BASED = """
MATCH (u:User {id:$userId})-[:LIKED]->(p:Paper)
MATCH (a:Author)-[:WROTE]->(p)
MATCH (a)-[:WROTE]->(rec:Paper)
WHERE p <> rec
RETURN rec
"""

VENUE_BASED = """
MATCH (u:User {id:$userId})-[:LIKED]->(p:Paper)
MATCH (p)-[:PUBLISHED_IN]->(v:Venue)
MATCH (rec:Paper)-[:PUBLISHED_IN]->(v)
WHERE p <> rec
RETURN rec.id AS paperId, 1 AS venueScore
"""

POPULARITY_QUERY = """
MATCH (rec:Paper)<-[:CITES]-()
RETURN rec.id AS paperId, COUNT(*) AS popularity
ORDER BY popularity DESC
LIMIT 10
"""
