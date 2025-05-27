from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, JSON
from sqlalchemy.orm import relationship
from app.config import Base

class Volunteer(Base):
    __tablename__ = "volunteers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    
    name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    skills = Column(JSON, nullable=True)
    availability = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    avatar = Column(String, nullable=True)
   
    user = relationship("User", back_populates="volunteer_profile")