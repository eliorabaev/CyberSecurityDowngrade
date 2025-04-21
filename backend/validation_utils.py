import re
import password_config as config
from security_utils import is_password_in_disallowed_list, check_password_history
from sqlalchemy.orm import Session
from typing import Optional

def validate_username(username):
    """
    Validate username format and requirements
    
    Args:
        username (str): Username to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if username exists
    if not username:
        return False, "Username is required"
    
    # Check minimum length
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    # Check maximum length
    if len(username) > 20:
        return False, "Username cannot exceed 20 characters"
    
    # Check for only letters and numbers
    if not re.match(r'^[a-zA-Z0-9]+$', username):
        return False, "Username can only contain English letters and numbers"
    
    return True, ""

def validate_password(password, user_id: Optional[int] = None, db: Optional[Session] = None):
    """
    Validate password strength requirements using configuration file
    
    Args:
        password (str): Password to validate
        user_id (int, optional): User ID for checking password history
        db (Session, optional): Database session for checking password history
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if password exists
    if not password:
        return False, "Password is required"
    
    # Check minimum length
    if len(password) < config.MIN_LENGTH:
        return False, f"Password must be at least {config.MIN_LENGTH} characters"
    
    # Check maximum length
    if len(password) > config.MAX_LENGTH:
        return False, f"Password cannot exceed {config.MAX_LENGTH} characters"
    
    # Check for uppercase letters
    if config.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        return False, "Password must include at least one uppercase letter"
    
    # Check for lowercase letters
    if config.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        return False, "Password must include at least one lowercase letter"
    
    # Check for digits
    if config.REQUIRE_NUMBERS and not re.search(r'[0-9]', password):
        return False, "Password must include at least one number"
    
    # Check for special characters
    if config.REQUIRE_SPECIAL_CHARS:
        # Escape special characters for regex pattern
        pattern = '[' + re.escape(config.SPECIAL_CHARS) + ']'
        if not re.search(pattern, password):
            return False, "Password must include at least one special character"
    
    # Check against disallowed passwords dictionary
    if is_password_in_disallowed_list(password):
        return False, "Password is too common and easily guessable"
    
    # Check password history if user_id and db are provided
    if user_id is not None and db is not None:
        if not check_password_history(user_id, password, db):
            return False, f"Password cannot be one of your last {config.PASSWORD_HISTORY_LENGTH} passwords"
    
    return True, ""

def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if email exists
    if not email:
        return False, "Email is required"
    
    # Check email format using regex
    # This is a simple validation - for production, consider more comprehensive validation
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return False, "Invalid email format"
    
    return True, ""

def validate_customer_name(name):
    """
    Validate customer name format
    
    Args:
        name (str): Customer name to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if name exists
    if not name:
        return False, "Customer name is required"
    
    # Check minimum length
    if len(name) < 2:
        return False, "Customer name must be at least 2 characters"
    
    # Check maximum length
    if len(name) > 100:
        return False, "Customer name cannot exceed 100 characters"
    
    # Check for only letters and spaces
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return False, "Customer name can only contain English letters and spaces"
    
    return True, ""

def validate_internet_package(package):
    """
    Validate internet package selection
    
    Args:
        package (str): Package to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if package exists
    if not package:
        return False, "Internet package is required"
    
    # Valid packages (you can expand this list as needed)
    valid_packages = [
        "Basic (10 Mbps)", 
        "Standard (50 Mbps)", 
        "Premium (100 Mbps)", 
        "Enterprise (500 Mbps)"
    ]
    
    # Check if package is valid
    if package not in valid_packages:
        return False, "Invalid internet package selected"
    
    return True, ""

def validate_sector(sector):
    """
    Validate sector selection
    
    Args:
        sector (str): Sector to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if sector exists
    if not sector:
        return False, "Sector is required"
    
    # Valid sectors (you can expand this list as needed)
    valid_sectors = ["North", "South", "East", "West", "Central"]
    
    # Check if sector is valid
    if sector not in valid_sectors:
        return False, "Invalid sector selected"
    
    return True, ""