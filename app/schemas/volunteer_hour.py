from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VolunteerHourBase(BaseModel):
    volunteer_id: int
    opportunity_id: int
    hours: float
    date: datetime
    description: Optional[str] = None

    
class VolunteerHourCreate(BaseModel):
    opportunity_id: int
    hours: float
    date: datetime
class VolunteerHourUpdate(BaseModel):
    hours: Optional[float] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[str] = None

class VolunteerHourVerify(BaseModel):
    status: str  
    admin_notes: Optional[str] = None

class VolunteerHourResponse(BaseModel):
    id: int
    user_id: int
    opportunity_id: int
    hours: float
    date: datetime
    verified: bool
    
    class Config:
        from_attribute = True
