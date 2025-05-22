from pydantic import BaseModel, EmailStr
from typing import Optional, List

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    contact_email: EmailStr
    location: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    location: Optional[str] = None

class OrganizationResponse(OrganizationBase):
    id: int
    
    class Config:
        from_attributes = True  
