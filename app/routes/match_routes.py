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
import logging
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# Create router WITHOUT prefix - it will be added in run.py
router = APIRouter()

@router.get("/test")
def test_endpoint():
    return {"message": "Match routes are working"}

@router.get("/", response_model=List[MatchResponse])
def list_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List matches based on user role:
    - Volunteers see only their own matches
    - Organizations see matches for their opportunities  
    - Admins see all matches
    """
    try:
        logger.info(f"User {current_user.id} ({current_user.role}) requesting matches")
        
        if current_user.role == UserRole.VOLUNTEER:
            matches = db.query(Match).filter(Match.user_id == current_user.id).all()
            logger.info(f"Volunteer {current_user.id} retrieved {len(matches)} matches")
            return matches
        
        elif current_user.role == UserRole.ORGANIZATION:
            if not current_user.organization_id:
                logger.warning(f"Organization user {current_user.id} has no organization_id")
                return []
            
            matches = (
                db.query(Match)
                .join(Opportunity, Match.opportunity_id == Opportunity.id)
                .filter(Opportunity.organization_id == current_user.organization_id)
                .all()
            )
            logger.info(f"Organization user {current_user.id} retrieved {len(matches)} matches")
            return matches
        
        elif current_user.role == UserRole.ADMIN:
            matches = db.query(Match).all()
            logger.info(f"Admin {current_user.id} retrieved {len(matches)} matches")
            return matches
        
        logger.warning(f"Unknown role {current_user.role} for user {current_user.id}")
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
    🎯 MAIN IMPLEMENTATION: Apply to an opportunity (volunteers only)
    This is the matchesAPI.apply() functionality
    """
    try:
        logger.info(f"User {current_user.id} applying to opportunity {match_data.opportunity_id}")
        
        # Only volunteers can apply
        if current_user.role != UserRole.VOLUNTEER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only volunteers can apply for opportunities"
            )

        # Check if opportunity exists
        opportunity = db.query(Opportunity).filter(
            Opportunity.id == match_data.opportunity_id
        ).first()
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        # Check for duplicate application
        existing_match = db.query(Match).filter(
            Match.user_id == current_user.id,
            Match.opportunity_id == match_data.opportunity_id
        ).first()
        if existing_match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied for this opportunity"
            )

        # Create new match/application
        new_match = Match(
            user_id=current_user.id,
            opportunity_id=match_data.opportunity_id,
            status=MatchStatus.PENDING
        )
        
        db.add(new_match)
        db.commit()
        db.refresh(new_match)
        
        logger.info(f"User {current_user.id} successfully applied to opportunity {match_data.opportunity_id}")
        return new_match
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating match: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while applying"
        )

@router.put("/{match_id}", response_model=MatchResponse)
def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update match status (organizations and admins only)
    """
    try:
        logger.info(f"User {current_user.id} updating match {match_id} to {match_data.status}")
        
        # Get the match
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )

        # Get the opportunity
        opportunity = db.query(Opportunity).filter(
            Opportunity.id == match.opportunity_id
        ).first()
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )

        # Check authorization
        if current_user.role == UserRole.ADMIN:
            pass  # Admins can update any match
        elif current_user.role == UserRole.ORGANIZATION:
            if (not current_user.organization_id or 
                opportunity.organization_id != current_user.organization_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to update this match"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organizations and admins can update match status"
            )

        # Update the match status
        match.status = match_data.status
        db.commit()
        db.refresh(match)
        
        logger.info(f"Match {match_id} updated to {match_data.status} by user {current_user.id}")
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

@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific match by ID
    """
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        
        # Check authorization
        if current_user.role == UserRole.VOLUNTEER:
            if match.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this match"
                )
        elif current_user.role == UserRole.ORGANIZATION:
            opportunity = db.query(Opportunity).filter(
                Opportunity.id == match.opportunity_id
            ).first()
            if (not current_user.organization_id or 
                not opportunity or 
                opportunity.organization_id != current_user.organization_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this match"
                )
        # Admins can view any match
        
        return match
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match {match_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
