import sys
import os

# Add parent directory to path for recommendation module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import after loading env
from db.postgres import init_db, SessionLocal
from db.neo4j import Neo4jConnection
from models.user_models import Interest
from routes import auth_routes, user_routes, paper_routes, arxiv_routes

# Also import and expose the original recommendation endpoint for backwards compatibility
from recommendation.engine import recommend_papers


def seed_interests(db):
    """Seed default interests if not exists"""
    default_interests = [
        {"name": "Artificial Intelligence", "icon": "Brain", "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400"},
        {"name": "Machine Learning", "icon": "Cpu", "image_url": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400"},
        {"name": "Natural Language Processing", "icon": "MessageSquare", "image_url": "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=400"},
        {"name": "Computer Vision", "icon": "Eye", "image_url": "https://images.unsplash.com/photo-1561557944-6e7860d1a7eb?w=400"},
        {"name": "Robotics", "icon": "Bot", "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400"},
        {"name": "Data Science", "icon": "BarChart", "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400"},
        {"name": "Bioinformatics", "icon": "Dna", "image_url": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400"},
        {"name": "Physics", "icon": "Atom", "image_url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400"},
        {"name": "Mathematics", "icon": "Calculator", "image_url": "https://images.unsplash.com/photo-1635372722656-389f87a941b7?w=400"},
        {"name": "Medicine", "icon": "Stethoscope", "image_url": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=400"},
        {"name": "Neuroscience", "icon": "Brain", "image_url": "https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=400"},
        {"name": "Chemistry", "icon": "FlaskConical", "image_url": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=400"},
        {"name": "Environmental Science", "icon": "Leaf", "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400"},
        {"name": "Economics", "icon": "TrendingUp", "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400"},
        {"name": "Psychology", "icon": "Heart", "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400"},
        {"name": "Cybersecurity", "icon": "Shield", "image_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400"},
    ]
    
    existing = db.query(Interest).count()
    if existing == 0:
        for interest_data in default_interests:
            interest = Interest(**interest_data)
            db.add(interest)
        db.commit()
        logger.info("Seeded default interests")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    init_db()
    
    # Seed data
    db = SessionLocal()
    try:
        seed_interests(db)
    finally:
        db.close()
    
    # Test Neo4j connection
    driver = Neo4jConnection.get_driver()
    if driver:
        logger.info("Neo4j connection established")
    else:
        logger.warning("Neo4j connection failed - recommendations may be limited")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    Neo4jConnection.close()


app = FastAPI(
    title="Re-Search API",
    description="Research Paper Discovery & Recommendation System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(paper_routes.router)


# Keep original recommendation endpoint for backwards compatibility
@app.get("/api/recommendations/{user_id}")
def get_recommendations_legacy(user_id: int):
    """Legacy recommendation endpoint (from original repo)"""
    data = recommend_papers(user_id)
    if not data.get("recommendations"):
        data = {"message": "No recommendations found"}
    return data


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    neo4j_status = "connected" if Neo4jConnection.get_driver() else "disconnected"
    return {
        "status": "healthy",
        "neo4j": neo4j_status,
        "database": "connected"
    }


@app.get("/")
def root():
    return {
        "message": "Re-Search API - Research Paper Discovery System",
        "docs": "/docs",
        "health": "/api/health"
    }
