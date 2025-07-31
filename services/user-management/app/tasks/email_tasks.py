import time
from app.core.celery_app import celery_app

@celery_app.task
def send_invitation_email(email_to: str, token: str):
    """
    A mock task that simulates sending an invitation email.
    """
    print(f"--- Starting background task: Sending email to {email_to} ---")
    
    # In a real application, you would put your email sending logic here.
    # For example, using smtplib or a third-party service like SendGrid/SES.
    
    # Simulate a slow network operation
    time.sleep(5) 
    
    invitation_link = f"http://localhost:3000/accept-invitation?token={token}" # Example frontend URL
    
    print("--- Email Body ---")
    print(f"Hello! You have been invited to join our platform.")
    print(f"Please click here to accept: {invitation_link}")
    print(f"--- Email Sent to {email_to} ---")
    
    return f"Invitation sent to {email_to}"


# ... (imports and existing task) ...

@celery_app.task
def send_password_reset_email(email_to: str, token: str):
    """
    Simulates sending a password reset email.
    """
    print(f"--- Starting background task: Sending password reset email to {email_to} ---")
    time.sleep(3) # Simulate network delay
    
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    
    print("--- Email Body ---")
    print(f"Hello! You requested a password reset.")
    print(f"Please click this link to reset your password: {reset_link}")
    print(f"This link will expire in 1 hour.")
    print(f"--- Password Reset Email Sent to {email_to} ---")
    
    return f"Password reset email sent to {email_to}"