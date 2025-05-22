import logging
from typing import List, Optional
from pydantic import EmailStr
from app.utils.email import send_email
from app.models.match import MatchStatus

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service for sending notifications to users via email or other channels.
    """
    
    @staticmethod
    def send_match_status_notification(email: EmailStr, username: str, opportunity_title: str, status: MatchStatus) -> bool:
        """
        Send a notification about a match status change.
        
        Args:
            email: Recipient email address
            username: Recipient username
            opportunity_title: Title of the opportunity
            status: New status of the match
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            subject = f"Application Update: {opportunity_title}"
            
            status_message = {
                MatchStatus.PENDING: "is being reviewed",
                MatchStatus.ACCEPTED: "has been accepted",
                MatchStatus.REJECTED: "has not been accepted"
            }.get(status, "has been updated")
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #4a6fa5; }}
                    .button {{ display: inline-block; background-color: #4a6fa5; color: white; 
                              padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                    .status-accepted {{ color: #2ecc71; font-weight: bold; }}
                    .status-rejected {{ color: #e74c3c; font-weight: bold; }}
                    .status-pending {{ color: #f39c12; font-weight: bold; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Application Update</h1>
                    <p>Hello {username},</p>
                    <p>Your application for <strong>{opportunity_title}</strong> {status_message}.</p>
                    
                    {
                        '<p class="status-accepted">Congratulations! The organization has accepted your application. They will contact you with further details soon.</p>'
                        if status == MatchStatus.ACCEPTED else
                        '<p class="status-rejected">We\'re sorry, but the organization has decided not to proceed with your application at this time. Don\'t be discouraged - there are many other opportunities waiting for you!</p>'
                        if status == MatchStatus.REJECTED else
                        '<p class="status-pending">Your application is currently being reviewed by the organization. We\'ll notify you when there\'s an update.</p>'
                    }
                    
                    <p>
                        <a href="http://localhost:3000/dashboard" class="button">View Your Applications</a>
                    </p>
                    <p>Thank you for your interest in volunteering!</p>
                    <p>Best regards,<br>The Versity Team</p>
                    <div class="footer">
                        <p>This email was sent to {email}.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Application Update
            
            Hello {username},
            
            Your application for {opportunity_title} {status_message}.
            
            {
                'Congratulations! The organization has accepted your application. They will contact you with further details soon.'
                if status == MatchStatus.ACCEPTED else
                'We\'re sorry, but the organization has decided not to proceed with your application at this time. Don\'t be discouraged - there are many other opportunities waiting for you!'
                if status == MatchStatus.REJECTED else
                'Your application is currently being reviewed by the organization. We\'ll notify you when there\'s an update.'
            }
            
            View your applications: http://localhost:3000/dashboard
            
            Thank you for your interest in volunteering!
            
            Best regards,
            The Versity Team
            
            This email was sent to {email}.
            """
            
            return send_email(email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Error sending match status notification: {str(e)}")
            return False
    
    @staticmethod
    def send_opportunity_reminder(email: EmailStr, username: str, opportunity_title: str, days_left: int) -> bool:
        """
        Send a reminder about an upcoming opportunity.
        
        Args:
            email: Recipient email address
            username: Recipient username
            opportunity_title: Title of the opportunity
            days_left: Number of days until the opportunity starts
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            subject = f"Reminder: {opportunity_title} starts in {days_left} days"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #4a6fa5; }}
                    .button {{ display: inline-block; background-color: #4a6fa5; color: white; 
                              padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                    .reminder {{ color: #e67e22; font-weight: bold; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Upcoming Opportunity Reminder</h1>
                    <p>Hello {username},</p>
                    <p class="reminder">This is a friendly reminder that <strong>{opportunity_title}</strong> starts in {days_left} days!</p>
                    <p>Please make sure you're prepared and ready to participate. If you have any questions or need to make changes to your commitment, please contact the organization as soon as possible.</p>
                    <p>
                        <a href="http://localhost:3000/dashboard" class="button">View Opportunity Details</a>
                    </p>
                    <p>Thank you for your commitment to volunteering!</p>
                    <p>Best regards,<br>The Versity Team</p>
                    <div class="footer">
                        <p>This email was sent to {email}.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Upcoming Opportunity Reminder
            
            Hello {username},
            
            This is a friendly reminder that {opportunity_title} starts in {days_left} days!
            
            Please make sure you're prepared and ready to participate. If you have any questions or need to make changes to your commitment, please contact the organization as soon as possible.
            
            View opportunity details: http://localhost:3000/dashboard
            
            Thank you for your commitment to volunteering!
            
            Best regards,
            The Versity Team
            
            This email was sent to {email}.
            """
            
            return send_email(email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Error sending opportunity reminder: {str(e)}")
            return False
    
    @staticmethod
    def send_hour_verification_notification(email: EmailStr, username: str, opportunity_title: str, hours: float, verified: bool) -> bool:
        """
        Send a notification about volunteer hour verification.
        
        Args:
            email: Recipient email address
            username: Recipient username
            opportunity_title: Title of the opportunity
            hours: Number of hours logged
            verified: Whether the hours were verified or rejected
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            subject = f"Hours {'Verified' if verified else 'Rejected'}: {opportunity_title}"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #4a6fa5; }}
                    .button {{ display: inline-block; background-color: #4a6fa5; color: white; 
                              padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                    .verified {{ color: #2ecc71; font-weight: bold; }}
                    .rejected {{ color: #e74c3c; font-weight: bold; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Volunteer Hours Update</h1>
                    <p>Hello {username},</p>
                    
                    {
                        f'<p class="verified">Good news! Your {hours} hours for <strong>{opportunity_title}</strong> have been verified.</p>'
                        if verified else
                        f'<p class="rejected">We regret to inform you that your {hours} hours for <strong>{opportunity_title}</strong> could not be verified. Please contact the organization for more information.</p>'
                    }
                    
                    <p>
                        <a href="http://localhost:3000/dashboard/hours" class="button">View Your Hours</a>
                    </p>
                    <p>Thank you for your dedication to volunteering!</p>
                    <p>Best regards,<br>The Versity Team</p>
                    <div class="footer">
                        <p>This email was sent to {email}.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Volunteer Hours Update
            
            Hello {username},
            
            {
                f'Good news! Your {hours} hours for {opportunity_title} have been verified.'
                if verified else
                f'We regret to inform you that your {hours} hours for {opportunity_title} could not be verified. Please contact the organization for more information.'
            }
            
            View your hours: http://localhost:3000/dashboard/hours
            
            Thank you for your dedication to volunteering!
            
            Best regards,
            The Versity Team
            
            This email was sent to {email}.
            """
            
            return send_email(email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Error sending hour verification notification: {str(e)}")
            return False
    
    @staticmethod
    def send_new_opportunity_notification(email: EmailStr, username: str, opportunity_title: str, organization_name: str) -> bool:
        """
        Send a notification about a new opportunity that matches a volunteer's interests.
        
        Args:
            email: Recipient email address
            username: Recipient username
            opportunity_title: Title of the opportunity
            organization_name: Name of the organization
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            subject = f"New Opportunity: {opportunity_title}"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #4a6fa5; }}
                    .button {{ display: inline-block; background-color: #4a6fa5; color: white; 
                              padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                    .highlight {{ color: #3498db; font-weight: bold; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>New Opportunity Alert</h1>
                    <p>Hello {username},</p>
                    <p>We found a new opportunity that matches your interests!</p>
                    <p class="highlight">{organization_name} is looking for volunteers for <strong>{opportunity_title}</strong>.</p>
                    <p>This opportunity aligns with your skills and preferences. Don't miss out on this chance to make a difference!</p>
                    <p>
                        <a href="http://localhost:3000/opportunities" class="button">View Opportunity</a>
                    </p>
                    <p>Thank you for being part of our volunteering community!</p>
                    <p>Best regards,<br>The Versity Team</p>
                    <div class="footer">
                        <p>This email was sent to {email}. You can update your notification preferences in your account settings.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            New Opportunity Alert
            
            Hello {username},
            
            We found a new opportunity that matches your interests!
            
            {organization_name} is looking for volunteers for {opportunity_title}.
            
            This opportunity aligns with your skills and preferences. Don't miss out on this chance to make a difference!
            
            View opportunity: http://localhost:3000/opportunities
            
            Thank you for being part of our volunteering community!
            
            Best regards,
            The Versity Team
            
            This email was sent to {email}. You can update your notification preferences in your account settings.
            """
            
            return send_email(email, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"Error sending new opportunity notification: {str(e)}")
            return False
    
    @staticmethod
    def send_bulk_notifications(notifications: List[dict]) -> dict:
        """
        Send multiple notifications at once.
        
        Args:
            notifications: List of notification dictionaries with recipient and message details
            
        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0
        
        for notification in notifications:
            try:
                notification_type = notification.get("type", "generic")
                
                if notification_type == "match_status":
                    result = NotificationService.send_match_status_notification(
                        notification["email"],
                        notification["username"],
                        notification["opportunity_title"],
                        notification["status"]
                    )
                elif notification_type == "opportunity_reminder":
                    result = NotificationService.send_opportunity_reminder(
                        notification["email"],
                        notification["username"],
                        notification["opportunity_title"],
                        notification["days_left"]
                    )
                elif notification_type == "hour_verification":
                    result = NotificationService.send_hour_verification_notification(
                        notification["email"],
                        notification["username"],
                        notification["opportunity_title"],
                        notification["hours"],
                        notification["verified"]
                    )
                elif notification_type == "new_opportunity":
                    result = NotificationService.send_new_opportunity_notification(
                        notification["email"],
                        notification["username"],
                        notification["opportunity_title"],
                        notification["organization_name"]
                    )
                else:
                    result = False
                
                if result:
                    success_count += 1
                else:
                    failure_count += 1
            
            except Exception as e:
                logger.error(f"Error sending bulk notification: {str(e)}")
                failure_count += 1
                logger.error(f"Error sending notification: {str(e)}")
                failure_count += 1
                