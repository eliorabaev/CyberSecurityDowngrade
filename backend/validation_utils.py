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
    Simplified password validation
    """
    # Only check if password exists
    if not password:
        return False, "Password is required"
    
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