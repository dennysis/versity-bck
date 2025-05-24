from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import get_db
from app.models.user import User, UserRole
from app.models.volunteer_hour import VolunteerHour
from app.models.opportunity import Opportunity
from app.schemas.volunteer_hour import VolunteerHourCreate, VolunteerHourResponse, VolunteerHourVerify, VolunteerHourUpdate
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


@router.get("/{id}", response_model=VolunteerHourResponse)
def get_volunteer_hour(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific volunteer hour entry
    """
    hour_entry = db.query(VolunteerHour).filter(VolunteerHour.id == id).first()
    
    if not hour_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer hour entry not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.VOLUNTEER and hour_entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own hour entries"
        )
    elif current_user.role == UserRole.ORGANIZATION:
        # Check if the hour entry is for their opportunity
        opportunity = db.query(Opportunity).filter(
            Opportunity.id == hour_entry.opportunity_id,
            Opportunity.organization_id == current_user.organization_id
        ).first()
        
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view hours for your organization's opportunities"
            )
    
    return hour_entry

@router.put("/{id}", response_model=VolunteerHourResponse)
def update_volunteer_hour(
    id: int,
    hour_data: VolunteerHourUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update volunteer hour entry
    """
    hour_entry = db.query(VolunteerHour).filter(VolunteerHour.id == id).first()
    
    if not hour_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer hour entry not found"
        )
    
    # Authorization check - only the volunteer who logged it can update
    if current_user.role == UserRole.VOLUNTEER and hour_entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own hour entries"
        )
    elif current_user.role != UserRole.VOLUNTEER and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers and admins can update hour entries"
        )
    
    # Don't allow updates if already verified
    if hour_entry.status == "verified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update verified hour entries"
        )
    
    try:
        # Update only provided fields
        update_data = hour_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(hour_entry, field):
                setattr(hour_entry, field, value)
        
        db.commit()
        db.refresh(hour_entry)
        
        return hour_entry
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating hour entry: {str(e)}"
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_volunteer_hour(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete volunteer hour entry
    """
    hour_entry = db.query(VolunteerHour).filter(VolunteerHour.id == id).first()
    
    if not hour_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer hour entry not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.VOLUNTEER and hour_entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own hour entries"
        )
    elif current_user.role != UserRole.VOLUNTEER and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers and admins can delete hour entries"
        )
    
    # Don't allow deletion if already verified
    if hour_entry.status == "verified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete verified hour entries"
        )
    
    try:
        db.delete(hour_entry)
        db.commit()
        return None
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting hour entry: {str(e)}"
        )