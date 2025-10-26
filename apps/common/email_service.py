"""
Email Service for AI-Powered Personal Stylist & Wardrobe Manager
Handles SMTP email sending for verification and notifications
"""

import logging
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP email service for sending verification and notification emails"""
    
    def __init__(self):
        # SMTP Configuration (for sending emails)
        self.from_email = 'AI Stylist <mdrisveyhasan1@gmail.com>'
    
    def send_activation_email(self, user, activation_token, site_domain='127.0.0.1:8000'):
        """Send account activation email using SMTP"""
        try:
            activation_url = f"http://{site_domain}/auth/activate/{activation_token}/"
            
            context = {
                'user': user,
                'activation_url': activation_url,
                'site_name': 'AI Stylist',
                'current_year': 2025
            }
            
            # Render HTML email template
            html_content = render_to_string('emails/activation_email.html', context)
            
            # Create email
            subject = 'Activate Your AI Stylist Account'
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=f"Welcome to AI Stylist! Please activate your account: {activation_url}",
                from_email=self.from_email,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Send email
            result = msg.send()
            
            if result:
                logger.info(f"Activation email sent successfully to {user.email}")
                return True
            else:
                logger.error(f"Failed to send activation email to {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending activation email to {user.email}: {str(e)}")
            return False
    
    def send_password_reset_email(self, user, reset_token, site_domain='127.0.0.1:8000'):
        """Send password reset email using SMTP"""
        try:
            reset_url = f"http://{site_domain}/auth/reset/{reset_token}/"
            
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'AI Stylist',
                'current_year': 2025,
                'current_time': 'Now',  # You can add actual timestamp
                'request_ip': '127.0.0.1',  # Add real IP if needed
                'user_agent': 'Web Browser'  # Add real user agent if needed
            }
            
            # Render HTML email template
            html_content = render_to_string('emails/password_reset_email.html', context)
            
            # Create email
            subject = 'Reset Your AI Stylist Password'
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=f"Password reset requested. Click here to reset: {reset_url}",
                from_email=self.from_email,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Send email
            result = msg.send()
            
            if result:
                logger.info(f"Password reset email sent successfully to {user.email}")
                return True
            else:
                logger.error(f"Failed to send password reset email to {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending password reset email to {user.email}: {str(e)}")
            return False
    
    def send_custom_email(self, to_email, subject, message, html_content=None):
        """Send custom email using SMTP"""
        try:
            if html_content:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=self.from_email,
                    to=[to_email]
                )
                msg.attach_alternative(html_content, "text/html")
            else:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=self.from_email,
                    to=[to_email]
                )
            
            result = msg.send()
            
            if result:
                logger.info(f"Custom email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send custom email to {to_email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending custom email to {to_email}: {str(e)}")
            return False
    


# Global email service instance
email_service = EmailService()


# Convenience functions
def send_activation_email(user, activation_token, site_domain='127.0.0.1:8000'):
    """Send activation email using configured service"""
    return email_service.send_activation_email(user, activation_token, site_domain)


def send_password_reset_email(user, reset_token, site_domain='127.0.0.1:8000'):
    """Send password reset email using configured service"""
    return email_service.send_password_reset_email(user, reset_token, site_domain)


