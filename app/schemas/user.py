from pydantic import BaseModel, EmailStr 
from typing import Optional 
from datetime import date
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str
    admin_key: Optional[str] = None

# Add this to your existing user.py schema file

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    
    class Config:
        from_attributes = True

class VolunteerHourUpdate(BaseModel):
    hours: Optional[float] = None
    date: Optional[date] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attribute = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
