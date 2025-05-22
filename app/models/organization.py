from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.config import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    contact_email = Column(String, nullable=False)
    location = Column(String)
    
    
    opportunities = relationship("Opportunity", back_populates="organization")
    users = relationship("User", back_populates="organization")
