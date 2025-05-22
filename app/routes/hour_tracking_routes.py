from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import get_db
from app.models.user import User, UserRole
from app.models.volunteer_hour import VolunteerHour
from app.models.opportunity import Opportunity
from app.schemas.volunteer_hour import VolunteerHourCreate, VolunteerHourResponse, VolunteerHourVerify
from app.utils.auth import get_current_user, get_organization_user
from typing import List

router = APIRouter(prefix="/api/hours", tags=["hour tracking"])

@router.post("/", response_model=VolunteerHourResponse)
def log_hours(
    hour_data: VolunteerHourCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):

    if current_user.role != UserRole.VOLUNTEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can log hours"
        )
    
 
    opportunity = db.query(Opportunity).filter(Opportunity.id == hour_data.opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    

    new_hour = VolunteerHour(
        user_id=current_user.id,
        opportunity_id=hour_data.opportunity_id,
        hours=hour_data.hours,
        date=hour_data.date,
        verified=False
    )
    
    db.add(new_hour)
    db.commit()
    db.refresh(new_hour)
    
    return new_hour


@router.get("/", response_model=List[VolunteerHourResponse])
def list_hours(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    if current_user.role == UserRole.VOLUNTEER:
        hours = db.query(VolunteerHour).filter(VolunteerHour.user_id == current_user.id).all()
    
    elif current_user.role == UserRole.ORGANIZATION:
        
        hours = db.query(VolunteerHour).join(
            Opportunity, VolunteerHour.opportunity_id == Opportunity.id
        ).filter(
            Opportunity.organization_id == current_user.id
        ).all()

    elif current_user.role == UserRole.ADMIN:
        hours = db.query(VolunteerHour).all()
    else:
        hours = []
    
    return hours


@router.put("/{id}/verify", response_model=VolunteerHourResponse)
def verify_hours(
    id: int, 
    verify_data: VolunteerHourVerify, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_organization_user)
):
    hour = db.query(VolunteerHour).filter(VolunteerHour.id == id).first()
    if not hour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hour record not found"
        )
  
    if current_user.role == UserRole.ORGANIZATION:
      
        opportunity = db.query(Opportunity).filter(Opportunity.id == hour.opportunity_id).first()
        if not opportunity or opportunity.organization_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to verify these hours"
            )
    
   
    hour.verified = (verify_data.status == "approved")
    
    db.commit()
    db.refresh(hour)
    
    return hour