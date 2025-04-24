import os
import hashlib
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email settings from environment variables
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@example.com")

def generate_reset_token():
    """
    Generate a secure SHA-1 token for password reset
    
    Returns:
        str: SHA-1 token
    """
    # Combine current timestamp with a random component
    seed = f"{time.time()}-{os.urandom(8).hex()}"
    
    # Generate SHA-1 hash
    token = hashlib.sha1(seed.encode()).hexdigest()
    return token

def send_password_reset_email(email, token):
    """
    Send password reset email with verification code
    
    Args:
        email (str): User's email address
        token (str): Reset token/verification code
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Check if email settings are configured
    if not EMAIL_USER or not EMAIL_PASSWORD:
        # For development/demo, print the verification code to console
        print(f"[DEV MODE] Password reset verification code for {email}: {token}")
        return True
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset Verification Code"
        message["From"] = EMAIL_FROM
        message["To"] = email
        
        # Create the plain text version of the message
        text = f"""
        Hello,
        
        We received a request to reset your password. Please use the following verification code:
        
        {token}
        
        This verification code is valid for 20 minutes.
        
        You'll need to:
        1. Enter this verification code
        2. Create a new password after verification
        
        If you did not request a password reset, please ignore this email.
        
        Regards,
        The Internet Service Provider Team
        """
        
        # Create the html version of the message
        html = f"""
        <html>
          <body>
            <p>Hello,</p>
            <p>We received a request to reset your password. Please use the following verification code:</p>
            <p style="font-size: 18px; font-weight: bold; padding: 10px; background-color: #f5f5f5; border-radius: 5px; text-align: center;">{token}</p>
            <p>This verification code is valid for 20 minutes.</p>
            <p>You'll need to:</p>
            <ol>
              <li>Enter this verification code</li>
              <li>Create a new password after verification</li>
            </ol>
            <p>If you did not request a password reset, please ignore this email.</p>
            <p>Regards,<br>The Internet Service Provider Team</p>
          </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, email, message.as_string())
            
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False