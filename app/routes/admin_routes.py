from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.config import get_db
from app.models.user import User, UserRole
from app.models.admin import Admin
from app.models.opportunity import Opportunity
from app.models.match import Match
from app.models.volunteer_hour import VolunteerHour
from app.models.system_log import SystemLog  

from app.schemas.user import UserResponse
from app.schemas.opportunity import OpportunityResponse
from app.schemas.match import MatchResponse
from app.schemas.volunteer_hour import VolunteerHourResponse
from app.schemas.admin import AdminResponse 

from app.utils.auth import get_current_user, get_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_admin_user)]
)

@router.get("/test")
def test_endpoint():
    return {"message": "Admin routes are working"}

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all users (admin only)
    """
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get a specific user by ID (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Delete a user (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Not to delete Admin's account
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    return None

@router.get("/logs")
def get_system_logs(
    limit: int = 100, 
    offset: int = 0, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
):
    """
    Get system logs (admin only)
    """
    
    logs = db.query(SystemLog).order_by(SystemLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get system statistics for admin dashboard
    """
    volunteer_count = db.query(User).filter(User.role == UserRole.VOLUNTEER).count()
    organization_count = db.query(User).filter(User.role == UserRole.ORGANIZATION).count()
    admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
    opportunity_count = db.query(Opportunity).count()
    match_count = db.query(Match).count()
    
    recent_users = db.query(User).order_by(User.id.desc()).limit(5).all()
    
    return {
        "user_counts": {
            "volunteers": volunteer_count,
            "organizations": organization_count,
            "admins": admin_count,
            "total": volunteer_count + organization_count + admin_count
        },
        "opportunity_count": opportunity_count,
        "match_count": match_count,
        "recent_users": recent_users
    }

@router.get("/users/volunteers", response_model=List[UserResponse])
def get_all_volunteers(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all volunteer users (admin only)
    """
    volunteers = db.query(User).filter(User.role == UserRole.VOLUNTEER).all()
    return volunteers

@router.get("/users/organizations", response_model=List[UserResponse])
def get_all_organizations(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all organization users (admin only)
    """
    organizations = db.query(User).filter(User.role == UserRole.ORGANIZATION).all()
    return organizations
@router.get("/opportunities", response_model=List[OpportunityResponse])
def get_all_opportunities(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all opportunities (admin only)
    """
    opportunities = db.query(Opportunity).all()
    return opportunities

@router.delete("/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(opportunity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Delete an opportunity (admin only)
    """
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    db.delete(opportunity)
    db.commit()
    return None
@router.get("/matches", response_model=List[MatchResponse])
def get_all_matches(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all matches (admin only)
    """
    matches = db.query(Match).all()
    return matches
@router.get("/hours", response_model=List[VolunteerHourResponse])
def get_all_volunteer_hours(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all volunteer hours (admin only)
    """
    hours = db.query(VolunteerHour).all()
    return hours

@router.get("/admins", response_model=List[AdminResponse])
def get_all_admins(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all admin users with their permissions (admin only)
    """
    admins = db.query(Admin).all()
    return admins
