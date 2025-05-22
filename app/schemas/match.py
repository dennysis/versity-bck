from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.models.match import MatchStatus

class MatchBase(BaseModel):
    opportunity_id: int

    @validator('opportunity_id')
    def opportunity_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('opportunity_id must be positive')
        return v

class MatchCreate(BaseModel):
    opportunity_id: int
    pass

class MatchUpdate(BaseModel):
    status: Optional[str] = None

    @validator('status')
    def status_must_be_valid(cls, v):
        if v not in [status.value for status in MatchStatus]:
            raise ValueError(f'status must be one of {[status.value for status in MatchStatus]}')
        return v

class MatchResponse(BaseModel):
    id: int
    user_id: int  
    opportunity_id: int
    status: MatchStatus
    matched_on: datetime 
    class Config:
        from_attribute = True
