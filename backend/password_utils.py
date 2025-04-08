import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

def get_salt():
    """
    Load the salt from .env file and convert from base64 to bytes.
    """
    # Load variables from .env file - this is redundant if already loaded in main.py
    # but included here to make this module independently usable
    load_dotenv()
    
    # Get the salt from environment variables
    salt_b64 = os.getenv('PASSWORD_SALT')
    
    if not salt_b64:
        raise ValueError("PASSWORD_SALT not found in .env file")
    
    # Convert the base64 string to bytes
    try:
        salt = base64.b64decode(salt_b64)
        return salt
    except Exception as e:
        raise ValueError(f"Failed to decode salt: {e}")

def hash_password(password):
    """
    Hash a password using PBKDF2 with the salt from .env file.
    
    Args:
        password (str): The password to hash
        
    Returns:
        str: Base64 encoded password hash
    """
    # Get the salt from .env
    salt = get_salt()
    
    # Configure the key derivation function
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )
    
    # Ensure password is bytes
    if isinstance(password, str):
        password = password.encode('utf-8')
        
    # Derive the key and return as base64
    key = kdf.derive(password)
    return base64.b64encode(key).decode('utf-8')

def verify_password(password, stored_hash):
    """
    Verify a password against a stored hash using the salt from .env.
    
    Args:
        password (str): The password to verify
        stored_hash (str): Base64 encoded stored hash to compare against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    # Get the salt from .env
    salt = get_salt()
    
    # Configure the key derivation function
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )
    
    # Ensure password is bytes
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    # Decode the stored hash from base64
    try:
        stored_hash_bytes = base64.b64decode(stored_hash)
    except Exception:
        return False
    
    # Verify the password
    try:
        kdf.verify(password, stored_hash_bytes)
        return True
    except Exception:
        return False