from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PaperBase(BaseModel):
    paper_id: str
    title: str
    abstract: Optional[str] = None
    year: Optional[int] = None
    authors: List[str] = []
    venue: Optional[str] = None
    citation_count: Optional[int] = 0
    url: Optional[str] = None


class PaperResponse(PaperBase):
    is_liked: bool = False
    
    class Config:
        from_attributes = True


class PaperDetailResponse(PaperBase):
    is_liked: bool = False
    references: List[str] = []
    cited_by: List[str] = []
    
    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    limit: int = 20


class RecommendationResponse(BaseModel):
    paper_id: str
    title: str
    score: float
    reason: str
    authors: List[str] = []
    year: Optional[int] = None
    venue: Optional[str] = None


class UserFavoriteResponse(BaseModel):
    id: int
    paper_id: str
    paper_title: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserRecentViewResponse(BaseModel):
    id: int
    paper_id: str
    paper_title: Optional[str]
    viewed_at: datetime
    
    class Config:
        from_attributes = True
