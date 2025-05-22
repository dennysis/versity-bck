from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
import sqlalchemy as sa


from app.config import get_db
from app.models.user import User, UserRole
from app.models.admin import Admin
from app.models.opportunity import Opportunity
from app.models.match import Match , MatchStatus
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

@router.get("/analytics", response_model=dict)
def get_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get detailed analytics data for admin dashboard
    """
    # Get user statistics
    volunteer_count = db.query(User).filter(User.role == UserRole.VOLUNTEER).count()
    organization_count = db.query(User).filter(User.role == UserRole.ORGANIZATION).count()
    admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
    total_users = volunteer_count + organization_count + admin_count
    
    # Get opportunity statistics
    opportunity_count = db.query(Opportunity).count()
    active_opportunities = db.query(Opportunity).filter(Opportunity.end_date >= datetime.now()).count()
    
    # Get match statistics
    total_matches = db.query(Match).count()
    pending_matches = db.query(Match).filter(Match.status == MatchStatus.PENDING).count()
    accepted_matches = db.query(Match).filter(Match.status == MatchStatus.ACCEPTED).count()
    rejected_matches = db.query(Match).filter(Match.status == MatchStatus.REJECTED).count()
    
    # Get volunteer hours statistics
    total_hours = db.query(sa.func.sum(VolunteerHour.hours)).scalar() or 0
    verified_hours = db.query(sa.func.sum(VolunteerHour.hours)).filter(VolunteerHour.verified == True).scalar() or 0
    
    # Get recent activity
    recent_users = db.query(User).order_by(User.id.desc()).limit(5).all()
    recent_opportunities = db.query(Opportunity).order_by(Opportunity.id.desc()).limit(5).all()
    recent_matches = db.query(Match).order_by(Match.id.desc()).limit(5).all()
    
    # Get monthly user registration data for charts
    current_year = datetime.now().year
    monthly_registrations = []
    
    # This would need to be adjusted based on how you store registration dates
    # Assuming there's a created_at field on the User model
    for month in range(1, 13):
        count = db.query(User).filter(
            sa.extract('year', User.created_at) == current_year,
            sa.extract('month', User.created_at) == month
        ).count()
        monthly_registrations.append({"month": month, "count": count})
    
    return {
        "users": {
            "total": total_users,
            "volunteers": volunteer_count,
            "organizations": organization_count,
            "admins": admin_count,
            "monthly_registrations": monthly_registrations
        },
        "opportunities": {
            "total": opportunity_count,
            "active": active_opportunities
        },
        "matches": {
            "total": total_matches,
            "pending": pending_matches,
            "accepted": accepted_matches,
            "rejected": rejected_matches
        },
        "volunteer_hours": {
            "total": float(total_hours),
            "verified": float(verified_hours)
        },
        "recent_activity": {
            "users": recent_users,
            "opportunities": recent_opportunities,
            "matches": recent_matches
        }
    }
