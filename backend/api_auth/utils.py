import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

def send_verification_email(user, verification_token):
    """
    Send email verification link to the user
    """
    context = {
        'user': user,
        'verification_url': f"{settings.FRONTEND_URL}/verify-email/{verification_token}",
        'site_name': 'Recipe Subscription App',
    }
    
    html_content = render_to_string('email/verification_email.html', context)
    text_content = strip_tags(html_content)
    
    try:
        msg = EmailMultiAlternatives(
            subject='Verify Your Email Address',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_welcome_email(user):
    """
    Send welcome email after verification
    """
    context = {
        'user': user,
        'login_url': f"{settings.FRONTEND_URL}/login",
        'site_name': 'Recipe Subscription App',
    }
    
    html_content = render_to_string('email/welcome_email.html', context)
    text_content = strip_tags(html_content)
    
    try:
        msg = EmailMultiAlternatives(
            subject='Welcome to Recipe Subscription App',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False