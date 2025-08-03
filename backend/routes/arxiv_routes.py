from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from db.postgres import get_db
from models.user_models import User, SavedArxivPaper
from schemas.arxiv_schemas import (
    ArxivSearchResponse, ArxivPaperResponse, ArxivCategoryResponse,
    AISummaryRequest, AISummaryResponse, SavedPaperCreate, SavedPaperResponse
)
from services.arxiv_service import search_arxiv, get_arxiv_paper, get_latest_papers, get_categories
from services.ai_service import summarize_paper
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/arxiv", tags=["arXiv"])


@router.get("/search", response_model=ArxivSearchResponse)
async def search(
    query: str = Query("", description="Search query"),
    search_field: str = Query("all", description="Field to search: all, ti, au, abs, cat"),
    category: Optional[str] = Query(None, description="arXiv category filter"),
    start: int = Query(0, ge=0),
    max_results: int = Query(20, ge=1, le=100),
    sort_by: str = Query("relevance", description="Sort by: relevance, lastUpdatedDate, submittedDate"),
    sort_order: str = Query("descending"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search arXiv papers with filters."""
    result = await search_arxiv(
        query=query,
        search_field=search_field,
        category=category,
        start=start,
        max_results=max_results,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    # Mark saved papers
    saved_ids = {s.arxiv_id for s in db.query(SavedArxivPaper).filter(
        SavedArxivPaper.user_id == current_user.id
    ).all()}

    for paper in result["papers"]:
        paper["is_saved"] = paper["arxiv_id"] in saved_ids

    return result


@router.get("/categories", response_model=List[ArxivCategoryResponse])
async def list_categories(current_user: User = Depends(get_current_user)):
    """List all supported arXiv categories."""
    return get_categories()


@router.get("/latest", response_model=ArxivSearchResponse)
async def latest_papers(
    category: str = Query("cs.AI", description="arXiv category"),
    max_results: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get latest papers in a category."""
    result = await get_latest_papers(category=category, max_results=max_results)

    saved_ids = {s.arxiv_id for s in db.query(SavedArxivPaper).filter(
        SavedArxivPaper.user_id == current_user.id
    ).all()}

    for paper in result["papers"]:
        paper["is_saved"] = paper["arxiv_id"] in saved_ids

    return result


@router.get("/paper/{arxiv_id:path}", response_model=ArxivPaperResponse)
async def get_paper(
    arxiv_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single arXiv paper by ID."""
    paper = await get_arxiv_paper(arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found on arXiv")

    is_saved = db.query(SavedArxivPaper).filter(
        SavedArxivPaper.user_id == current_user.id,
        SavedArxivPaper.arxiv_id == arxiv_id,
    ).first() is not None

    paper["is_saved"] = is_saved
    return paper


@router.post("/summarize", response_model=AISummaryResponse)
async def ai_summarize(
    data: AISummaryRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate AI summary for a paper using Gemini."""
    result = await summarize_paper(
        title=data.title,
        abstract=data.abstract,
        authors=data.authors,
    )
    return result


@router.post("/save", response_model=SavedPaperResponse)
async def save_paper(
    data: SavedPaperCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save an arXiv paper to reading list."""
    existing = db.query(SavedArxivPaper).filter(
        SavedArxivPaper.user_id == current_user.id,
        SavedArxivPaper.arxiv_id == data.arxiv_id,
    ).first()

    if existing:
        return existing

    saved = SavedArxivPaper(
        user_id=current_user.id,
        arxiv_id=data.arxiv_id,
        title=data.title,
        authors_str=", ".join(data.authors[:10]),
        summary=data.summary,
        primary_category=data.primary_category,
        published=data.published,
        pdf_url=data.pdf_url,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.delete("/save/{arxiv_id:path}")
async def unsave_paper(
    arxiv_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a paper from reading list."""
    saved = db.query(SavedArxivPaper).filter(
        SavedArxivPaper.user_id == current_user.id,
        SavedArxivPaper.arxiv_id == arxiv_id,
    ).first()

    if saved:
        db.delete(saved)
        db.commit()

    return {"message": "Paper removed from reading list"}


@router.get("/reading-list", response_model=List[SavedPaperResponse])
async def get_reading_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's saved arXiv papers."""
    papers = db.query(SavedArxivPaper).filter(
        SavedArxivPaper.user_id == current_user.id
    ).order_by(SavedArxivPaper.saved_at.desc()).all()
    return papers
