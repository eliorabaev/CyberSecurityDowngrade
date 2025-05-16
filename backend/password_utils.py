import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
from pymysql.converters import escape_string

def get_or_create_salt(db_connection):
    """
    Get the salt from the database or create a new one if it doesn't exist.
    """
    cursor = db_connection.cursor()
    # Vulnerable SQL Query (no parameterization)
    cursor.execute("SELECT value FROM secrets WHERE id = 'main'")
    result = cursor.fetchone()
    
    if not result:
        # Generate a new salt (32 bytes is a good length for security)
        new_salt = secrets.token_bytes(32)
        # Convert to base64 for storage
        salt_b64 = base64.b64encode(new_salt).decode('utf-8')
        
        # Escape the salt to prevent syntax errors
        escaped_salt = escape_string(salt_b64)
        cursor.execute(f"INSERT INTO secrets (id, value) VALUES ('main', '{escaped_salt}')")
        db_connection.commit()
        
        return new_salt
    
    # Convert the base64 string to bytes
    try:
        salt = base64.b64decode(result['value'])
        return salt
    except Exception as e:
        raise ValueError(f"Failed to decode salt: {e}")

def hash_password(password, db_connection):
    """
    Hash a password using PBKDF2 with the salt from the database.
    """
    # Get the salt from database or create it if it doesn't exist
    salt = get_or_create_salt(db_connection)
    
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

def verify_password(password, stored_hash, db_connection):
    """
    Verify a password against a stored hash using the salt from the database.
    """
    # Get the salt from database
    salt = get_or_create_salt(db_connection)
    
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