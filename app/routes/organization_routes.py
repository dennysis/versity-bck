from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import get_db
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.schemas.organization import OrganizationResponse, OrganizationUpdate,OrganizationCreate
from app.utils.auth import get_current_user, get_admin_user


router = APIRouter()

@router.get("/test")
def test_endpoint():
    return {"message": "Opportunity routes are working"}

@router.get("/{id}", response_model=OrganizationResponse)
def get_organization_profile(id: int, db: Session = Depends(get_db)):
    organization = db.query(Organization).filter(Organization.id == id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization

@router.put("/{id}", response_model=OrganizationResponse)
def update_organization_profile(
    id: int, 
    org_data: OrganizationUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
  
    if current_user.role != UserRole.ADMIN:
    
        if current_user.role != UserRole.ORGANIZATION:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this organization"
            )
    
    organization = db.query(Organization).filter(Organization.id == id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    
    for key, value in org_data.dict(exclude_unset=True).items():
        setattr(organization, key, value)
    
    db.commit()
    db.refresh(organization)
    
    return organization
@router.post("", response_model=OrganizationResponse)
@router.post("/", response_model=OrganizationResponse)
def create_organization(
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
  
    new_organization = Organization(
        name=organization_data.name,
        description=organization_data.description,
        contact_email=organization_data.contact_email,
        location=organization_data.location
    )
    
    db.add(new_organization)
    db.commit()
    db.refresh(new_organization)
    
    return new_organization

