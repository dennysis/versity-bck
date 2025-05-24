from fastapi import APIRouter, Depends, HTTPException, status ,Query
from sqlalchemy.orm import Session
from app.config import get_db
from app.models.user import User, UserRole
from app.models.volunteer_hour import VolunteerHour
from app.schemas.user import UserResponse, UserUpdate
from app.models.opportunity import Opportunity
from app.schemas.volunteer_hour import VolunteerHourResponse
from app.models.match import Match, MatchStatus ,MatchResponse
from app.utils.auth import get_current_user
from typing import List,Dict , Any ,Optional
from sqlalchemy import func

router = APIRouter(prefix="/api/volunteers", tags=["volunteers"])

@router.get("/{id}", response_model=UserResponse)
def get_volunteer_profile(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    if current_user.id != id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this profile"
        )
    
    volunteer = db.query(User).filter(User.id == id, User.role == UserRole.VOLUNTEER).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    return volunteer

@router.put("/{id}", response_model=UserResponse)
def update_volunteer_profile(
    id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    
    if current_user.id != id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    volunteer = db.query(User).filter(User.id == id, User.role == UserRole.VOLUNTEER).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(volunteer, key, value)
    
    db.commit()
    db.refresh(volunteer)
    
    return volunteer

@router.get("/{id}/hours", response_model=List[VolunteerHourResponse])
def get_volunteer_hours(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    
    if current_user.id != id and current_user.role == UserRole.VOLUNTEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these hours"
        )
    
    volunteer = db.query(User).filter(User.id == id).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    hours = db.query(VolunteerHour).filter(VolunteerHour.user_id == id).all()
    
    return hours

@router.get("/{volunteer_id}/stats", response_model=Dict[str, Any])
def get_volunteer_stats(
    volunteer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a volunteer
    """
    # Check if volunteer exists
    volunteer = db.query(User).filter(
        User.id == volunteer_id,
        User.role == UserRole.VOLUNTEER
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Get total hours
    total_hours = db.query(func.sum(VolunteerHour.hours)).filter(
        VolunteerHour.user_id == volunteer_id
    ).scalar() or 0
    
    # Get total opportunities applied
    total_applications = db.query(func.count(Match.id)).filter(
        Match.user_id == volunteer_id
    ).scalar() or 0
    
    # Get accepted opportunities
    accepted_applications = db.query(func.count(Match.id)).filter(
        Match.user_id == volunteer_id,
        Match.status == MatchStatus.ACCEPTED
    ).scalar() or 0
    
    # Get recent activity
    recent_activity = db.query(VolunteerHour).filter(
        VolunteerHour.user_id == volunteer_id
    ).order_by(VolunteerHour.date.desc()).limit(5).all()
    
    return {
        "total_hours": float(total_hours),
        "total_applications": total_applications,
        "accepted_applications": accepted_applications,
        "completion_rate": (accepted_applications / total_applications * 100) if total_applications > 0 else 0,
        "recent_activity": recent_activity
    }


@router.get("/", response_model=List[UserResponse])
def list_volunteers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all volunteers
    - Admins: see all volunteers
    - Organizations: see volunteers who applied to their opportunities
    - Volunteers: see other volunteers (limited info)
    """
    if current_user.role == UserRole.ADMIN:
        # Admins can see all volunteers
        volunteers = db.query(User).filter(
            User.role == UserRole.VOLUNTEER
        ).offset(skip).limit(limit).all()
        
    elif current_user.role == UserRole.ORGANIZATION:
        # Organizations see volunteers who applied to their opportunities
        volunteers = db.query(User).join(Match).join(Opportunity).filter(
            User.role == UserRole.VOLUNTEER,
            Opportunity.organization_id == current_user.organization_id
        ).distinct().offset(skip).limit(limit).all()
        
    else:
        # Regular volunteers see other volunteers (basic info only)
        volunteers = db.query(User).filter(
            User.role == UserRole.VOLUNTEER,
            User.id != current_user.id
        ).offset(skip).limit(limit).all()
    
    return volunteers

@router.get("/{id}/matches", response_model=List[MatchResponse])
def get_volunteer_matches(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get volunteer's applications/matches
    """
    # Check if volunteer exists
    volunteer = db.query(User).filter(
        User.id == id, 
        User.role == UserRole.VOLUNTEER
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.VOLUNTEER and current_user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own applications"
        )
    elif current_user.role == UserRole.ORGANIZATION:
        # Organizations can only see matches for their opportunities
        matches = db.query(Match).join(Opportunity).filter(
            Match.user_id == id,
            Opportunity.organization_id == current_user.organization_id
        ).all()
        return matches
    
    # Admin or the volunteer themselves can see all matches
    matches = db.query(Match).filter(Match.user_id == id).all()
    return matches