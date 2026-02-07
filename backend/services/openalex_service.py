"""
OpenAlex API Service
Free open-access academic data API.
Docs: https://docs.openalex.org/
"""
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

OA_API = "https://api.openalex.org"


async def search_openalex(
    query: str,
    limit: int = 20,
    page: int = 1,
    from_year: Optional[int] = None,
    to_year: Optional[int] = None,
    sort: str = "relevance_score:desc",
) -> Dict[str, Any]:
    """Search OpenAlex works."""
    params = {
        "search": query,
        "per_page": min(limit, 50),
        "page": page,
        "sort": sort,
        "mailto": "research-search@example.com",
    }
    filters = []
    if from_year:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if to_year:
        filters.append(f"to_publication_date:{to_year}-12-31")
    if filters:
        params["filter"] = ",".join(filters)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{OA_API}/works", params=params)
            resp.raise_for_status()
            data = resp.json()

            papers = []
            for w in data.get("results", []):
                authors = []
                for a in (w.get("authorships") or [])[:10]:
                    name = (a.get("author") or {}).get("display_name", "")
                    if name:
                        authors.append(name)

                abstract = ""
                inv = w.get("abstract_inverted_index")
                if inv:
                    words = {}
                    for word, positions in inv.items():
                        for pos in positions:
                            words[pos] = word
                    abstract = " ".join(words[k] for k in sorted(words.keys()))

                pdf_url = None
                oa_info = w.get("open_access") or {}
                if oa_info.get("oa_url"):
                    pdf_url = oa_info["oa_url"]

                papers.append({
                    "source": "openalex",
                    "source_id": (w.get("id") or "").replace("https://openalex.org/", ""),
                    "title": w.get("display_name") or w.get("title") or "",
                    "abstract": abstract[:2000],
                    "authors": authors,
                    "year": w.get("publication_year"),
                    "citation_count": w.get("cited_by_count", 0),
                    "url": w.get("id", ""),
                    "pdf_url": pdf_url,
                    "doi": (w.get("doi") or "").replace("https://doi.org/", "") if w.get("doi") else None,
                    "journal": (w.get("primary_location") or {}).get("source", {}).get("display_name") if w.get("primary_location") else None,
                    "fields_of_study": [c.get("display_name", "") for c in (w.get("concepts") or [])[:5]],
                })

            total = data.get("meta", {}).get("count", 0)
            return {"total": total, "page": page, "papers": papers}
    except Exception as e:
        logger.error(f"OpenAlex search error: {e}")
        return {"total": 0, "page": 1, "papers": []}
