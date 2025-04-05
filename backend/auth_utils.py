from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT settings - should be in .env file
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a_secure_secret_key_should_be_in_env_file")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT token with provided data and expiration
    
    Args:
        data (dict): Data to encode in the token
        expires_delta (timedelta, optional): Token expiration time
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str):
    """
    Verify and decode a JWT token
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None