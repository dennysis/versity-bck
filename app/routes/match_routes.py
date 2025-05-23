from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config import get_db
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.match import Match, MatchStatus
from app.models.opportunity import Opportunity
from app.schemas.match import MatchCreate, MatchResponse, MatchUpdate
from app.utils.auth import get_current_user, get_organization_user

router = APIRouter(prefix="/api/matches", tags=["matches"], redirect_slashes=True)


@router.get("/test")
def test_endpoint():
    return {"message": "Match routes are working"}

@router.get("/", response_model=List[MatchResponse])
def list_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    - Volunteers see only their own matches.
    - Organizations see matches for opportunities they own.
    - Admins see all matches.
    """
    try:
        # Volunteer users see only their own matches
        if current_user.role == UserRole.VOLUNTEER:
            return db.query(Match).filter(Match.user_id == current_user.id).all()
        
        # Organization users see matches for their opportunities
        elif current_user.role == UserRole.ORGANIZATION:
            # Get organization directly from user's organization_id
            if not current_user.organization_id:
               return []
            
            # Find all matches for opportunities belonging to this organization
            return (
                db.query(Match)
                .join(Opportunity, Match.opportunity_id == Opportunity.id)
                .filter(Opportunity.organization_id == current_user.organization_id)
                .all()
            )
        
        # Admin users see all matches
        elif current_user.role == UserRole.ADMIN:
            return db.query(Match).all()
        
        # Default case - empty list for unknown roles
        return []
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_matches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving matches from database"
        )
    except Exception as e:
        logger.error(f"Unexpected error in list_matches: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    match_data: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Only volunteers can apply for an opportunity.
    Prevent duplicate applications.
    """
    if current_user.role != UserRole.VOLUNTEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only volunteers can apply for opportunities"
        )

    opportunity = db.query(Opportunity) \
                    .filter(Opportunity.id == match_data.opportunity_id) \
                    .first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

   
    duplicate = db.query(Match) \
                  .filter(
                      Match.user_id == current_user.id,
                      Match.opportunity_id == match_data.opportunity_id
                  ).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already applied for this opportunity"
        )

    new_match = Match(
        user_id=current_user.id,
        opportunity_id=match_data.opportunity_id,
        status=MatchStatus.PENDING
    )
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match
@router.put("/{match_id}", response_model=MatchResponse)
def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_organization_user)
):
    """
    Organizations (and Admins, via the same dependency) can accept/reject an application.
    """
    match = (
        db.query(Match)
          .filter(Match.id == match_id)
          .first()
    )
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

  
    opportunity = db.query(Opportunity) \
                    .filter(Opportunity.id == match.opportunity_id) \
                    .first()
    if opportunity.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this match"
        )


    match.status = match_data.status
    db.commit()
    db.refresh(match)
    return match
