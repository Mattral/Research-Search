"""
arXiv API Service
Provides search, browse, and paper retrieval from the arXiv public API.
API Docs: https://info.arxiv.org/help/api/user-manual.html
"""
import httpx
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any
import logging
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)

ARXIV_API_BASE = "http://export.arxiv.org/api/query"

ARXIV_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}

ARXIV_CATEGORIES = {
    "cs.AI": "Artificial Intelligence",
    "cs.CL": "Computation and Language (NLP)",
    "cs.CV": "Computer Vision",
    "cs.LG": "Machine Learning",
    "cs.NE": "Neural and Evolutionary Computing",
    "cs.RO": "Robotics",
    "cs.CR": "Cryptography and Security",
    "cs.DB": "Databases",
    "cs.DS": "Data Structures and Algorithms",
    "cs.IR": "Information Retrieval",
    "cs.SE": "Software Engineering",
    "cs.HC": "Human-Computer Interaction",
    "stat.ML": "Machine Learning (Statistics)",
    "math.OC": "Optimization and Control",
    "physics.comp-ph": "Computational Physics",
    "q-bio.BM": "Biomolecules",
    "q-bio.GN": "Genomics",
    "q-bio.NC": "Neurons and Cognition",
    "q-fin.ST": "Statistical Finance",
    "econ.EM": "Econometrics",
    "eess.SP": "Signal Processing",
    "eess.IV": "Image and Video Processing",
    "astro-ph": "Astrophysics",
    "cond-mat": "Condensed Matter",
    "hep-ph": "High Energy Physics - Phenomenology",
    "quant-ph": "Quantum Physics",
    "math.NA": "Numerical Analysis",
    "math.ST": "Statistics Theory",
}


def _parse_entry(entry: ET.Element) -> Dict[str, Any]:
    """Parse a single Atom <entry> into a dict."""
    def text(tag, ns="atom"):
        el = entry.find(f"{ns}:{tag}", ARXIV_NS) if ns else entry.find(tag)
        return el.text.strip() if el is not None and el.text else None

    # Extract arXiv ID from the <id> URL
    raw_id = text("id") or ""
    arxiv_id = raw_id.replace("http://arxiv.org/abs/", "").replace("https://arxiv.org/abs/", "")

    # Authors
    authors = []
    for author_el in entry.findall("atom:author", ARXIV_NS):
        name_el = author_el.find("atom:name", ARXIV_NS)
        if name_el is not None and name_el.text:
            authors.append(name_el.text.strip())

    # Categories
    categories = []
    primary_category = None
    for cat_el in entry.findall("atom:category", ARXIV_NS):
        term = cat_el.get("term")
        if term:
            categories.append(term)
    pc_el = entry.find("arxiv:primary_category", ARXIV_NS)
    if pc_el is not None:
        primary_category = pc_el.get("term")

    # Links
    pdf_url = None
    abstract_url = None
    doi_url = None
    for link_el in entry.findall("atom:link", ARXIV_NS):
        rel = link_el.get("rel", "")
        title = link_el.get("title", "")
        href = link_el.get("href", "")
        if rel == "alternate":
            abstract_url = href
        elif title == "pdf":
            pdf_url = href
        elif title == "doi":
            doi_url = href

    # Published / updated
    published = text("published")
    updated = text("updated")

    # Year extraction
    year = None
    if published:
        match = re.search(r"(\d{4})", published)
        if match:
            year = int(match.group(1))

    # Extension elements
    comment = text("comment", "arxiv")
    journal_ref = text("journal_ref", "arxiv")
    doi = text("doi", "arxiv")

    summary = text("summary") or ""
    summary = re.sub(r"\s+", " ", summary).strip()

    title = text("title") or ""
    title = re.sub(r"\s+", " ", title).strip()

    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "summary": summary,
        "authors": authors,
        "categories": categories,
        "primary_category": primary_category,
        "published": published,
        "updated": updated,
        "year": year,
        "pdf_url": pdf_url,
        "abstract_url": abstract_url,
        "doi_url": doi_url,
        "doi": doi,
        "comment": comment,
        "journal_ref": journal_ref,
    }


def _parse_feed(xml_text: str) -> Dict[str, Any]:
    """Parse the full Atom feed response."""
    root = ET.fromstring(xml_text)
    total_el = root.find("opensearch:totalResults", ARXIV_NS)
    total_results = int(total_el.text) if total_el is not None and total_el.text else 0

    start_el = root.find("opensearch:startIndex", ARXIV_NS)
    start_index = int(start_el.text) if start_el is not None and start_el.text else 0

    entries = root.findall("atom:entry", ARXIV_NS)
    papers = []
    for entry in entries:
        parsed = _parse_entry(entry)
        # Skip error entries
        if parsed["title"] == "Error":
            continue
        papers.append(parsed)

    return {
        "total_results": total_results,
        "start_index": start_index,
        "papers": papers,
    }


async def search_arxiv(
    query: str,
    search_field: str = "all",
    category: Optional[str] = None,
    start: int = 0,
    max_results: int = 20,
    sort_by: str = "relevance",
    sort_order: str = "descending",
) -> Dict[str, Any]:
    """
    Search arXiv papers.
    search_field: all, ti, au, abs, cat
    sort_by: relevance, lastUpdatedDate, submittedDate
    sort_order: ascending, descending
    """
    search_parts = []
    if query:
        search_parts.append(f"{search_field}:{quote(query)}")
    if category:
        search_parts.append(f"cat:{category}")

    search_query = "+AND+".join(search_parts) if search_parts else "all:*"

    params = {
        "search_query": search_query,
        "start": start,
        "max_results": min(max_results, 100),
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(ARXIV_API_BASE, params=params)
            resp.raise_for_status()
            return _parse_feed(resp.text)
    except Exception as e:
        logger.error(f"arXiv search error: {e}")
        return {"total_results": 0, "start_index": 0, "papers": []}


async def get_arxiv_paper(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """Get a single paper by arXiv ID."""
    params = {"id_list": arxiv_id}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(ARXIV_API_BASE, params=params)
            resp.raise_for_status()
            result = _parse_feed(resp.text)
            if result["papers"]:
                return result["papers"][0]
            return None
    except Exception as e:
        logger.error(f"arXiv paper fetch error: {e}")
        return None


async def get_latest_papers(
    category: str = "cs.AI",
    max_results: int = 20,
) -> Dict[str, Any]:
    """Get latest papers in a category."""
    return await search_arxiv(
        query="",
        category=category,
        max_results=max_results,
        sort_by="submittedDate",
        sort_order="descending",
    )


def get_categories() -> List[Dict[str, str]]:
    """Return list of supported arXiv categories."""
    return [
        {"code": code, "name": name}
        for code, name in sorted(ARXIV_CATEGORIES.items(), key=lambda x: x[1])
    ]
