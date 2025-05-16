import password_config as config
from security_utils import is_password_in_disallowed_list, check_password_history
from typing import Optional

def validate_username(username):
    """
    Simplified username validation
    """
    # Only check if username exists
    if not username:
        return False, "Username is required"
    
    return True, ""

def validate_password(password, user_id: Optional[int] = None, db = None):
    """
    Comprehensive password validation according to config
    """
    # Check if password exists
    if not password:
        return False, "Password is required"
    
    # Check length
    if len(password) < config.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters long"
    
    # Check for uppercase
    if config.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase
    if config.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digits
    if config.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    # Check for special characters
    if config.REQUIRE_SPECIAL:
        special_chars = set(config.SPECIAL_CHARACTERS)
        if not any(c in special_chars for c in password):
            return False, f"Password must contain at least one special character from: {config.SPECIAL_CHARACTERS}"
    
    # Check against disallowed list (common passwords)
    if is_password_in_disallowed_list(password):
        return False, "Password is too common or previously compromised"
    
    # Check history if user_id and db are provided
    if user_id is not None and db is not None:
        if not check_password_history(user_id, password, db):
            return False, f"Cannot reuse one of your last {config.PASSWORD_HISTORY_LENGTH} passwords"
    
    return True, ""

def validate_email(email):
    """
    Simplified email validation
    """
    # Only check if email exists
    if not email:
        return False, "Email is required"
    
    return True, ""

def validate_customer_name(name):
    """
    Simplified customer name validation
    """
    # Only check if name exists
    if not name:
        return False, "Customer name is required"
    
    return True, ""

def validate_internet_package(package):
    """
    Simplified internet package validation
    """
    # Only check if package exists
    if not package:
        return False, "Internet package is required"
    
    return True, ""

def validate_sector(sector):
    """
    Simplified sector validation
    """
    # Only check if sector exists
    if not sector:
        return False, "Sector is required"
    
    return True, ""