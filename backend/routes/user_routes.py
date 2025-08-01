from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.postgres import get_db
from models.user_models import User, Interest
from schemas.user_schemas import InterestResponse, UserInterestsUpdate, UserResponse
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/interests", response_model=List[InterestResponse])
def get_all_interests(db: Session = Depends(get_db)):
    """Get all available interests for onboarding"""
    interests = db.query(Interest).all()
    return interests


@router.post("/interests", response_model=UserResponse)
def update_user_interests(
    interests_data: UserInterestsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's selected interests (onboarding)"""
    # Get interests by IDs
    interests = db.query(Interest).filter(Interest.id.in_(interests_data.interest_ids)).all()
    
    # Update user's interests
    current_user.interests = interests
    current_user.has_completed_onboarding = True
    db.commit()
    db.refresh(current_user)
    
    interest_names = [interest.name for interest in current_user.interests]
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        has_completed_onboarding=current_user.has_completed_onboarding,
        interests=interest_names,
        created_at=current_user.created_at
    )


@router.get("/me/interests", response_model=List[InterestResponse])
def get_my_interests(current_user: User = Depends(get_current_user)):
    """Get current user's selected interests"""
    return current_user.interests
