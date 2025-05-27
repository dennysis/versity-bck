from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config import get_db
from app.models.user import User, UserRole
from app.models.admin import Admin
from app.models.volunteer import Volunteer  # Add this import
from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate
from app.utils.auth import create_access_token, get_password_hash
from datetime import timedelta
from passlib.context import CryptContext
from app.utils.auth import get_current_user, get_admin_user
from app.models.organization import Organization
from app.utils.email import send_welcome_email, request_password_reset, verify_password_reset_token
from app.schemas.auth import EmailSchema, PasswordResetSchema
import os

router = APIRouter(prefix="/api/auth", tags=["authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_ADMINS = 3

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    admin_key = user_data.admin_key
    
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    if user_data.role == UserRole.ADMIN:
        if not admin_key or admin_key != os.getenv("ADMIN_REGISTRATION_KEY"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin registration key"
            )
        
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        if admin_count >= MAX_ADMINS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin registration limit reached"
            )

    hashed_password = pwd_context.hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create volunteer profile for volunteers
    if new_user.role == UserRole.VOLUNTEER:
        volunteer_profile = Volunteer(
            user_id=new_user.id,
            name=user_data.username  # Set initial name to username
        )
        db.add(volunteer_profile)
        db.commit()
        db.refresh(volunteer_profile)
    
    # Handle organization creation
    elif new_user.role == UserRole.ORGANIZATION:
        new_organization = Organization(
            name=user_data.username,
            description="Organization profile",
            contact_email=user_data.email,
            location="Not specified"
        )
        
        db.add(new_organization)
        db.commit()
        db.refresh(new_organization)
        
        new_user.organization_id = new_organization.id
        db.commit()
        db.refresh(new_user)
    
    # Handle admin creation
    elif new_user.role == UserRole.ADMIN:
        new_admin = Admin(
            user_id=new_user.id,
            can_manage_users=True,
            can_manage_organizations=True,
            can_manage_opportunities=True,
            can_verify_hours=True
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

    send_welcome_email(new_user.username, new_user.email)

    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    return {"message": "Successfully logged out"}

@router.post("/refresh-token", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

def get_user_response_data(user: User, db: Session) -> dict:
    """Helper function to get user data with volunteer profile if applicable"""
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "organization_id": user.organization_id,
    }
    
    # If user is a volunteer, include volunteer profile data
    if user.role == UserRole.VOLUNTEER:
        volunteer = db.query(Volunteer).filter(Volunteer.user_id == user.id).first()
        if volunteer:
            user_data.update({
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
    
    return user_data

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the current authenticated user's profile"""
    return get_user_response_data(current_user, db)

@router.post("/forgot-password")
def forgot_password(email_data: EmailSchema, db: Session = Depends(get_db)):
    success = request_password_reset(email_data.email, db)
    return {"message": "If your email is registered, you will receive a password reset link"}

@router.post("/reset-password")
def reset_password(reset_data: PasswordResetSchema, db: Session = Depends(get_db)):
    email = verify_password_reset_token(reset_data.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    hashed_password = pwd_context.hash(reset_data.new_password)
    user.password_hash = hashed_password
    
    db.commit()
    
    return {"message": "Password has been reset successfully"}

@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    try:
        update_data = user_data.dict(exclude_unset=True)
        
        # Update basic user fields
        user_fields = ["username", "email"]
        for field in user_fields:
            if field in update_data and hasattr(current_user, field):
                setattr(current_user, field, update_data[field])
        
        # Handle password update
        if 'password' in update_data:
            hashed_password = get_password_hash(update_data['password'])
            current_user.password_hash = hashed_password
        
        # If user is a volunteer, update volunteer profile
        if current_user.role == UserRole.VOLUNTEER:
            volunteer = db.query(Volunteer).filter(Volunteer.user_id == current_user.id).first()
            if not volunteer:
                # Create volunteer profile if it doesn't exist
                volunteer = Volunteer(user_id=current_user.id)
                db.add(volunteer)
            
            # Update volunteer fields
            volunteer_fields = [
                "name", "bio", "phone", "location", "skills", 
                "availability", "emergency_contact", "date_of_birth", "avatar"
            ]
            for field in volunteer_fields:
                if field in update_data:
                    setattr(volunteer, field, update_data[field])
        
        db.commit()
        db.refresh(current_user)
        
        return get_user_response_data(current_user, db)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update any user's profile (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        update_data = user_data.dict(exclude_unset=True)
        
        # Update basic user fields
        user_fields = ["username", "email"]
        for field in user_fields:
            if field in update_data and hasattr(user, field):
                setattr(user, field, update_data[field])
        
        # Handle password update
        if 'password' in update_data:
            hashed_password = get_password_hash(update_data['password'])
            user.password_hash = hashed_password
        
               # If user is a volunteer, update volunteer profile
        if user.role == UserRole.VOLUNTEER:
            volunteer = db.query(Volunteer).filter(Volunteer.user_id == user.id).first()
            if not volunteer:
                # Create volunteer profile if it doesn't exist
                volunteer = Volunteer(user_id=user.id)
                db.add(volunteer)
            
            # Update volunteer fields
            volunteer_fields = [
                "name", "bio", "phone", "location", "skills", 
                "availability", "emergency_contact", "date_of_birth", "avatar"
            ]
            for field in volunteer_fields:
                if field in update_data:
                    setattr(volunteer, field, update_data[field])
        
        db.commit()
        db.refresh(user)
        
        return get_user_response_data(user, db)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

