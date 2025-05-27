from fastapi import APIRouter, Depends, HTTPException, status, Query  # ✅ Add Query here
from sqlalchemy.orm import Session
from app.config import get_db
from app.models.user import User, UserRole
from app.models.opportunity import Opportunity
from app.models.organization import Organization
from app.schemas.opportunity import OpportunityCreate, OpportunityResponse, OpportunityUpdate
from app.utils.auth import get_current_user, get_organization_user
from typing import List, Optional, Dict, Any

# Create router without prefix - prefix is added in run.py
router = APIRouter()

@router.get("/", response_model=List[OpportunityResponse])
def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    title: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    remote: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get all opportunities with optional filtering
    """
    try:
        # Now db is a proper Session object
        query = db.query(Opportunity)
        
        # Apply filters
        if title:
            query = query.filter(Opportunity.title.ilike(f"%{title}%"))
        
        if location:
            query = query.filter(Opportunity.location.ilike(f"%{location}%"))
            
        if category:
            query = query.filter(Opportunity.category.ilike(f"%{category}%"))
            
        if search:
            query = query.filter(
                Opportunity.title.ilike(f"%{search}%") |
                Opportunity.description.ilike(f"%{search}%")
            )
            
        if remote is not None:
            query = query.filter(Opportunity.is_remote == remote)
        
        # Get total count for pagination
        total = query.count()
        
        # Apply pagination
        opportunities = query.offset(skip).limit(limit).all()
        
        return opportunities
        
    except Exception as e:
        print(f"Error in list_opportunities: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Remove the duplicate route - this is causing conflicts
# @router.get("", response_model=Dict[str, Any])  # ❌ DELETE THIS
# def list_opportunities_no_slash(...):  # ❌ DELETE THIS

@router.get("/{id}", response_model=OpportunityResponse)
def get_opportunity(id: int, db: Session = Depends(get_db)):
    opportunity = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity

@router.post("/", response_model=OpportunityResponse)
def create_opportunity(
    opportunity_data: OpportunityCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_organization_user)
):
    try:
        if current_user.role == UserRole.ORGANIZATION:
            if hasattr(current_user, 'organization_id') and current_user.organization_id:
                organization_id = current_user.organization_id
            else:
                # Create organization if it doesn't exist
                organization = db.query(Organization).filter(
                    Organization.contact_email == current_user.email
                ).first()
                
                if not organization:
                    organization = Organization(
                        name=current_user.username,
                        description="Organization profile",
                        contact_email=current_user.email,
                        location="Not specified"
                    )
                    db.add(organization)
                    db.commit()
                    db.refresh(organization)
                
                organization_id = organization.id
                
        elif current_user.role == UserRole.ADMIN:
            if not hasattr(opportunity_data, 'organization_id') or not opportunity_data.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Admin users must specify an organization_id"
                )
            organization_id = opportunity_data.organization_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization or admin users can create opportunities"
            )
        
        new_opportunity = Opportunity(
            title=opportunity_data.title,
            description=opportunity_data.description,
            skills_required=opportunity_data.skills_required,
            start_date=opportunity_data.start_date,
            end_date=opportunity_data.end_date,
            location=opportunity_data.location,
            organization_id=organization_id
        )
        
        db.add(new_opportunity)
        db.commit()
        db.refresh(new_opportunity)
        
        return new_opportunity
        
    except Exception as e:
        print(f"Error in create_opportunity: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.put("/{id}", response_model=OpportunityResponse)
def update_opportunity(
    id: int, 
    opportunity_data: OpportunityUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_organization_user)
):
    opportunity = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Authorization check (unless admin)
    if current_user.role != UserRole.ADMIN:
        if opportunity.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this opportunity"
            )
    
    for key, value in opportunity_data.dict(exclude_unset=True).items():
        setattr(opportunity, key, value)
    
    db.commit()
    db.refresh(opportunity)
    
    return opportunity

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_organization_user)
):
    opportunity = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Authorization check (unless admin)
    if current_user.role != UserRole.ADMIN:
        if opportunity.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this opportunity"
            )
    
    db.delete(opportunity)
    db.commit()
    
    return None
