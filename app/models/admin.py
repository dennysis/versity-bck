from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.config import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    can_manage_users = Column(Boolean, default=True)
    can_manage_organizations = Column(Boolean, default=True)
    can_manage_opportunities = Column(Boolean, default=True)
    can_verify_hours = Column(Boolean, default=True)
    
    # Add this relationship to link to User
    user = relationship("User", back_populates="admin_profile")
