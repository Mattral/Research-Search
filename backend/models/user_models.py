from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db.postgres import Base

# Association table for user interests
user_interests = Table(
    'user_interests',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('interest_id', Integer, ForeignKey('interests.id'), primary_key=True)
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    has_completed_onboarding = Column(Boolean, default=False)
    
    interests = relationship("Interest", secondary=user_interests, back_populates="users")
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    recent_views = relationship("UserRecentView", back_populates="user", cascade="all, delete-orphan")
    saved_arxiv_papers = relationship("SavedArxivPaper", back_populates="user", cascade="all, delete-orphan")


class Interest(Base):
    __tablename__ = "interests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    icon = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    users = relationship("User", secondary=user_interests, back_populates="interests")


class UserFavorite(Base):
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    paper_id = Column(String(100), nullable=False)
    paper_title = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="favorites")


class UserRecentView(Base):
    __tablename__ = "user_recent_views"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    paper_id = Column(String(100), nullable=False)
    paper_title = Column(String(500), nullable=True)
    viewed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="recent_views")


class SavedArxivPaper(Base):
    __tablename__ = "saved_arxiv_papers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    arxiv_id = Column(String(50), nullable=False)
    title = Column(String(1000), nullable=False)
    authors_str = Column(String(2000), nullable=True)
    summary = Column(String(5000), nullable=True)
    primary_category = Column(String(50), nullable=True)
    published = Column(String(50), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    notes = Column(String(2000), nullable=True)
    saved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="saved_arxiv_papers")
