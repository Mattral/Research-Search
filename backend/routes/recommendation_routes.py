from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone

from db.postgres import get_db
from db.mongo import feedback_collection, papers_collection, meta_collection
from models.user_models import User
from services.auth_service import get_current_user
from services.hybrid_recommendation_service import get_hybrid_recommendations, get_trending
from services.embedding_service import active_backend

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


class RecommendationItem(BaseModel):
    paper_id: str
    title: str
    score: float
    reasons: List[str] = []
    match_type: str = "hybrid"
    authors: List[str] = []
    year: Optional[int] = None
    venue: Optional[str] = None
    abstract: Optional[str] = ""
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    doi: Optional[str] = None
    source: Optional[str] = None
    citation_count: int = 0
    fields_of_study: List[str] = []


class FeedbackRequest(BaseModel):
    paper_id: str
    feedback: str  # "up" | "down"
    reason: Optional[str] = None


@router.get("", response_model=List[RecommendationItem])
@router.get("/", response_model=List[RecommendationItem], include_in_schema=False)
async def recommendations(
    limit: int = Query(12, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Personalized hybrid recommendations (semantic + collaborative + popularity)."""
    return await get_hybrid_recommendations(db, current_user, limit)


@router.get("/trending", response_model=List[RecommendationItem])
async def trending(
    limit: int = Query(12, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Popularity-based fallback recommendations."""
    return await get_trending(db, current_user, limit)


@router.post("/feedback")
async def submit_feedback(
    data: FeedbackRequest,
    current_user: User = Depends(get_current_user),
):
    """Record thumbs up/down on a recommendation to improve future results."""
    if data.feedback not in ("up", "down"):
        raise HTTPException(status_code=400, detail="feedback must be 'up' or 'down'")
    await feedback_collection.update_one(
        {"user_id": current_user.id, "paper_id": data.paper_id},
        {"$set": {
            "user_id": current_user.id,
            "paper_id": data.paper_id,
            "feedback": data.feedback,
            "reason": data.reason,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )
    return {"message": "Feedback recorded", "paper_id": data.paper_id, "feedback": data.feedback}


@router.get("/status")
async def status(current_user: User = Depends(get_current_user)):
    """Diagnostics for the recommendation engine."""
    count = await papers_collection.count_documents({})
    meta = await meta_collection.find_one({"_id": "papers"}) or {}
    return {
        "engine": "hybrid",
        "embedding_backend": active_backend(),
        "corpus_size": count,
        "seed_backend": meta.get("embedding_backend"),
        "seeded_at": meta.get("seeded_at"),
    }
