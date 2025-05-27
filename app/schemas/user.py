from pydantic import BaseModel, EmailStr 
from typing import Optional, List
from datetime import date
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str
    admin_key: Optional[str] = None

class UserUpdate(BaseModel):
    # Basic user fields
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
    # Volunteer profile fields (will be handled separately)
    name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    availability: Optional[str] = None
    emergency_contact: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True

class VolunteerHourUpdate(BaseModel):
    hours: Optional[float] = None
    date: Optional[date] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    organization_id: Optional[int] = None
    
    # Volunteer profile fields (optional, only for volunteers)
    name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    availability: Optional[str] = None
    emergency_contact: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
