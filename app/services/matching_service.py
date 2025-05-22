from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from app.models.user import User, UserRole
from app.models.match import Match, MatchStatus
from app.models.opportunity import Opportunity
from app.models.organization import Organization
from app.utils.email import send_match_notification_email

logger = logging.getLogger(__name__)

class MatchingService:
    """
    Service for matching volunteers with opportunities based on skills and preferences.
    Also handles match status updates and notifications.
    """
    
    @staticmethod
    def find_matches_for_volunteer(db: Session, volunteer_id: int, limit: int = 10) -> List[Opportunity]:
        """
        Find suitable opportunities for a volunteer based on their skills and preferences.
        
        Args:
            db: Database session
            volunteer_id: ID of the volunteer
            limit: Maximum number of opportunities to return
            
        Returns:
            List of matching opportunities
        """
        try:
            
            volunteer = db.query(User).filter(
                User.id == volunteer_id,
                User.role == UserRole.VOLUNTEER
            ).first()
            
            if not volunteer:
                logger.warning(f"Volunteer with ID {volunteer_id} not found")
                return []
            
            
            existing_matches = db.query(Match.opportunity_id).filter(
                Match.user_id == volunteer_id
            ).all()
            
            existing_opportunity_ids = [match[0] for match in existing_matches]
            
         
            query = db.query(Opportunity).filter(
                Opportunity.id.notin_(existing_opportunity_ids)
            )
            
        
            
            return query.limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error finding matches for volunteer {volunteer_id}: {str(e)}")
            return []
    
    @staticmethod
    def find_volunteers_for_opportunity(db: Session, opportunity_id: int, limit: int = 20) -> List[User]:
        """
        Find suitable volunteers for an opportunity based on skills and preferences.
        
        Args:
            db: Database session
            opportunity_id: ID of the opportunity
            limit: Maximum number of volunteers to return
            
        Returns:
            List of matching volunteers
        """
        try:
          
            opportunity = db.query(Opportunity).filter(
                Opportunity.id == opportunity_id
            ).first()
            
            if not opportunity:
                logger.warning(f"Opportunity with ID {opportunity_id} not found")
                return []
            
          
            existing_applicants = db.query(Match.user_id).filter(
                Match.opportunity_id == opportunity_id
            ).all()
            
            existing_applicant_ids = [match[0] for match in existing_applicants]
            
         
            query = db.query(User).filter(
                User.role == UserRole.VOLUNTEER,
                User.id.notin_(existing_applicant_ids)
            )
            
            
            return query.limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error finding volunteers for opportunity {opportunity_id}: {str(e)}")
            return []
    
    @staticmethod
    def create_match(db: Session, volunteer_id: int, opportunity_id: int) -> Optional[Match]:
        """
        Create a new match between a volunteer and an opportunity.
        
        Args:
            db: Database session
            volunteer_id: ID of the volunteer
            opportunity_id: ID of the opportunity
            
        Returns:
            Created match or None if creation failed
        """
        try:
          
            volunteer = db.query(User).filter(
                User.id == volunteer_id,
                User.role == UserRole.VOLUNTEER
            ).first()
            
            if not volunteer:
                logger.warning(f"Volunteer with ID {volunteer_id} not found")
                return None
            
           
            opportunity = db.query(Opportunity).filter(
                Opportunity.id == opportunity_id
            ).first()
            
            if not opportunity:
                logger.warning(f"Opportunity with ID {opportunity_id} not found")
                return None
         
            existing_match = db.query(Match).filter(
                Match.user_id == volunteer_id,
                Match.opportunity_id == opportunity_id
            ).first()
            
            if existing_match:
                logger.info(f"Match already exists between volunteer {volunteer_id} and opportunity {opportunity_id}")
                return existing_match
            
       
            new_match = Match(
                user_id=volunteer_id,
                opportunity_id=opportunity_id,
                status=MatchStatus.PENDING
            )
            
            db.add(new_match)
            db.commit()
            db.refresh(new_match)
         
            send_match_notification_email(
                volunteer.email,
                volunteer.username,
                opportunity.title
            )
            
            return new_match
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating match: {str(e)}")
            return None
    
    @staticmethod
    def update_match_status(db: Session, match_id: int, new_status: MatchStatus) -> Optional[Match]:
        """
        Update the status of a match.
        
        Args:
            db: Database session
            match_id: ID of the match
            new_status: New status for the match
            
        Returns:
            Updated match or None if update failed
        """
        try:
            match = db.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                logger.warning(f"Match with ID {match_id} not found")
                return None
            
            match.status = new_status
            db.commit()
            db.refresh(match)
            
            
            volunteer = db.query(User).filter(User.id == match.user_id).first()
            opportunity = db.query(Opportunity).filter(Opportunity.id == match.opportunity_id).first()
            
         
            from app.services.notification_service import NotificationService
            NotificationService.send_match_status_notification(
                volunteer.email,
                volunteer.username,
                opportunity.title,
                new_status
            )
            
            return match
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating match status: {str(e)}")
            return None
    
    @staticmethod
    def get_match_statistics(db: Session, organization_id: Optional[int] = None) -> dict:
        """
        Get statistics about matches.
        
        Args:
            db: Database session
            organization_id: Optional organization ID to filter statistics
            
        Returns:
            Dictionary with match statistics
        """
        try:
        
            base_query = db.query(Match)
            
          
            if organization_id:
                base_query = base_query.join(
                    Opportunity, Match.opportunity_id == Opportunity.id
                ).filter(
                    Opportunity.organization_id == organization_id
                )
       
            total_matches = base_query.count()
         
            pending_matches = base_query.filter(Match.status == MatchStatus.PENDING).count()
            accepted_matches = base_query.filter(Match.status == MatchStatus.ACCEPTED).count()
            rejected_matches = base_query.filter(Match.status == MatchStatus.REJECTED).count()
            
            return {
                "total_matches": total_matches,
                "pending_matches": pending_matches,
                "accepted_matches": accepted_matches,
                "rejected_matches": rejected_matches,
                "acceptance_rate": (accepted_matches / total_matches * 100) if total_matches > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting match statistics: {str(e)}")
            return {
                "total_matches": 0,
                "pending_matches": 0,
                "accepted_matches": 0,
                "rejected_matches": 0,
                "acceptance_rate": 0
            }
