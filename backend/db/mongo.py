"""
MongoDB (async, Motor) connection for the hybrid recommendation store.

Holds the seeded `papers` corpus (with embeddings) and `recommendation_feedback`.
Relational data (users, workspaces, favorites) stays in SQLAlchemy/Postgres.
"""
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

papers_collection = db["papers"]
feedback_collection = db["recommendation_feedback"]
meta_collection = db["rec_meta"]


async def ensure_indexes():
    await papers_collection.create_index("paper_id", unique=True)
    await papers_collection.create_index("citation_count")
    await feedback_collection.create_index([("user_id", 1), ("paper_id", 1)], unique=True)
