from enum import Enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.config import Base
from datetime import datetime

class MatchStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    status = Column(SQLAlchemyEnum(MatchStatus), default=MatchStatus.PENDING)
    matched_on = Column(DateTime, default=datetime.utcnow)

    
    user = relationship("User", back_populates="matches")
    opportunity = relationship("Opportunity", back_populates="matches")
