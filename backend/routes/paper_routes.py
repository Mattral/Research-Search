from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from db.postgres import get_db
from db.neo4j import get_neo4j_session
from db.mongo import papers_collection
from models.user_models import User, UserFavorite, UserRecentView
from schemas.paper_schemas import (
    PaperResponse, PaperDetailResponse,
    RecommendationResponse, UserFavoriteResponse, UserRecentViewResponse,
)
from services.auth_service import get_current_user
from services.paper_service import (
    search_papers, get_all_papers, get_paper_by_id,
    track_paper_view, track_paper_like,
)
from services.recommendation_service import get_recommendations
from services.semantic_scholar_service import get_paper_details as get_ss_paper_details
from services.openalex_service import get_work_details as get_oa_work_details
from neo4j import Session as Neo4jSession

router = APIRouter(prefix="/api/papers", tags=["Papers"])


async def _get_external_details(paper_id: str):
    """Resolve a paper from external sources by ID convention.
    OpenAlex work IDs start with 'W'; otherwise treat as Semantic Scholar."""
    if paper_id.startswith("W") and paper_id[1:].isdigit():
        return await get_oa_work_details(paper_id)
    return await get_ss_paper_details(paper_id)


async def _get_local_or_external(paper_id: str):
    """Return normalized detail dict from the Mongo corpus, else external APIs."""
    doc = await papers_collection.find_one({"paper_id": paper_id}, {"embedding": 0, "_id": 0})
    if doc:
        return {
            "paper_id": doc["paper_id"],
            "title": doc.get("title", ""),
            "abstract": doc.get("abstract", ""),
            "year": doc.get("year"),
            "authors": doc.get("authors", []) or [],
            "venue": doc.get("journal"),
            "citation_count": doc.get("citation_count", 0) or 0,
            "url": doc.get("url"),
            "references": [],
            "cited_by": [],
        }
    details = await _get_external_details(paper_id)
    if not details:
        return None
    return {
        "paper_id": details.get("source_id") or paper_id,
        "title": details.get("title", ""),
        "abstract": details.get("abstract", ""),
        "year": details.get("year"),
        "authors": details.get("authors", []) or [],
        "venue": details.get("journal"),
        "citation_count": details.get("citation_count", 0) or 0,
        "url": details.get("url"),
        "references": [r["id"] for r in details.get("references", [])],
        "cited_by": [c["id"] for c in details.get("citations", [])],
    }


async def _resolve_title(paper_id: str):
    detail = await _get_local_or_external(paper_id)
    return detail["title"] if detail else None


@router.get("/search", response_model=List[PaperResponse])
def search(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
):
    """Search papers by title, author, or year (legacy Neo4j store)."""
    papers = search_papers(neo4j_session, title, author, year, limit)
    liked_paper_ids = {f.paper_id for f in current_user.favorites}
    for paper in papers:
        paper["is_liked"] = paper["paper_id"] in liked_paper_ids
    return papers


@router.get("/browse", response_model=List[PaperResponse])
def browse_papers(
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
):
    """Browse all papers (legacy Neo4j store)."""
    papers = get_all_papers(neo4j_session, limit)
    liked_paper_ids = {f.paper_id for f in current_user.favorites}
    for paper in papers:
        paper["is_liked"] = paper["paper_id"] in liked_paper_ids
    return papers


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_paper_recommendations(
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Legacy live-search recommendations (kept for backwards compatibility).
    The primary engine is now GET /api/recommendations (hybrid)."""
    return await get_recommendations(db, current_user, limit)


@router.get("/{paper_id}", response_model=PaperDetailResponse)
async def get_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paper details (Mongo corpus first, then external APIs)."""
    paper = await _get_local_or_external(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper["is_liked"] = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.paper_id == paper_id,
    ).first() is not None
    return paper


@router.post("/{paper_id}/view")
async def view_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
):
    """Track paper view"""
    paper_title = await _resolve_title(paper_id)

    existing_view = db.query(UserRecentView).filter(
        UserRecentView.user_id == current_user.id,
        UserRecentView.paper_id == paper_id,
    ).first()

    if existing_view:
        existing_view.viewed_at = datetime.now(timezone.utc)
    else:
        db.add(UserRecentView(user_id=current_user.id, paper_id=paper_id, paper_title=paper_title))
    db.commit()

    track_paper_view(neo4j_session, current_user.id, paper_id)
    return {"message": "View tracked"}


@router.post("/{paper_id}/like")
async def like_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
):
    """Like/save a paper"""
    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.paper_id == paper_id,
    ).first()
    if existing:
        return {"message": "Paper already liked", "is_liked": True}

    paper_title = await _resolve_title(paper_id)
    db.add(UserFavorite(user_id=current_user.id, paper_id=paper_id, paper_title=paper_title))
    db.commit()

    track_paper_like(neo4j_session, current_user.id, paper_id, True)
    return {"message": "Paper liked", "is_liked": True}


@router.delete("/{paper_id}/like")
def unlike_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session),
):
    """Unlike/unsave a paper"""
    favorite = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.paper_id == paper_id,
    ).first()
    if favorite:
        db.delete(favorite)
        db.commit()
    track_paper_like(neo4j_session, current_user.id, paper_id, False)
    return {"message": "Paper unliked", "is_liked": False}


@router.get("/me/favorites", response_model=List[UserFavoriteResponse])
def get_my_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's favorite papers"""
    return db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id
    ).order_by(UserFavorite.created_at.desc()).all()


@router.get("/me/recent-views", response_model=List[UserRecentViewResponse])
def get_my_recent_views(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's recently viewed papers"""
    return db.query(UserRecentView).filter(
        UserRecentView.user_id == current_user.id
    ).order_by(UserRecentView.viewed_at.desc()).limit(20).all()
