from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OpportunityBase(BaseModel):
    title: str
    description: Optional[str] = None
    skills_required: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    organization_id: int

class OpportunityCreate(BaseModel):
    title: str
    description: Optional[str] = None
    skills_required: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    organization_id: Optional[int] = None  

class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    skills_required: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None

class OpportunityResponse(OpportunityBase):
    id: int
    
    class Config:
        from_attributes = True  
