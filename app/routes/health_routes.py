from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import get_db

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/")
def health_check():
    """
    Basic health check endpoint
    """
    return {"status": "healthy"}

@router.get("/db")
def db_health_check(db: Session = Depends(get_db)):
    """
    Database connection health check
    """
    try:
        # Use text() to wrap the SQL query
        db.execute(text("SELECT 1")).fetchall()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "disconnected", 
            "error": str(e)
        }