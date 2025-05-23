from fastapi import APIRouter, Depends, HTTPException, status
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

@router.get("/", response_model=Dict[str, Any])
def list_opportunities(
    skip: int = 0, 
    limit: int = 10,
    title: Optional[str] = None,
    location: Optional[str] = None,
    organization_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity)
   
    if title:
        query = query.filter(Opportunity.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location}%"))

    if organization_id:  
        query = query.filter(Opportunity.organization_id == organization_id)
    
    # Get total count for pagination
    total_count = query.count()
    
    # Get paginated results
    opportunities = query.offset(skip).limit(limit).all()
    
    # Convert SQLAlchemy models to dictionaries
    opportunity_dicts = []
    for opp in opportunities:
        # Create a dictionary with the opportunity attributes
        opp_dict = {
            "id": opp.id,
            "title": opp.title,
            "description": opp.description,
            "skills_required": opp.skills_required,
            "start_date": opp.start_date,
            "end_date": opp.end_date,
            "location": opp.location,
            "organization_id": opp.organization_id,
            # Add any other fields you need
        }
        opportunity_dicts.append(opp_dict)
    
    # Calculate page number and total pages
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 1  # Ceiling division
    
    # Return structured response with pagination info
    return {
        "items": opportunity_dicts,  # Use the list of dictionaries instead of SQLAlchemy models
        "page": page,
        "totalPages": total_pages,
        "totalItems": total_count
    }

@router.get("", response_model=Dict[str, Any])  # Add this route to handle requests without trailing slash
def list_opportunities_no_slash(
    skip: int = 0, 
    limit: int = 10,
    title: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return list_opportunities(skip, limit, title, location, db)

@router.get("/{id}", response_model=OpportunityResponse)
def get_opportunity(id: int, db: Session = Depends(get_db)):
    opportunity = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Convert SQLAlchemy model to dictionary
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
    
   
    if current_user.role != UserRole.ADMIN:
        
        pass
    
   
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
    
   
    if current_user.role != UserRole.ADMIN:
     
        if opportunity.organization_id != current_user.id:  
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this opportunity"
            )
    
    db.delete(opportunity)
    db.commit()
    
    return None
