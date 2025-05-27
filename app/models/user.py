from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, JSON
from sqlalchemy.orm import relationship
from app.config import Base
from enum import Enum as PyEnum
from datetime import date
from typing import Optional

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
    
    
    name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    skills = Column(JSON, nullable=True) 
    availability = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    avatar = Column(String, nullable=True)  
    

    volunteer_hours = relationship("VolunteerHour", back_populates="user")
    matches = relationship("Match", back_populates="user")
    organization = relationship("Organization", back_populates="users")
    logs = relationship("SystemLog", back_populates="user")
    admin_profile = relationship("Admin", back_populates="user", uselist=False)
    volunteer_profile = relationship("Volunteer", back_populates="user", uselist=False)
