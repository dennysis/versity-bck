from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
import sqlalchemy as sa
import traceback

from app.config import get_db
from app.models.user import User, UserRole
from app.models.admin import Admin
from app.models.opportunity import Opportunity
from app.models.match import Match, MatchStatus
from app.models.volunteer_hour import VolunteerHour
from app.models.system_log import SystemLog
from app.models.organization import Organization
from app.schemas.organization import OrganizationResponse

from app.schemas.user import UserResponse
from app.schemas.opportunity import OpportunityResponse
from app.schemas.match import MatchResponse
from app.schemas.volunteer_hour import VolunteerHourResponse
from app.schemas.admin import AdminResponse

from app.utils.auth import get_current_user, get_admin_user

router = APIRouter()

@router.get("/test")
def test_endpoint():
    return {"message": "Admin routes are working"}

# Get all users
@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all users (admin only)
    """
    users = db.query(User).all()
    return users

# Get all volunteers - DEFINE THIS BEFORE /users/{user_id}
@router.get("/users/volunteers", response_model=List[UserResponse])
def get_all_volunteers(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all volunteer users (admin only)
    """
    volunteers = db.query(User).filter(User.role == UserRole.VOLUNTEER).all()
    return volunteers

# Get all organizations - DEFINE THIS BEFORE /users/{user_id}
@router.get("/users/organizations", response_model=List[UserResponse])
def get_all_organizations(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all organization users (admin only)
    """
    organizations = db.query(User).filter(User.role == UserRole.ORGANIZATION).all()
    return organizations

# Get a specific user by ID - DEFINE THIS AFTER the more specific routes
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get a specific user by ID (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Delete a user (admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Not to delete Admin's account
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    return None

@router.get("/logs")
def get_system_logs(
    limit: int = 100, 
    offset: int = 0, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
):
    """
    Get system logs (admin only)
    """
    
    logs = db.query(SystemLog).order_by(SystemLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get system statistics for admin dashboard
    """
    volunteer_count = db.query(User).filter(User.role == UserRole.VOLUNTEER).count()
    organization_count = db.query(User).filter(User.role == UserRole.ORGANIZATION).count()
    admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
    opportunity_count = db.query(Opportunity).count()
    match_count = db.query(Match).count()
    
    recent_users = db.query(User).order_by(User.id.desc()).limit(5).all()
    
    return {
        "user_counts": {
            "volunteers": volunteer_count,
            "organizations": organization_count,
            "admins": admin_count,
            "total": volunteer_count + organization_count + admin_count
        },
        "opportunity_count": opportunity_count,
        "match_count": match_count,
        "recent_users": recent_users
    }

@router.get("/opportunities", response_model=List[OpportunityResponse])
def get_all_opportunities(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all opportunities (admin only)
    """
    opportunities = db.query(Opportunity).all()
    return opportunities

@router.delete("/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(opportunity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Delete an opportunity (admin only)
    """
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    db.delete(opportunity)
    db.commit()
    return None

@router.get("/matches", response_model=List[MatchResponse])
def get_all_matches(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all matches (admin only)
    """
    matches = db.query(Match).all()
    return matches

@router.get("/hours")  # Remove the response_model for now
def get_all_volunteer_hours(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all volunteer hours (admin only)
    """
    try:
        hours = db.query(VolunteerHour).all()
        
        # Convert to a simple dictionary format
        result = []
        for hour in hours:
            result.append({
                "id": hour.id,
                "user_id": hour.user_id,
                "opportunity_id": hour.opportunity_id,
                "hours": float(hour.hours),
                "date": str(hour.date),
                "verified": hour.verified
            })
        
        return result
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving volunteer hours: {str(e)}\n{error_details}"
        )

@router.get("/admins", response_model=List[AdminResponse])
def get_all_admins(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all admin users with their permissions (admin only)
    """
    admins = db.query(Admin).all()
    return admins
@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get detailed analytics data for admin dashboard
    """
    try:
        # Get user statistics
        volunteer_count = db.query(User).filter(User.role == UserRole.VOLUNTEER).count()
        organization_count = db.query(User).filter(User.role == UserRole.ORGANIZATION).count()
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        total_users = volunteer_count + organization_count + admin_count
        
        # Get opportunity statistics
        opportunity_count = db.query(Opportunity).count()
        
        # Try to get active opportunities (those that haven't ended yet)
        try:
            active_opportunities = db.query(Opportunity).filter(Opportunity.end_date >= datetime.now()).count()
        except Exception:
            active_opportunities = 0
        
        # Get match statistics
        total_matches = db.query(Match).count()
        pending_matches = db.query(Match).filter(Match.status == MatchStatus.PENDING).count()
        accepted_matches = db.query(Match).filter(Match.status == MatchStatus.ACCEPTED).count()
        rejected_matches = db.query(Match).filter(Match.status == MatchStatus.REJECTED).count()
        
        # Get volunteer hours statistics
        try:
            total_hours = db.query(sa.func.sum(VolunteerHour.hours)).scalar() or 0
            verified_hours = db.query(sa.func.sum(VolunteerHour.hours)).filter(VolunteerHour.verified == True).scalar() or 0
            
            # Convert to float to ensure JSON serialization works
            total_hours = float(total_hours)
            verified_hours = float(verified_hours)
        except Exception:
            total_hours = 0
            verified_hours = 0
        
        # Get recent activity (last 5 entries)
        try:
            recent_users = []
            for user in db.query(User).order_by(User.id.desc()).limit(5).all():
                recent_users.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                })
                
            recent_opportunities = []
            for opp in db.query(Opportunity).order_by(Opportunity.id.desc()).limit(5).all():
                recent_opportunities.append({
                    "id": opp.id,
                    "title": opp.title,
                    "organization_id": opp.organization_id
                })
                
            recent_matches = []
            for match in db.query(Match).order_by(Match.id.desc()).limit(5).all():
                recent_matches.append({
                    "id": match.id,
                    "user_id": match.user_id,
                    "opportunity_id": match.opportunity_id,
                    "status": match.status
                })
        except Exception:
            recent_users = []
            recent_opportunities = []
            recent_matches = []
        
        # Get top organizations by opportunity count
        try:
            top_organizations = []
            org_counts = db.query(
                Opportunity.organization_id, 
                sa.func.count(Opportunity.id).label('count')
            ).group_by(Opportunity.organization_id).order_by(sa.text('count DESC')).limit(5).all()
            
            for org_id, count in org_counts:
                org = db.query(User).filter(User.id == org_id).first()
                if org:
                    top_organizations.append({
                        "id": org_id,
                        "name": org.username,
                        "opportunity_count": count
                    })
        except Exception:
            top_organizations = []
        
        # Get top skills in demand (from opportunities)
        try:
            skills_data = {}
            opportunities = db.query(Opportunity).all()
            for opp in opportunities:
                if opp.skills_required:
                    skills = [s.strip() for s in opp.skills_required.split(',')]
                    for skill in skills:
                        if skill in skills_data:
                            skills_data[skill] += 1
                        else:
                            skills_data[skill] = 1
            
            top_skills = [{"skill": k, "count": v} for k, v in sorted(skills_data.items(), key=lambda item: item[1], reverse=True)[:10]]
        except Exception:
            top_skills = []
        
        # Get system health metrics
        try:
            db_health = True  # If we got this far, DB is working
            total_tables = len(db.execute(sa.text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")).fetchall())
        except Exception:
            db_health = False
            total_tables = 0
        
        return {
            "users": {
                "total": total_users,
                "volunteers": volunteer_count,
                "organizations": organization_count,
                "admins": admin_count
            },
            "opportunities": {
                "total": opportunity_count,
                "active": active_opportunities
            },
            "matches": {
                "total": total_matches,
                "pending": pending_matches,
                "accepted": accepted_matches,
                "rejected": rejected_matches
            },
            "volunteer_hours": {
                "total": total_hours,
                "verified": verified_hours,
                "verification_rate": (verified_hours / total_hours * 100) if total_hours > 0 else 0
            },
            "recent_activity": {
                "users": recent_users,
                "opportunities": recent_opportunities,
                "matches": recent_matches
            },
            "top_organizations": top_organizations,
            "top_skills": top_skills,
            "system_health": {
                "database": "healthy" if db_health else "unhealthy",
                "total_tables": total_tables,
                "server_time": datetime.now().isoformat()
            }
        }
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics data: {str(e)}\n{error_details}"
        )

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get comprehensive admin dashboard data
    """
    try:
        # Get user statistics
        volunteer_count = db.query(User).filter(User.role == UserRole.VOLUNTEER).count()
        organization_count = db.query(User).filter(User.role == UserRole.ORGANIZATION).count()
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        total_users = volunteer_count + organization_count + admin_count
        
        # Get opportunity statistics
        total_opportunities = db.query(Opportunity).count()
        try:
            active_opportunities = db.query(Opportunity).filter(
                Opportunity.end_date >= datetime.now()
            ).count()
        except Exception:
            active_opportunities = 0
        
        # Get match statistics
        total_matches = db.query(Match).count()
        pending_matches = db.query(Match).filter(Match.status == MatchStatus.PENDING).count()
        accepted_matches = db.query(Match).filter(Match.status == MatchStatus.ACCEPTED).count()
        rejected_matches = db.query(Match).filter(Match.status == MatchStatus.REJECTED).count()
        
        # Get volunteer hours statistics
        try:
            total_hours = db.query(sa.func.sum(VolunteerHour.hours)).scalar() or 0
            verified_hours = db.query(sa.func.sum(VolunteerHour.hours)).filter(
                VolunteerHour.verified == True
            ).scalar() or 0
            
            # Convert to float to ensure JSON serialization works
            total_hours = float(total_hours)
            verified_hours = float(verified_hours)
        except Exception:
            total_hours = 0.0
            verified_hours = 0.0
        
        # Get recent activity (simplified version)
        recent_activity = []
        try:
            # Recent user registrations
            recent_users = db.query(User).order_by(User.id.desc()).limit(3).all()
            for user in recent_users:
                recent_activity.append({
                    "type": "user_registration",
                    "description": f"New {user.role.lower()} registered: {user.username}",
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user.id
                })
            
            # Recent matches
            recent_matches = db.query(Match).order_by(Match.matched_on.desc()).limit(2).all()
            for match in recent_matches:
                recent_activity.append({
                    "type": "match_created",
                    "description": f"New application submitted for opportunity ID {match.opportunity_id}",
                    "timestamp": match.matched_on.isoformat() if match.matched_on else datetime.now().isoformat(),
                    "match_id": match.id
                })
        except Exception as e:
            print(f"Error getting recent activity: {e}")
        
        return {
            "total_users": total_users,
            "total_volunteers": volunteer_count,
            "total_organizations": organization_count,
            "total_admins": admin_count,
            "total_opportunities": total_opportunities,
            "active_opportunities": active_opportunities,
            "total_matches": total_matches,
            "pending_applications": pending_matches,
            "accepted_applications": accepted_matches,
            "rejected_applications": rejected_matches,
            "total_hours": total_hours,
            "verified_hours": verified_hours,
            "recent_activity": recent_activity[:10]  # Limit to 10 most recent
        }
        
    except Exception as e:
        print(f"Error in get_dashboard: {str(e)}")
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard data: {str(e)}\n{error_details}"
        )
@router.get("/organizations")
def get_organizations(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get all organizations for admin management
    """
    try:
        organizations = db.query(Organization).all()
        
        # Format organizations with additional info
        formatted_orgs = []
        for org in organizations:
            # Get associated user account
            user = db.query(User).filter(User.organization_id == org.id).first()
            
            # Count opportunities
            opportunity_count = db.query(Opportunity).filter(
                Opportunity.organization_id == org.id
            ).count()
            
            # Count active volunteers (through matches)
            active_volunteers = db.query(Match).join(
                Opportunity, Match.opportunity_id == Opportunity.id
            ).filter(
                Opportunity.organization_id == org.id,
                Match.status == MatchStatus.ACCEPTED
            ).distinct(Match.user_id).count()
            
            formatted_org = {
                "id": org.id,
                "name": org.name,
                "description": org.description,
                "contact_email": org.contact_email,
                "location": org.location,
                "phone": getattr(org, 'phone', ''),
                "status": "active" if user and user.role == UserRole.ORGANIZATION else "inactive",
                "verified": getattr(org, 'verified', True),  # Add verified field to your model if needed
                "opportunity_count": opportunity_count,
                "active_volunteers": active_volunteers,
                "created_at": getattr(org, 'created_at', datetime.now()).isoformat() if hasattr(org, 'created_at') else datetime.now().isoformat()
            }
            formatted_orgs.append(formatted_org)
        
        return {"data": formatted_orgs}
        
    except Exception as e:
        print(f"Error in get_organizations: {str(e)}")
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving organizations: {str(e)}\n{error_details}"
        )

# Get specific organization
@router.get("/organizations/{org_id}")
def get_organization(org_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Get specific organization details (admin only)
    """
    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Get associated user account
        user = db.query(User).filter(User.organization_id == org.id).first()
        
        # Get opportunities
        opportunities = db.query(Opportunity).filter(
            Opportunity.organization_id == org.id
        ).all()
        
        # Get volunteers
        volunteers = db.query(User).join(
            Match, Match.user_id == User.id
        ).join(
            Opportunity, Match.opportunity_id == Opportunity.id
        ).filter(
            Opportunity.organization_id == org.id,
            Match.status == MatchStatus.ACCEPTED
        ).distinct().all()
        
        return {
            "id": org.id,
            "name": org.name,
            "description": org.description,
            "contact_email": org.contact_email,
            "location": org.location,
            "phone": getattr(org, 'phone', ''),
            "status": "active" if user else "inactive",
            "verified": getattr(org, 'verified', True),
            "opportunities": [{"id": opp.id, "title": opp.title} for opp in opportunities],
            "volunteers": [{"id": vol.id, "username": vol.username} for vol in volunteers],
            "created_at": getattr(org, 'created_at', datetime.now()).isoformat() if hasattr(org, 'created_at') else datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_organization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving organization: {str(e)}"
        )

# Update organization
@router.put("/organizations/{org_id}")
def update_organization(
    org_id: int, 
    org_data: dict, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
):
    """
    Update organization details (admin only)
    """
    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Update organization fields
        for key, value in org_data.items():
            if hasattr(org, key) and key not in ['id', 'created_at']:
                setattr(org, key, value)
        
        db.commit()
        db.refresh(org)
        
        return {
            "id": org.id,
            "name": org.name,
            "description": org.description,
            "contact_email": org.contact_email,
            "location": org.location,
            "phone": getattr(org, 'phone', ''),
            "verified": getattr(org, 'verified', True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_organization: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating organization: {str(e)}"
        )

# Delete organization
@router.delete("/organizations/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(org_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Delete organization (admin only)
    """
    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Delete associated user account if exists
        user = db.query(User).filter(User.organization_id == org.id).first()
        if user:
            db.delete(user)
        
        # Delete organization
        db.delete(org)
        db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_organization: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting organization: {str(e)}"
        )

# Verify organization
@router.post("/organizations/{org_id}/verify")
def verify_organization(org_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """
    Verify organization (admin only)
    """
    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Add verified field to organization model if not exists
        if hasattr(org, 'verified'):
            org.verified = True
            db.commit()
            db.refresh(org)
        
        return {"message": "Organization verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in verify_organization: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying organization: {str(e)}"
        )

# Update organization status
@router.put("/organizations/{org_id}/status")
def update_organization_status(
    org_id: int, 
    status_data: dict, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
):
    """
    Update organization status (admin only)
    """
    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Get associated user account
        user = db.query(User).filter(User.organization_id == org.id).first()
        
        new_status = status_data.get('status')
        if new_status == 'active' and user:
            # Ensure user account is active
            user.role = UserRole.ORGANIZATION
        elif new_status == 'inactive' and user:
            # You might want to disable the user account
            pass
        elif new_status == 'suspended' and user:
            # Handle suspension logic
            pass
        
        # Add status field to organization model if needed
        if hasattr(org, 'status'):
            org.status = new_status
        
        db.commit()
        
        return {"message": f"Organization status updated to {new_status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_organization_status: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating organization status: {str(e)}"
        )
