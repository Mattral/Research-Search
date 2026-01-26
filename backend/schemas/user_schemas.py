from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    has_completed_onboarding: bool
    interests: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None


class InterestCreate(BaseModel):
    name: str
    icon: Optional[str] = None
    image_url: Optional[str] = None


class InterestResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str]
    image_url: Optional[str]
    
    class Config:
        from_attributes = True


class UserInterestsUpdate(BaseModel):
    interest_ids: List[int]


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
