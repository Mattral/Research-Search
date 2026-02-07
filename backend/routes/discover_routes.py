from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from db.postgres import get_db
from models.user_models import User, Workspace, WorkspacePaper
from services.auth_service import get_current_user
from services.semantic_scholar_service import search_semantic_scholar, get_paper_details
from services.openalex_service import search_openalex
from services.arxiv_service import search_arxiv
from services.ai_service import summarize_paper
from pydantic import BaseModel
from datetime import datetime, timezone
import asyncio

router = APIRouter(prefix="/api/discover", tags=["Discover"])


# --- Schemas ---

class UnifiedPaper(BaseModel):
    source: str
    source_id: str
    title: str
    abstract: Optional[str] = ""
    authors: List[str] = []
    year: Optional[int] = None
    citation_count: int = 0
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    fields_of_study: List[str] = []


class MultiSearchResponse(BaseModel):
    query: str
    sources_searched: List[str]
    total_results: int
    papers: List[UnifiedPaper]


class CompareRequest(BaseModel):
    papers: List[dict]


class CompareResult(BaseModel):
    papers: List[dict]
    comparison_matrix: dict


class TrendDataPoint(BaseModel):
    year: int
    count: int


class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = ""


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class WorkspacePaperAdd(BaseModel):
    source: str
    source_id: str
    title: str
    authors_str: Optional[str] = ""
    abstract: Optional[str] = ""
    year: Optional[int] = None
    pdf_url: Optional[str] = None
    doi: Optional[str] = None


class AnnotationUpdate(BaseModel):
    notes: Optional[str] = None
    tags: Optional[str] = None
    highlight: Optional[str] = None


class ExportRequest(BaseModel):
    paper_ids: List[int] = []
    format: str = "bibtex"


# --- Multi-Source Search ---

@router.get("/search", response_model=MultiSearchResponse)
async def multi_search(
    query: str = Query(..., min_length=1),
    sources: str = Query("arxiv,semantic_scholar,openalex", description="Comma-separated sources"),
    limit: int = Query(10, ge=1, le=30),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    sort: str = Query("relevance"),
    current_user: User = Depends(get_current_user),
):
    """Search across multiple research databases simultaneously."""
    source_list = [s.strip() for s in sources.split(",")]
    tasks = []

    if "arxiv" in source_list:
        tasks.append(("arxiv", _search_arxiv_unified(query, limit)))
    if "semantic_scholar" in source_list:
        year_filter = None
        if year_from and year_to:
            year_filter = f"{year_from}-{year_to}"
        elif year_from:
            year_filter = f"{year_from}-"
        tasks.append(("semantic_scholar", search_semantic_scholar(query, limit=limit, year=year_filter)))
    if "openalex" in source_list:
        tasks.append(("openalex", search_openalex(query, limit=limit, from_year=year_from, to_year=year_to)))

    results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)

    all_papers = []
    sources_searched = []
    total = 0

    for i, (src_name, _) in enumerate(tasks):
        res = results[i]
        if isinstance(res, Exception):
            continue
        sources_searched.append(src_name)
        total += res.get("total", res.get("total_results", 0))
        for p in res.get("papers", []):
            all_papers.append(p)

    # Sort by citation count if available and sort=citations
    if sort == "citations":
        all_papers.sort(key=lambda x: x.get("citation_count", 0), reverse=True)
    elif sort == "year":
        all_papers.sort(key=lambda x: x.get("year") or 0, reverse=True)

    return {
        "query": query,
        "sources_searched": sources_searched,
        "total_results": total,
        "papers": all_papers[:limit * len(source_list)],
    }


async def _search_arxiv_unified(query: str, limit: int) -> dict:
    result = await search_arxiv(query=query, max_results=limit)
    papers = []
    for p in result.get("papers", []):
        papers.append({
            "source": "arxiv",
            "source_id": p["arxiv_id"],
            "title": p["title"],
            "abstract": p.get("summary", ""),
            "authors": p.get("authors", []),
            "year": p.get("year"),
            "citation_count": 0,
            "url": p.get("abstract_url", ""),
            "pdf_url": p.get("pdf_url"),
            "doi": p.get("doi"),
            "journal": p.get("journal_ref"),
            "fields_of_study": p.get("categories", []),
        })
    return {"total": result.get("total_results", 0), "papers": papers}


# --- Paper Comparison ---

@router.post("/compare")
async def compare_papers(
    data: CompareRequest,
    current_user: User = Depends(get_current_user),
):
    """Compare multiple papers side-by-side. Generates AI comparison if 2-5 papers provided."""
    if len(data.papers) < 2 or len(data.papers) > 5:
        raise HTTPException(status_code=400, detail="Provide 2-5 papers for comparison")

    # Build comparison matrix
    matrix = {
        "titles": [],
        "authors": [],
        "years": [],
        "citations": [],
        "sources": [],
        "journals": [],
        "fields": [],
        "has_pdf": [],
    }

    for p in data.papers:
        matrix["titles"].append(p.get("title", ""))
        matrix["authors"].append(", ".join(p.get("authors", [])[:3]))
        matrix["years"].append(p.get("year"))
        matrix["citations"].append(p.get("citation_count", 0))
        matrix["sources"].append(p.get("source", ""))
        matrix["journals"].append(p.get("journal") or "N/A")
        matrix["fields"].append(", ".join(p.get("fields_of_study", [])[:3]) or "N/A")
        matrix["has_pdf"].append(bool(p.get("pdf_url")))

    # AI comparison
    ai_comparison = None
    try:
        combined = "\n\n".join([
            f"Paper {i+1}: {p.get('title', '')}\nAbstract: {(p.get('abstract') or '')[:300]}"
            for i, p in enumerate(data.papers)
        ])
        from services.ai_service import summarize_paper
        prompt_title = f"Comparison of {len(data.papers)} papers"
        prompt_abstract = f"Compare these papers:\n{combined}\n\nProvide: 1) How they differ in approach 2) Common themes 3) Which is most impactful and why"
        ai_comparison = await summarize_paper(prompt_title, prompt_abstract)
    except Exception:
        pass

    return {
        "papers": data.papers,
        "comparison_matrix": matrix,
        "ai_comparison": ai_comparison,
    }


# --- Trend Analysis ---

@router.get("/trends")
async def get_trends(
    query: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
):
    """Get publication trend data for a query across years."""
    year_counts = {}
    current_year = datetime.now().year

    # Search across recent years
    tasks = []
    for yr in range(current_year - 9, current_year + 1):
        tasks.append((yr, search_openalex(query, limit=1, from_year=yr, to_year=yr)))

    results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)

    trend_data = []
    for i, (yr, _) in enumerate(tasks):
        res = results[i]
        if isinstance(res, Exception):
            trend_data.append({"year": yr, "count": 0})
        else:
            trend_data.append({"year": yr, "count": res.get("total", 0)})

    return {"query": query, "trend_data": trend_data}


# --- Workspaces ---

@router.post("/workspaces")
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = Workspace(user_id=current_user.id, name=data.name, description=data.description or "")
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return _workspace_to_dict(ws)


@router.get("/workspaces")
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wss = db.query(Workspace).filter(Workspace.user_id == current_user.id).order_by(Workspace.updated_at.desc()).all()
    return [_workspace_to_dict(w) for w in wss]


@router.get("/workspaces/{ws_id}")
async def get_workspace(
    ws_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = db.query(Workspace).filter(Workspace.id == ws_id, Workspace.user_id == current_user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    papers = db.query(WorkspacePaper).filter(WorkspacePaper.workspace_id == ws_id).order_by(WorkspacePaper.added_at.desc()).all()
    return {**_workspace_to_dict(ws), "papers": [_wp_to_dict(p) for p in papers]}


@router.put("/workspaces/{ws_id}")
async def update_workspace(
    ws_id: int,
    data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = db.query(Workspace).filter(Workspace.id == ws_id, Workspace.user_id == current_user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if data.name is not None:
        ws.name = data.name
    if data.description is not None:
        ws.description = data.description
    ws.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ws)
    return _workspace_to_dict(ws)


@router.delete("/workspaces/{ws_id}")
async def delete_workspace(
    ws_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = db.query(Workspace).filter(Workspace.id == ws_id, Workspace.user_id == current_user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    db.query(WorkspacePaper).filter(WorkspacePaper.workspace_id == ws_id).delete()
    db.delete(ws)
    db.commit()
    return {"message": "Workspace deleted"}


@router.post("/workspaces/{ws_id}/papers")
async def add_paper_to_workspace(
    ws_id: int,
    data: WorkspacePaperAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = db.query(Workspace).filter(Workspace.id == ws_id, Workspace.user_id == current_user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")

    existing = db.query(WorkspacePaper).filter(
        WorkspacePaper.workspace_id == ws_id,
        WorkspacePaper.source_id == data.source_id,
        WorkspacePaper.source == data.source,
    ).first()
    if existing:
        return _wp_to_dict(existing)

    wp = WorkspacePaper(
        workspace_id=ws_id, source=data.source, source_id=data.source_id,
        title=data.title, authors_str=data.authors_str, abstract=data.abstract,
        year=data.year, pdf_url=data.pdf_url, doi=data.doi,
    )
    db.add(wp)
    ws.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(wp)
    return _wp_to_dict(wp)


@router.delete("/workspaces/{ws_id}/papers/{paper_id}")
async def remove_paper_from_workspace(
    ws_id: int,
    paper_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = db.query(Workspace).filter(Workspace.id == ws_id, Workspace.user_id == current_user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    wp = db.query(WorkspacePaper).filter(WorkspacePaper.id == paper_id, WorkspacePaper.workspace_id == ws_id).first()
    if wp:
        db.delete(wp)
        db.commit()
    return {"message": "Paper removed"}


@router.put("/workspaces/{ws_id}/papers/{paper_id}/annotate")
async def annotate_paper(
    ws_id: int,
    paper_id: int,
    data: AnnotationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = db.query(Workspace).filter(Workspace.id == ws_id, Workspace.user_id == current_user.id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    wp = db.query(WorkspacePaper).filter(WorkspacePaper.id == paper_id, WorkspacePaper.workspace_id == ws_id).first()
    if not wp:
        raise HTTPException(status_code=404, detail="Paper not found in workspace")
    if data.notes is not None:
        wp.notes = data.notes
    if data.tags is not None:
        wp.tags = data.tags
    if data.highlight is not None:
        wp.highlight = data.highlight
    db.commit()
    db.refresh(wp)
    return _wp_to_dict(wp)


# --- Export ---

@router.post("/export")
async def export_papers(
    data: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export papers as BibTeX or Markdown."""
    papers = db.query(WorkspacePaper).filter(WorkspacePaper.id.in_(data.paper_ids)).all()
    if not papers:
        raise HTTPException(status_code=404, detail="No papers found")

    if data.format == "bibtex":
        entries = []
        for p in papers:
            first_author = (p.authors_str or "unknown").split(",")[0].strip().split()[-1].lower()
            key = f"{first_author}{p.year or ''}"
            entry = f"@article{{{key},\n  title={{{p.title}}},\n  author={{{p.authors_str or 'Unknown'}}},\n  year={{{p.year or ''}}}"
            if p.doi:
                entry += f",\n  doi={{{p.doi}}}"
            entry += "\n}"
            entries.append(entry)
        return {"format": "bibtex", "content": "\n\n".join(entries)}

    elif data.format == "markdown":
        lines = ["# Research Export\n"]
        for i, p in enumerate(papers, 1):
            lines.append(f"## {i}. {p.title}\n")
            if p.authors_str:
                lines.append(f"**Authors:** {p.authors_str}\n")
            if p.year:
                lines.append(f"**Year:** {p.year}\n")
            if p.doi:
                lines.append(f"**DOI:** {p.doi}\n")
            if p.abstract:
                lines.append(f"\n{p.abstract[:500]}\n")
            if p.notes:
                lines.append(f"\n> **Notes:** {p.notes}\n")
            lines.append("---\n")
        return {"format": "markdown", "content": "\n".join(lines)}

    raise HTTPException(status_code=400, detail="Unsupported format. Use 'bibtex' or 'markdown'.")


def _workspace_to_dict(ws):
    return {
        "id": ws.id, "name": ws.name, "description": ws.description,
        "created_at": ws.created_at.isoformat() if ws.created_at else None,
        "updated_at": ws.updated_at.isoformat() if ws.updated_at else None,
    }


def _wp_to_dict(wp):
    return {
        "id": wp.id, "workspace_id": wp.workspace_id, "source": wp.source,
        "source_id": wp.source_id, "title": wp.title, "authors_str": wp.authors_str,
        "abstract": wp.abstract, "year": wp.year, "pdf_url": wp.pdf_url, "doi": wp.doi,
        "notes": wp.notes, "tags": wp.tags, "highlight": wp.highlight,
        "added_at": wp.added_at.isoformat() if wp.added_at else None,
    }
