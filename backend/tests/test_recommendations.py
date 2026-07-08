"""Backend tests for hybrid recommendation engine (Re-Search)."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # Fallback: read frontend/.env
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")

EMAIL = "researcher@test.com"
PASSWORD = "Test1234!"


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def token(api):
    # Try login; if fails, register then login
    r = api.post(f"{BASE_URL}/api/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=30)
    if r.status_code != 200:
        api.post(f"{BASE_URL}/api/auth/register",
                 json={"email": EMAIL, "username": "researcher", "password": PASSWORD, "full_name": "Test Researcher"},
                 timeout=30)
        r = api.post(f"{BASE_URL}/api/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=30)
    assert r.status_code == 200, f"Login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ---------------- health & status ----------------
def test_health(api):
    r = api.get(f"{BASE_URL}/api/health", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d.get("status") == "healthy"
    assert d.get("recommendation_engine") == "hybrid"
    assert "embedding_backend" in d
    assert d.get("corpus_size", 0) > 0


def test_status_requires_auth(api):
    r = api.get(f"{BASE_URL}/api/recommendations/status", timeout=30)
    assert r.status_code in (401, 403)


def test_status_authed(api, auth_headers):
    r = api.get(f"{BASE_URL}/api/recommendations/status", headers=auth_headers, timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d.get("engine") == "hybrid"
    assert d.get("corpus_size", 0) > 0
    assert "embedding_backend" in d
    assert "seed_backend" in d


# ---------------- recommendations ----------------
def test_recommendations_requires_auth(api):
    r = api.get(f"{BASE_URL}/api/recommendations", timeout=30)
    assert r.status_code in (401, 403)


def test_recommendations_shape(api, auth_headers):
    r = api.get(f"{BASE_URL}/api/recommendations?limit=15", headers=auth_headers, timeout=60)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) > 0, "expected non-empty recommendations for AI/ML interests user"
    for it in items[:5]:
        assert isinstance(it.get("paper_id"), str) and it["paper_id"]
        assert isinstance(it.get("title"), str) and it["title"]
        assert 0.0 <= float(it["score"]) <= 1.0
        assert isinstance(it["reasons"], list) and len(it["reasons"]) > 0
        assert "match_type" in it
        assert isinstance(it.get("authors", []), list)
        assert "year" in it
        assert "source" in it
        assert "citation_count" in it


def test_recommendations_semantic_relevance(api, auth_headers):
    r = api.get(f"{BASE_URL}/api/recommendations?limit=15", headers=auth_headers, timeout=60)
    assert r.status_code == 200
    items = r.json()
    # Look for AI/ML relevance across reasons + fields + titles.
    blob = " ".join(
        (it.get("title", "") + " " + " ".join(it.get("reasons", [])) + " " +
         " ".join(it.get("fields_of_study", []) or []))
        for it in items
    ).lower()
    ai_terms = ["artificial intelligence", "machine learning", "learning", "neural", "deep",
                "semantic", "computer science", "in your field"]
    hits = sum(1 for t in ai_terms if t in blob)
    assert hits >= 2, f"expected AI/ML relevance signals, got hits={hits}, blob head={blob[:400]}"


# ---------------- trending ----------------
def test_trending(api, auth_headers):
    r = api.get(f"{BASE_URL}/api/recommendations/trending?limit=10", headers=auth_headers, timeout=60)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list) and len(items) > 0
    for it in items:
        assert it["match_type"] == "trending"
    # popularity-ordered (non-increasing) by citation_count
    cites = [it.get("citation_count") or 0 for it in items]
    assert cites == sorted(cites, reverse=True), f"trending not popularity-ordered: {cites}"


# ---------------- feedback ----------------
def test_feedback_up_down_and_invalid(api, auth_headers):
    # need a paper_id from recs
    r = api.get(f"{BASE_URL}/api/recommendations?limit=3", headers=auth_headers, timeout=60)
    assert r.status_code == 200 and r.json(), "no recs to use for feedback"
    pid = r.json()[0]["paper_id"]

    up = api.post(f"{BASE_URL}/api/recommendations/feedback",
                  json={"paper_id": pid, "feedback": "up"}, headers=auth_headers, timeout=30)
    assert up.status_code == 200
    assert up.json().get("feedback") == "up"

    down = api.post(f"{BASE_URL}/api/recommendations/feedback",
                    json={"paper_id": pid, "feedback": "down"}, headers=auth_headers, timeout=30)
    assert down.status_code == 200
    assert down.json().get("feedback") == "down"

    bad = api.post(f"{BASE_URL}/api/recommendations/feedback",
                   json={"paper_id": pid, "feedback": "nope"}, headers=auth_headers, timeout=30)
    assert bad.status_code == 400


# ---------------- paper detail resolution ----------------
def test_paper_detail_resolves_for_rec_paper(api, auth_headers):
    r = api.get(f"{BASE_URL}/api/recommendations?limit=5", headers=auth_headers, timeout=60)
    assert r.status_code == 200 and r.json()
    pid = r.json()[0]["paper_id"]
    # url-quote path segment
    from urllib.parse import quote
    detail = api.get(f"{BASE_URL}/api/papers/{quote(pid, safe='')}", headers=auth_headers, timeout=60)
    assert detail.status_code == 200, f"paper detail failed for {pid}: {detail.status_code} {detail.text[:200]}"
    d = detail.json()
    assert d.get("title")
    assert isinstance(d.get("authors", []), list)
    # abstract may be present or empty; year may be None sometimes but usually set for seeded papers
    assert "abstract" in d
    assert "year" in d
