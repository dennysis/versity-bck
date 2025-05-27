from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.models.user import User, UserRole
from app.models.volunteer import Volunteer
from app.schemas.user import UserResponse, UserUpdate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/volunteers", tags=["volunteers"])

@router.get("/{volunteer_id}", response_model=UserResponse)
def get_volunteer_profile(volunteer_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == volunteer_id).first()
    if not user or user.role != UserRole.VOLUNTEER:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    volunteer = db.query(Volunteer).filter(Volunteer.user_id == volunteer_id).first()
    
    profile_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id,
    }
    
    if volunteer:
        profile_data.update({
            "name": volunteer.name,
            "bio": volunteer.bio,
            "phone": volunteer.phone,
            "location": volunteer.location,
            "skills": volunteer.skills,
            "availability": volunteer.availability,
            "emergency_contact": volunteer.emergency_contact,
            "date_of_birth": volunteer.date_of_birth,
            "avatar": volunteer.avatar,
        })
    
    return profile_data

@router.put("/{volunteer_id}", response_model=UserResponse)
def update_volunteer_profile(
    volunteer_id: int,
    profile_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user can update this profile
    if current_user.id != volunteer_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    user = db.query(User).filter(User.id == volunteer_id).first()
    if not user or user.role != UserRole.VOLUNTEER:
        raise HTTPException(status_code=404, detail="Volunteer not found")
    
    volunteer = db.query(Volunteer).filter(Volunteer.user_id == volunteer_id).first()
    if not volunteer:
        volunteer = Volunteer(user_id=volunteer_id)
        db.add(volunteer)
    
    # Update volunteer fields
    update_data = profile_data.dict(exclude_unset=True)
    volunteer_fields = [
        "name", "bio", "phone", "location", "skills", 
        "availability", "emergency_contact", "date_of_birth", "avatar"
    ]
    for field in volunteer_fields:
        if field in update_data:
            setattr(volunteer, field, update_data[field])
    
    db.commit()
    db.refresh(volunteer)
    
    return get_volunteer_profile(volunteer_id, db)