from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.config import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    contact_email = Column(String, nullable=False)
    location = Column(String)
    phone = Column(String)  # Add if not exists
    verified = Column(Boolean, default=False)  # Add if not exists
    status = Column(String, default="active")  # Add if not exists
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Add if not exists
    
    # Relationships
    opportunities = relationship("Opportunity", back_populates="organization")
    users = relationship("User", back_populates="organization")
