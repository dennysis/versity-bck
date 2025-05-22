from pydantic import BaseModel
from typing import Optional

class AdminBase(BaseModel):
    user_id: int
    can_manage_users: bool = True
    can_manage_organizations: bool = True
    can_manage_opportunities: bool = True
    can_verify_hours: bool = True

class AdminCreate(AdminBase):
    pass

class AdminUpdate(BaseModel):
    can_manage_users: Optional[bool] = None
    can_manage_organizations: Optional[bool] = None
    can_manage_opportunities: Optional[bool] = None
    can_verify_hours: Optional[bool] = None

class AdminResponse(AdminBase):
    id: int
    
    class Config:
        from_attribute = True