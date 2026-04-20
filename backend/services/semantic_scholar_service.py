"""
Semantic Scholar API Service
Free academic search API - no key required for basic search.
Docs: https://api.semanticscholar.org/
"""
import httpx
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

SS_API = "https://api.semanticscholar.org/graph/v1"


async def search_semantic_scholar(
    query: str,
    limit: int = 20,
    offset: int = 0,
    year: Optional[str] = None,
    fields_of_study: Optional[str] = None,
) -> Dict[str, Any]:
    """Search Semantic Scholar papers."""
    params = {
        "query": query,
        "limit": min(limit, 100),
        "offset": offset,
        "fields": "paperId,title,abstract,authors,year,citationCount,url,externalIds,publicationTypes,journal,fieldsOfStudy,openAccessPdf",
    }
    if year:
        params["year"] = year
    if fields_of_study:
        params["fieldsOfStudy"] = fields_of_study

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{SS_API}/paper/search", params=params)
            resp.raise_for_status()
            data = resp.json()

            papers = []
            for p in data.get("data", []):
                authors = [a.get("name", "") for a in (p.get("authors") or [])]
                pdf_url = None
                if p.get("openAccessPdf"):
                    pdf_url = p["openAccessPdf"].get("url")
                doi = (p.get("externalIds") or {}).get("DOI")

                papers.append({
                    "source": "semantic_scholar",
                    "source_id": p.get("paperId", ""),
                    "title": p.get("title", ""),
                    "abstract": p.get("abstract") or "",
                    "authors": authors,
                    "year": p.get("year"),
                    "citation_count": p.get("citationCount", 0),
                    "url": p.get("url", ""),
                    "pdf_url": pdf_url,
                    "doi": doi,
                    "journal": (p.get("journal") or {}).get("name"),
                    "fields_of_study": p.get("fieldsOfStudy") or [],
                })

            return {
                "total": data.get("total", 0),
                "offset": data.get("offset", 0),
                "papers": papers,
            }
    except Exception as e:
        logger.error(f"Semantic Scholar search error: {e}")
        return {"total": 0, "offset": 0, "papers": []}


async def get_paper_details(paper_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed paper info from Semantic Scholar."""
    fields = "paperId,title,abstract,authors,year,citationCount,referenceCount,url,externalIds,journal,fieldsOfStudy,openAccessPdf,citations.paperId,citations.title,citations.year,references.paperId,references.title,references.year"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{SS_API}/paper/{paper_id}", params={"fields": fields})
            resp.raise_for_status()
            p = resp.json()

            authors = [a.get("name", "") for a in (p.get("authors") or [])]
            pdf_url = None
            if p.get("openAccessPdf"):
                pdf_url = p["openAccessPdf"].get("url")

            citations = [{"id": c["paperId"], "title": c.get("title", ""), "year": c.get("year")} for c in (p.get("citations") or [])[:20] if c.get("paperId")]
            references = [{"id": r["paperId"], "title": r.get("title", ""), "year": r.get("year")} for r in (p.get("references") or [])[:20] if r.get("paperId")]

            return {
                "source": "semantic_scholar",
                "source_id": p.get("paperId", ""),
                "title": p.get("title", ""),
                "abstract": p.get("abstract") or "",
                "authors": authors,
                "year": p.get("year"),
                "citation_count": p.get("citationCount", 0),
                "reference_count": p.get("referenceCount", 0),
                "url": p.get("url", ""),
                "pdf_url": pdf_url,
                "doi": (p.get("externalIds") or {}).get("DOI"),
                "journal": (p.get("journal") or {}).get("name"),
                "fields_of_study": p.get("fieldsOfStudy") or [],
                "citations": citations,
                "references": references,
            }
    except Exception as e:
        logger.error(f"Semantic Scholar detail error: {e}")
        return None
