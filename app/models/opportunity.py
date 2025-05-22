from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    skills_required = Column(String) 
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    
    organization = relationship("Organization", back_populates="opportunities")
    matches = relationship("Match", back_populates="opportunity")
    volunteer_hours = relationship("VolunteerHour", back_populates="opportunity")
