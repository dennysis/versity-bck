from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from app.config import get_db
from app.models.user import User, UserRole
from sqlalchemy.exc import SQLAlchemyError
from app.models.organization import Organization
from app.models.match import Match, MatchStatus
from app.models.opportunity import Opportunity
from app.schemas.match import MatchCreate, MatchResponse, MatchUpdate
from app.utils.auth import get_current_user, get_organization_user
logger = logging.getLogger(__name__)

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
    current_user: User = Depends(get_current_user)
):
    """
    Organizations (and Admins) can accept/reject an application.
    """
    try:
        # Debug logging
        logger.info(f"Update match {match_id} - User {current_user.id} (role: {current_user.role}, org_id: {current_user.organization_id})")
        
        # Get the match
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )

        # Get the opportunity
        opportunity = db.query(Opportunity).filter(Opportunity.id == match.opportunity_id).first()
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        # Debug logging
        logger.info(f"Match {match_id}: opportunity_id={match.opportunity_id}, opportunity.organization_id={opportunity.organization_id}")

        # Check authorization
        if current_user.role == UserRole.ADMIN:
            # Admins can update any match
            logger.info(f"Admin access granted for user {current_user.id}")
            pass
        elif current_user.role == UserRole.ORGANIZATION:
            # Organizations can only update matches for their opportunities
            logger.info(f"Organization check: user.org_id={current_user.organization_id}, opportunity.org_id={opportunity.organization_id}")
            if not current_user.organization_id or opportunity.organization_id != current_user.organization_id:
                logger.warning(f"Authorization failed: user.org_id={current_user.organization_id}, opportunity.org_id={opportunity.organization_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to update this match"
                )
        else:
            # Volunteers cannot update match status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organizations and admins can update match status"
            )

        # Update the match status
        match.status = match_data.status
        db.commit()
        db.refresh(match)
        
        logger.info(f"Match {match_id} updated to status {match_data.status} by user {current_user.id}")
        return match
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating match {match_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the match"
        )
