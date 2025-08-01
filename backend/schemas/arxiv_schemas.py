from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ArxivSearchParams(BaseModel):
    query: str = ""
    search_field: str = "all"
    category: Optional[str] = None
    start: int = 0
    max_results: int = 20
    sort_by: str = "relevance"
    sort_order: str = "descending"


class ArxivPaperResponse(BaseModel):
    arxiv_id: str
    title: str
    summary: Optional[str] = None
    authors: List[str] = []
    categories: List[str] = []
    primary_category: Optional[str] = None
    published: Optional[str] = None
    updated: Optional[str] = None
    year: Optional[int] = None
    pdf_url: Optional[str] = None
    abstract_url: Optional[str] = None
    doi_url: Optional[str] = None
    doi: Optional[str] = None
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    is_saved: bool = False


class ArxivSearchResponse(BaseModel):
    total_results: int
    start_index: int
    papers: List[ArxivPaperResponse]


class ArxivCategoryResponse(BaseModel):
    code: str
    name: str


class AISummaryRequest(BaseModel):
    title: str
    abstract: str
    authors: List[str] = []


class AISummaryResponse(BaseModel):
    summary: str
    key_points: List[str] = []
    significance: str = ""


class SavedPaperCreate(BaseModel):
    arxiv_id: str
    title: str
    authors: List[str] = []
    summary: Optional[str] = None
    primary_category: Optional[str] = None
    published: Optional[str] = None
    pdf_url: Optional[str] = None


class SavedPaperResponse(BaseModel):
    id: int
    arxiv_id: str
    title: str
    authors_str: Optional[str] = None
    summary: Optional[str] = None
    primary_category: Optional[str] = None
    published: Optional[str] = None
    pdf_url: Optional[str] = None
    saved_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True
