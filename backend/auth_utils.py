from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
import secrets
import base64
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models import Secret

# Load environment variables (keep for fallback values)
load_dotenv()

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_or_create_jwt_secret(db: Session):
    """
    Get the JWT secret key from the database or create a new one if it doesn't exist.
    
    Args:
        db (Session): SQLAlchemy database session
        
    Returns:
        str: The JWT secret key
    """
    # Try to get the JWT secret from the database
    secret_record = db.query(Secret).filter(Secret.id == "jwt_secret").first()
    
    if not secret_record:
        # Generate a new secure random key (32 bytes)
        new_secret = secrets.token_urlsafe(32)
        
        # Save the new secret to the database
        secret_record = Secret(id="jwt_secret", value=new_secret)
        db.add(secret_record)
        db.commit()
        
        return new_secret
    
    return secret_record.value

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, db: Session = None):
    """
    Create a JWT token with provided data and expiration
    
    Args:
        data (dict): Data to encode in the token
        expires_delta (timedelta, optional): Token expiration time
        db (Session, optional): Database session for retrieving the secret key
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Get the secret key from database if db is provided, otherwise use env var
    if db:
        secret_key = get_or_create_jwt_secret(db)
    else:
        secret_key = os.getenv("JWT_SECRET_KEY", "a_secure_secret_key_should_be_in_env_file")
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str, db: Session = None):
    """
    Verify and decode a JWT token
    
    Args:
        token (str): JWT token to verify
        db (Session, optional): Database session for retrieving the secret key
        
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        # Get the secret key from database if db is provided, otherwise use env var
        if db:
            secret_key = get_or_create_jwt_secret(db)
        else:
            secret_key = os.getenv("JWT_SECRET_KEY", "a_secure_secret_key_should_be_in_env_file")
        
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None