from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection variables
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

# Create shared base class - all models will use this
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()