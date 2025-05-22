from sqlalchemy import Column, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class VolunteerHour(Base):
    __tablename__ = "volunteer_hours"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    hours = Column(Float)
    date = Column(DateTime)
    verified = Column(Boolean, default=False)

    
    user = relationship("User", back_populates="volunteer_hours")
    opportunity = relationship("Opportunity", back_populates="volunteer_hours")
