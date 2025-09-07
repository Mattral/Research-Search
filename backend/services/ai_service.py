"""
AI Service - Gemini-powered paper summarization and insights.
"""
import os
import logging
from google import genai
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


async def summarize_paper(title: str, abstract: str, authors: list = None) -> dict:
    """Generate an AI summary of a research paper."""
    if not client:
        return {"summary": "AI summarization unavailable. Gemini API key not configured.", "key_points": [], "significance": ""}

    authors_str = ", ".join(authors[:5]) if authors else "Unknown"

    prompt = f"""You are an expert research analyst. Analyze this academic paper and provide a concise, insightful summary.

Paper Title: {title}
Authors: {authors_str}
Abstract: {abstract}

Provide your response in this exact format:
SUMMARY: [A clear 2-3 sentence summary in plain language that a graduate student could understand]
KEY_POINTS:
- [Key finding or contribution 1]
- [Key finding or contribution 2]
- [Key finding or contribution 3]
SIGNIFICANCE: [One sentence on why this paper matters and its potential impact]
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        text = response.text

        summary = ""
        key_points = []
        significance = ""

        lines = text.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("SUMMARY:"):
                current_section = "summary"
                summary = line[len("SUMMARY:"):].strip()
            elif line.startswith("KEY_POINTS:"):
                current_section = "key_points"
            elif line.startswith("SIGNIFICANCE:"):
                current_section = "significance"
                significance = line[len("SIGNIFICANCE:"):].strip()
            elif current_section == "summary" and line and not line.startswith("-"):
                summary += " " + line
            elif current_section == "key_points" and line.startswith("-"):
                key_points.append(line[1:].strip())
            elif current_section == "significance" and line:
                significance += " " + line

        return {
            "summary": summary.strip() or text[:500],
            "key_points": key_points or ["See full summary above"],
            "significance": significance.strip() or "",
        }
    except Exception as e:
        logger.error(f"Gemini summarize error: {e}")
        return {
            "summary": f"AI summary generation failed: {str(e)}",
            "key_points": [],
            "significance": "",
        }
