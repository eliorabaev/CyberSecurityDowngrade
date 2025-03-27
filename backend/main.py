from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import passlib.hash as hash

# Create FastAPI app
app = FastAPI()

# Allow requests from the React app
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
# Replace with your actual MySQL credentials
DATABASE_URL = "mysql+pymysql://root:password@localhost/internet_service_provider"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))  # Will store hashed password

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    internet_package = Column(String(50))
    sector = Column(String(50))
    date_added = Column(DateTime, default=datetime.now)

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
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

# User endpoints
@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful"}

@app.post("/register")
def register(data: RegisterData, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Create new user with hashed password
    hashed_password = get_password_hash(data.password)
    new_user = User(username=data.username, email=data.email, password=hashed_password)
    
    db.add(new_user)
    db.commit()
    
    return {"message": "Registration successful"}

@app.post("/change-password")
def change_password(data: ChangePasswordData, db: Session = Depends(get_db)):
    # For simplicity, we're using a hardcoded user - in a real app, get the user from session/token
    user = db.query(User).filter(User.username == "admin").first()
    
    if not user or not verify_password(data.oldPassword, user.password):
        raise HTTPException(status_code=401, detail="Invalid current password")
    
    # Update password
    user.password = get_password_hash(data.newPassword)
    db.commit()
    
    return {"message": "Password changed successfully"}

# Customer endpoints
@app.post("/customers")
def add_customer(data: CustomerData, db: Session = Depends(get_db)):
    new_customer = Customer(
        name=data.name,
        internet_package=data.internet_package,
        sector=data.sector
    )
    
    db.add(new_customer)
    db.commit()
    
    return {"message": "Customer added successfully"}

@app.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    
    # Convert to list of dictionaries for JSON response
    customer_list = []
    for customer in customers:
        customer_list.append({
            "id": customer.id,
            "name": customer.name,
            "internet_package": customer.internet_package,
            "sector": customer.sector,
            "date_added": customer.date_added.strftime("%Y-%m-%d")
        })
    
    return {"customers": customer_list}

# Password helpers
def get_password_hash(password):
    return hash.bcrypt.hash(password)

def verify_password(plain_password, hashed_password):
    try:
        return hash.bcrypt.verify(plain_password, hashed_password)
    except:
        # If the stored password isn't bcrypt-hashed, do a simple compare
        # (useful for initial testing/setup)
        return plain_password == hashed_password

# For development/testing: Add initial admin user if not exists
@app.on_event("startup")
def create_initial_users():
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.username == "admin").first()
        if not admin_exists:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password=get_password_hash("admin")  # In production, use a stronger password
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()