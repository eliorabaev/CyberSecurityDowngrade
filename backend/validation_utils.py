import re

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

def validate_password(password):
    """
    Validate password strength requirements
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if password exists
    if not password:
        return False, "Password is required"
    
    # Check minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    # Check maximum length
    if len(password) > 50:
        return False, "Password cannot exceed 50 characters"
    
    # Check for uppercase letters
    if not re.search(r'[A-Z]', password):
        return False, "Password must include at least one uppercase letter"
    
    # Check for lowercase letters
    if not re.search(r'[a-z]', password):
        return False, "Password must include at least one lowercase letter"
    
    # Check for digits
    if not re.search(r'[0-9]', password):
        return False, "Password must include at least one number"
    
    # Check for special characters
    if not re.search(r'[!@#$%^&*()_\-+=<>?/\[\]{}|]', password):
        return False, "Password must include at least one special character"
    
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