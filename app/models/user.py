from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base
from enum import Enum as PyEnum 

class UserRole(str, PyEnum):
    VOLUNTEER = "volunteer"
    ORGANIZATION = "organization"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) 
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Relationships
    volunteer_hours = relationship("VolunteerHour", back_populates="user")
    matches = relationship("Match", back_populates="user")
    organization = relationship("Organization", back_populates="users")
    logs = relationship("SystemLog", back_populates="user")
    
    # Add this relationship to link back to Admin
    admin_profile = relationship("Admin", back_populates="user", uselist=False)
