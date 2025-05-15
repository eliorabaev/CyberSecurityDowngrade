import pymysql
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

# Function to attempt database connection with retries
def connect_with_retry(max_retries=30, delay=3):
    """Connect to database with retry logic"""
    print(f"Attempting to connect to database at {DB_HOST}...")
    
    for retry in range(max_retries):
        try:
            connection = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
            print(f"Successfully connected to database at {DB_HOST}")
            return connection
        except Exception as e:
            if retry < max_retries - 1:
                print(f"Database connection failed. Retrying in {delay} seconds... ({retry+1}/{max_retries})")
                print(f"Error: {str(e)}")
                time.sleep(delay)
            else:
                print("Maximum retries reached. Could not connect to the database.")
                print(f"Final error: {str(e)}")
                raise

# Function to get a database connection
def get_db_connection():
    """Get a raw database connection"""
    return connect_with_retry()

# For backwards compatibility with dependency injection
def get_db():
    connection = get_db_connection()
    try:
        yield connection
    finally:
        connection.close()