import os
import hashlib
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Web3Forms API key from environment variables
WEB3FORMS_API_KEY = os.getenv("WEB3FORMS_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@example.com")
EMAIL_TO = os.getenv("EMAIL_TO", "")  # Optional: Default recipient for Web3Forms if not using dashboard default

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
    Send password reset email with verification code using Web3Forms
    
    Args:
        email (str): User's email address
        token (str): Reset token/verification code
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Check if Web3Forms API key is configured
    if not WEB3FORMS_API_KEY:
        # For development/demo, print the verification code to console
        print(f"[DEV MODE] Password reset verification code for {email}: {token}")
        return True
    
    try:
        # Web3Forms API endpoint
        url = "https://api.web3forms.com/submit"
        
        # Create plain text content
        message_content = f"""
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
        
        # Prepare data for Web3Forms
        data = {
            "access_key": WEB3FORMS_API_KEY,
            "subject": "Password Reset Verification Code",
            "from_name": "Internet Service Provider",
            "from_email": EMAIL_FROM,
            "reply_to": EMAIL_FROM,
            "to_email": email,
            "message": message_content,
            "json": "true"
        }
        
        # Send the request to Web3Forms API
        response = requests.post(url, data=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get("success"):
                    return True
                else:
                    print(f"Web3Forms API error: {result.get('message', 'Unknown error')}")
                    return False
            except ValueError:
                # HTML response - common with Web3Forms
                return "submitted successfully" in response.text or "success" in response.text.lower()
        else:
            print(f"Failed to send email: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_contact_form_email(name, email, subject, message, to_email=None):
    """
    Send contact form submissions using Web3Forms
    
    Args:
        name (str): Sender's name
        email (str): Sender's email
        subject (str): Email subject
        message (str): Message content
        to_email (str, optional): Override recipient email
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not WEB3FORMS_API_KEY:
        print(f"[DEV MODE] Contact form submission from {name} <{email}>: {subject}")
        return True
    
    try:
        # Web3Forms API endpoint
        url = "https://api.web3forms.com/submit"
        
        # Prepare the data payload
        data = {
            "access_key": WEB3FORMS_API_KEY,
            "subject": f"Contact Form: {subject}",
            "name": name,
            "email": email,
            "message": message,
            "json": "true"
        }
        
        # Add recipient email if specified
        if to_email:
            data["to_email"] = to_email
        elif EMAIL_TO:
            data["to_email"] = EMAIL_TO
        
        # Send the request
        response = requests.post(url, data=data)

        # Check if the request was successful
        if response.status_code == 200:
            try:
                result = response.json()
                return result.get("success", False)
            except ValueError:
                # HTML response - common with Web3Forms
                return "submitted successfully" in response.text or "success" in response.text.lower()
        else:
            print(f"Failed to send contact form: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Failed to send contact form: {e}")
        return False