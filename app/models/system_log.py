from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base
from datetime import datetime

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR, etc.
    message = Column(Text, nullable=False)
    source = Column(String, nullable=True)  # Which part of the system generated the log
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who triggered the action (if applicable)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="logs")