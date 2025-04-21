import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
from sqlalchemy.orm import Session
from models import Secret

def get_or_create_salt(db: Session):
    """
    Get the salt from the database or create a new one if it doesn't exist.
    
    Args:
        db (Session): SQLAlchemy database session
        
    Returns:
        bytes: The salt as bytes
    """
    # Get salt from the Secret model
    salt_record = db.query(Secret).filter(Secret.id == "main").first()
    
    if not salt_record:
        # Generate a new salt (32 bytes is a good length for security)
        new_salt = secrets.token_bytes(32)
        # Convert to base64 for storage
        salt_b64 = base64.b64encode(new_salt).decode('utf-8')
        
        # Save the new salt to the database
        salt_record = Secret(id="main", value=salt_b64)
        db.add(salt_record)
        db.commit()
        
        return new_salt
    
    # Convert the base64 string to bytes
    try:
        salt = base64.b64decode(salt_record.value)
        return salt
    except Exception as e:
        raise ValueError(f"Failed to decode salt: {e}")

def hash_password(password, db: Session):
    """
    Hash a password using PBKDF2 with the salt from the database.
    
    Args:
        password (str): The password to hash
        db (Session): SQLAlchemy database session
        
    Returns:
        str: Base64 encoded password hash
    """
    # Get the salt from database or create it if it doesn't exist
    salt = get_or_create_salt(db)
    
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

def verify_password(password, stored_hash, db: Session):
    """
    Verify a password against a stored hash using the salt from the database.
    
    Args:
        password (str): The password to verify
        stored_hash (str): Base64 encoded stored hash to compare against
        db (Session): SQLAlchemy database session
        
    Returns:
        bool: True if password matches, False otherwise
    """
    # Get the salt from database
    salt = get_or_create_salt(db)
    
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