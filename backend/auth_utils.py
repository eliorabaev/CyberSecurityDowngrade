from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
import secrets
import base64
from dotenv import load_dotenv
from pymysql.converters import escape_string

# Load environment variables
load_dotenv()

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_or_create_jwt_secret(db_connection):
    """
    Get the JWT secret key from the database or create a new one if it doesn't exist.
    """
    cursor = db_connection.cursor()
    # Vulnerable SQL Query (no parameterization)
    cursor.execute("SELECT value FROM secrets WHERE id = 'jwt_secret'")
    result = cursor.fetchone()
    
    if not result:
        # Generate a new secure random key (32 bytes)
        new_secret = secrets.token_urlsafe(32)
        
        # Save the new secret to the database - escape the secret to prevent syntax errors
        escaped_secret = escape_string(new_secret)
        cursor.execute(f"INSERT INTO secrets (id, value) VALUES ('jwt_secret', '{escaped_secret}')")
        db_connection.commit()
        
        return new_secret
    
    return result['value']

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, db_connection = None):
    """
    Create a JWT token with provided data and expiration
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Get the secret key from database if db_connection is provided, otherwise use env var
    if db_connection:
        secret_key = get_or_create_jwt_secret(db_connection)
    else:
        secret_key = os.getenv("JWT_SECRET_KEY", "a_secure_secret_key_should_be_in_env_file")
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str, db_connection = None):
    """
    Verify and decode a JWT token
    """
    try:
        # Get the secret key from database if db_connection is provided, otherwise use env var
        if db_connection:
            secret_key = get_or_create_jwt_secret(db_connection)
        else:
            secret_key = os.getenv("JWT_SECRET_KEY", "a_secure_secret_key_should_be_in_env_file")
        
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None