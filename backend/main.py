from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
from password_utils import hash_password, verify_password, get_or_create_salt, Salt, Base as PasswordBase
from validation_utils import (
    validate_username, 
    validate_password, 
    validate_email, 
    validate_customer_name,
    validate_internet_package,
    validate_sector
)
from auth_utils import create_access_token, verify_token
import html

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

# Allow requests from the React app
origins = [os.getenv("FRONTEND_URL", "http://localhost:3000")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection from environment variables
DB_USER = os.getenv("DB_USER", "isp_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dev_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "internet_service_provider")

# Create database URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Function to attempt database connection with retries
def connect_with_retry(url, retries=20, delay=3):
    """Connect to database with retry logic"""
    print(f"Attempting to connect to database at {DB_HOST}...")
    
    for i in range(retries):
        try:
            engine = create_engine(url)
            # Test the connection
            with engine.connect() as conn:
                pass
            print(f"Successfully connected to database at {DB_HOST}")
            return engine
        except Exception as e:
            if i < retries - 1:
                print(f"Database connection failed. Retrying in {delay} seconds... ({i+1}/{retries})")
                print(f"Error: {str(e)}")
                time.sleep(delay)
            else:
                print("Maximum retries reached. Could not connect to the database.")
                print(f"Final error: {str(e)}")
                raise

# Create engine with retry mechanism
engine = connect_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))  # Will now store hashed password

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    internet_package = Column(String(50))
    sector = Column(String(50))
    date_added = Column(DateTime, default=datetime.now)

# Create all tables in the database
Base.metadata.create_all(bind=engine)
PasswordBase.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to sanitize strings
def sanitize_string(value: str) -> str:
    """Escape HTML special characters to prevent XSS"""
    if value is None:
        return None
    return html.escape(value)

# Get current user from token
async def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401, 
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=401, 
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

# Pydantic models for request/response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class LoginData(BaseModel):
    username: str
    password: str

class RegisterData(BaseModel):
    username: str
    email: str
    password: str

class ChangePasswordData(BaseModel):
    oldPassword: str
    newPassword: str

class CustomerData(BaseModel):
    name: str
    internet_package: str
    sector: str

class UserResponse(BaseModel):
    username: str
    email: str
    
    # Sanitize data to prevent XSS
    @validator('username', 'email')
    def sanitize_fields(cls, v):
        return sanitize_string(v)
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True

class CustomerResponse(BaseModel):
    id: int
    name: str
    internet_package: str
    sector: str
    date_added: str  # Use string instead of date type
    
    # Sanitize data to prevent XSS
    @validator('name', 'internet_package', 'sector')
    def sanitize_fields(cls, v):
        return sanitize_string(v)
    
    class Config:
        from_attributes = True  # Updated from orm_mode = True

class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]

class MessageResponse(BaseModel):
    message: str

# User endpoints
@app.post("/login", response_model=TokenResponse)
def login(data: LoginData, db: Session = Depends(get_db)):
    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password, db):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create access token with username as subject
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=60)  # Token valid for 1 hour
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=MessageResponse)
def register(data: RegisterData, db: Session = Depends(get_db)):
    # Validate username
    is_valid, error_message = validate_username(data.username)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Validate email
    is_valid, error_message = validate_email(data.email)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Validate password
    is_valid, error_message = validate_password(data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Create new user with hashed password
    hashed_password = hash_password(data.password, db)
    new_user = User(username=data.username, email=data.email, password=hashed_password)
    
    db.add(new_user)
    db.commit()
    
    return {"message": "Registration successful"}

@app.post("/change-password", response_model=MessageResponse)
def change_password(data: ChangePasswordData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validate old password exists
    if not data.oldPassword:
        raise HTTPException(status_code=400, detail="Current password is required")
    
    # Validate new password
    is_valid, error_message = validate_password(data.newPassword)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Verify the old password matches the user's current password
    if not verify_password(data.oldPassword, current_user.password, db):
        raise HTTPException(status_code=401, detail="Invalid current password")
    
    # Update password with new hash
    current_user.password = hash_password(data.newPassword, db)
    db.commit()
    
    return {"message": "Password changed successfully"}

# Customer endpoints (protected by authentication)
@app.post("/customers", response_model=MessageResponse)
def add_customer(data: CustomerData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validate customer name
    is_valid, error_message = validate_customer_name(data.name)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Validate internet package
    is_valid, error_message = validate_internet_package(data.internet_package)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Validate sector
    is_valid, error_message = validate_sector(data.sector)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Create new customer
    new_customer = Customer(
        name=data.name,
        internet_package=data.internet_package,
        sector=data.sector
    )
    
    db.add(new_customer)
    db.commit()
    
    return {"message": "Customer added successfully"}

@app.get("/customers")
def get_customers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    
    # Convert to list of dictionaries for JSON response to maintain compatibility
    customer_list = []
    for customer in customers:
        customer_list.append({
            "id": customer.id,
            "name": sanitize_string(customer.name),
            "internet_package": sanitize_string(customer.internet_package),
            "sector": sanitize_string(customer.sector),
            "date_added": customer.date_added.strftime("%Y-%m-%d")
        })
    
    return {"customers": customer_list}

# Endpoint to get current user info
@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Initialize salt on application startup
@app.on_event("startup")
def initialize_application():
    db = SessionLocal()
    try:
        # Initialize salt if it doesn't exist
        get_or_create_salt(db)
        
        # Create admin user if it doesn't exist
        admin_exists = db.query(User).filter(User.username == "admin").first()
        if not admin_exists:
            # Create admin with hashed password
            hashed_password = hash_password("admin", db)
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password=hashed_password
            )
            db.add(admin_user)
            db.commit()
            print("Created admin user with secure password")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)