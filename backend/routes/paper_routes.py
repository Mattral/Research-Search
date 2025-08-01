from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from db.postgres import get_db
from db.neo4j import get_neo4j_session
from models.user_models import User, UserFavorite, UserRecentView
from schemas.paper_schemas import (
    PaperResponse, PaperDetailResponse, SearchQuery,
    RecommendationResponse, UserFavoriteResponse, UserRecentViewResponse
)
from services.auth_service import get_current_user
from services.paper_service import (
    search_papers, get_paper_by_id, get_all_papers,
    track_paper_view, track_paper_like
)
from services.recommendation_service import get_recommendations
from datetime import datetime, timezone
from neo4j import Session as Neo4jSession

router = APIRouter(prefix="/api/papers", tags=["Papers"])


@router.get("/search", response_model=List[PaperResponse])
def search(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session)
):
    """Search papers by title, author, or year"""
    papers = search_papers(neo4j_session, title, author, year, limit)
    
    # Get user's liked papers
    liked_paper_ids = {f.paper_id for f in current_user.favorites}
    
    # Mark liked papers
    for paper in papers:
        paper["is_liked"] = paper["paper_id"] in liked_paper_ids
    
    return papers


@router.get("/browse", response_model=List[PaperResponse])
def browse_papers(
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session)
):
    """Browse all papers (for discovery)"""
    papers = get_all_papers(neo4j_session, limit)
    
    # Get user's liked papers
    liked_paper_ids = {f.paper_id for f in current_user.favorites}
    
    # Mark liked papers
    for paper in papers:
        paper["is_liked"] = paper["paper_id"] in liked_paper_ids
    
    return papers


@router.get("/recommendations", response_model=List[RecommendationResponse])
def get_paper_recommendations(
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session)
):
    """Get personalized paper recommendations"""
    recommendations = get_recommendations(neo4j_session, db, current_user.id, limit)
    return recommendations


@router.get("/{paper_id}", response_model=PaperDetailResponse)
def get_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session)
):
    """Get paper details by ID"""
    paper = get_paper_by_id(neo4j_session, paper_id)
    
    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper not found"
        )
    
    # Check if paper is liked
    is_liked = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.paper_id == paper_id
    ).first() is not None
    
    paper["is_liked"] = is_liked
    
    return paper


@router.post("/{paper_id}/view")
def view_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session)
):
    """Track paper view"""
    # Get paper title from Neo4j
    paper = get_paper_by_id(neo4j_session, paper_id)
    paper_title = paper["title"] if paper else None
    
    # Track in PostgreSQL
    existing_view = db.query(UserRecentView).filter(
        UserRecentView.user_id == current_user.id,
        UserRecentView.paper_id == paper_id
    ).first()
    
    if existing_view:
        existing_view.viewed_at = datetime.now(timezone.utc)
    else:
        new_view = UserRecentView(
            user_id=current_user.id,
            paper_id=paper_id,
            paper_title=paper_title
        )
        db.add(new_view)
    
    db.commit()
    
    # Track in Neo4j
    track_paper_view(neo4j_session, current_user.id, paper_id)
    
    return {"message": "View tracked"}


@router.post("/{paper_id}/like")
def like_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session)
):
    """Like/save a paper"""
    # Check if already liked
    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.paper_id == paper_id
    ).first()
    
    if existing:
        return {"message": "Paper already liked", "is_liked": True}
    
    # Get paper title from Neo4j
    paper = get_paper_by_id(neo4j_session, paper_id)
    paper_title = paper["title"] if paper else None
    
    # Add to PostgreSQL
    favorite = UserFavorite(
        user_id=current_user.id,
        paper_id=paper_id,
        paper_title=paper_title
    )
    db.add(favorite)
    db.commit()
    
    # Track in Neo4j
    track_paper_like(neo4j_session, current_user.id, paper_id, True)
    
    return {"message": "Paper liked", "is_liked": True}


@router.delete("/{paper_id}/like")
def unlike_paper(
    paper_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    neo4j_session: Neo4jSession = Depends(get_neo4j_session)
):
    """Unlike/unsave a paper"""
    favorite = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.paper_id == paper_id
    ).first()
    
    if favorite:
        db.delete(favorite)
        db.commit()
    
    # Track in Neo4j
    track_paper_like(neo4j_session, current_user.id, paper_id, False)
    
    return {"message": "Paper unliked", "is_liked": False}


@router.get("/me/favorites", response_model=List[UserFavoriteResponse])
def get_my_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's favorite papers"""
    favorites = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id
    ).order_by(UserFavorite.created_at.desc()).all()
    return favorites


@router.get("/me/recent-views", response_model=List[UserRecentViewResponse])
def get_my_recent_views(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's recently viewed papers"""
    recent = db.query(UserRecentView).filter(
        UserRecentView.user_id == current_user.id
    ).order_by(UserRecentView.viewed_at.desc()).limit(20).all()
    return recent
