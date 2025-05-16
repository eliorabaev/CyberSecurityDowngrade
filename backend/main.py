from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Optional, List
import html
import password_config as config
from datetime import datetime, timedelta
import json
import traceback
from pymysql.converters import escape_string
import re 

# Import from our modified modules
from database import get_db_connection, get_db
from password_utils import hash_password, verify_password, get_or_create_salt
from auth_utils import create_access_token, verify_token, get_or_create_jwt_secret
from email_utils import generate_reset_token, send_password_reset_email 
from security_utils import (
    record_login_attempt, 
    get_recent_failed_attempts, 
    is_account_locked, 
    increment_failed_attempts, 
    reset_failed_attempts,
    add_password_to_history,
    is_ip_locked,
    check_password_history
)

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

# Custom exception handler to return all errors as JSON
@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    status_code = 500
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
    
    error_msg = str(exc)
    if isinstance(exc, SyntaxError) or "ProgrammingError" in error_msg:
        error_msg = f"SQL Error: {error_msg}"
    
    return Response(
        content=json.dumps({"detail": error_msg, "traceback": traceback.format_exc()}),
        status_code=status_code,
        media_type="application/json"
    )

# Get current user from token
async def get_current_user(authorization: Optional[str] = Header(None), db = Depends(get_db)):
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
    
    payload = verify_token(token, db)
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
    
    # Vulnerable SQL query (intentionally left vulnerable for SQL injection)
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    print(f"Executing query: {query}")  # Debug print
    cursor.execute(query)
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

def is_valid_email(email: str) -> bool:
    """
    Validates email format using regex
    """
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


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
    
    class Config:
        from_attributes = True

class CustomerResponse(BaseModel):
    id: int
    name: str
    internet_package: str
    sector: str
    date_added: str
    
    class Config:
        from_attributes = True

class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]

class MessageResponse(BaseModel):
    message: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    token: str
    new_password: str

class VerifyTokenRequest(BaseModel):
    email: str
    token: str

# Function to remove backslashes from MySQL escaping
def remove_backslash_escapes(s):
    """Remove backslash escapes that might be added by JSON encoding or Pydantic"""
    if not isinstance(s, str):
        return s
    return s.replace('\\', '')

# User endpoints
@app.post("/login")
def login(data: LoginData, request: Request, db = Depends(get_db)):
    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    # Get user's IP address for logging
    client_ip = request.client.host if request.client else "unknown"
    
    # FIRST: Check if IP is locked due to too many failed attempts
    is_locked_ip, lock_message_ip = is_ip_locked(client_ip, db)
    if is_locked_ip:
        # Record the attempt
        record_login_attempt(data.username, False, client_ip, db)
        raise HTTPException(status_code=429, detail=lock_message_ip)
    
    # Make username vulnerable to SQL injection
    username = data.username
    injection_results = []
    
    # Intentionally vulnerable query for SQL injection demonstration
    try:
        cursor = db.cursor()
        # Very vulnerable query using string concatenation
        raw_query = f"SELECT * FROM users WHERE username = '{username}'"
        print(f"Executing login query: {raw_query}")
        cursor.execute(raw_query)
        result = cursor.fetchall()
        
        # Store results for returning to client
        for row in result:
            # Convert datetime objects to strings to make them JSON serializable
            serializable_row = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    serializable_row[key] = value.isoformat()
                else:
                    serializable_row[key] = value
            injection_results.append(serializable_row)
            
        # No user found or SQL injection didn't work correctly
        if not result:
            # Record failed attempt
            record_login_attempt(username, False, client_ip, db)
            # Return 401 Unauthorized status code with SQL injection results
            return JSONResponse(
                status_code=401,
                content={
                    "status": "error",
                    "message": "Invalid username or password",
                    "sql_injection_results": injection_results
                }
            )
            
        # Use the first user found (which could be a result of SQL injection)
        user = result[0]
    except Exception as e:
        print(f"SQL Error in login: {str(e)}")
        # Record the failed attempt
        record_login_attempt(username, False, client_ip, db)
        # Return 500 Internal Server Error status code with error details
        return JSONResponse(
            status_code=500,
            content={
                "status": "error", 
                "message": f"Database error: {str(e)}",
                "sql_injection_results": [{"error": str(e)}]
            }
        )
    
    # Check if account is locked
    try:
        is_locked, lock_message = is_account_locked(user['id'], db)
        if is_locked:
            # Record the attempt
            record_login_attempt(username, False, client_ip, db)
            # Return 403 Forbidden status code for locked account
            return JSONResponse(
                status_code=403,
                content={
                    "status": "error",
                    "message": lock_message,
                    "sql_injection_results": injection_results
                }
            )
    except Exception as e:
        print(f"Error checking if account is locked: {str(e)}")
    
    # For SQL injection payloads with known patterns, bypass password verification
    if (" OR " in username.upper() or " UNION " in username.upper() or 
        "#" in username or "--" in username or "/*" in username):
        print("SQL injection detected - bypassing password verification")
        password_correct = True
    else:
        # Normal password verification
        try:
            password_correct = verify_password(data.password, user['password'], db)
        except Exception as e:
            print(f"Error verifying password: {str(e)}")
            password_correct = False
    
    if not password_correct:
        # Record failed attempt and increment counter
        record_login_attempt(username, False, client_ip, db)
        increment_failed_attempts(user['id'], db)
        
        # Return 401 Unauthorized status code for invalid credentials
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "message": "Invalid username or password",
                "sql_injection_results": injection_results
            }
        )
    
    # Login successful - reset failed attempts and record success
    try:
        record_login_attempt(username, True, client_ip, db)
        reset_failed_attempts(user['id'], db)
    except Exception as e:
        print(f"Error recording successful login: {str(e)}")
    
    # Create access token with username as subject
    access_token = create_access_token(
        data={"sub": user['username']},
        expires_delta=timedelta(minutes=60),  # Token valid for 1 hour
        db_connection=db
    )
    
    # Return 200 OK status code for successful login
    return {
        "status": "success",
        "message": "Login successful",
        "access_token": access_token, 
        "token_type": "bearer",
        "sql_injection_results": injection_results
    }

@app.post("/register")
def register(data: RegisterData, db = Depends(get_db)):
    # Basic validation - just check if fields exist
    if not data.username or not data.email or not data.password:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "All fields are required",
                "sql_injection_results": []
            }
        )
    
    # Email format validation
    if not is_valid_email(data.email):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Invalid email format",
                "sql_injection_results": []
            }
        )
    
    cursor = db.cursor()
    
    # For educational purposes only - make a vulnerable SELECT query
    username = data.username
    email = data.email
    injection_results = []
    
    try:
        # Intentionally vulnerable query using string concatenation
        raw_query = f"SELECT * FROM users WHERE id = 1 AND username = '{username}'"
        print(f"Executing query: {raw_query}")  # Debug print
        cursor.execute(raw_query)
        result = cursor.fetchall()
        print(f"Query result: {result}")
        
        # Store results for returning to client
        injection_results = []
        for row in result:
            # Convert datetime objects to strings to make them JSON serializable
            serializable_row = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    serializable_row[key] = value.isoformat()
                else:
                    serializable_row[key] = value
            injection_results.append(serializable_row)
            
        print(f"Number of rows returned: {len(injection_results)}")
        for row in result:
            print(row)
    except Exception as e:
        print(f"SQL Error in injection check: {str(e)}")
        injection_results = [{"error": str(e)}]
    
    # Now perform a simple user check
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (data.username, data.email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Still include the injection results even if user exists
            return JSONResponse(
                status_code=409,  # Conflict status code for already existing resource
                content={
                    "status": "error",
                    "message": f"A user with this {'username' if existing_user['username'] == data.username else 'email'} already exists",
                    "sql_injection_results": injection_results
                }
            )
    except Exception as e:
        print(f"SQL Error in user check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Database error checking user existence: {str(e)}",
                "sql_injection_results": injection_results
            }
        )
    
    # Create new user with hashed password
    user_id = None
    try:
        hashed_password = hash_password(data.password, db)
        
        # Use parameterized query for the actual insert
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (data.username, data.email, hashed_password)
        )
        db.commit()
        
        # Get the ID of the new user
        cursor.execute("SELECT id FROM users WHERE username = %s", (data.username,))
        new_user = cursor.fetchone()
        if new_user:
            user_id = new_user['id']
            add_password_to_history(user_id, hashed_password, db)
            
    except Exception as e:
        print(f"SQL Error in insert: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Registration failed: {str(e)}",
                "sql_injection_results": injection_results
            }
        )
    
    # Return registration success along with injection results
    return {
        "status": "success",
        "message": "Registration successful",
        "user_id": user_id,
        "sql_injection_results": injection_results
    }

@app.post("/forgot-password", response_model=MessageResponse)
def forgot_password(data: ForgotPasswordRequest, db = Depends(get_db)):
    """Initiate password reset process by sending a reset token via email"""
    # Basic validation - just check if email exists
    if not data.email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    cursor = db.cursor()
    # Find user by email - Vulnerable to SQL Injection (intentionally)
    try:
        # Direct string concatenation without escaping
        email = data.email
        
        # This query is intentionally vulnerable to SQL injection
        raw_query = "SELECT * FROM users WHERE email = '" + email + "'"
        print(f"Executing query: {raw_query}")  # Debug print
        cursor.execute(raw_query)
        user = cursor.fetchone()
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        raise
    
    # Don't reveal if email exists or not for security
    # Still generate and store a token even if user doesn't exist to prevent timing attacks
    reset_token = generate_reset_token()
    
    if user:
        # Expire any existing unused tokens for this user - Make it vulnerable
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "UPDATE password_reset_tokens SET is_used = 1 WHERE user_id = " + str(user['id']) + " AND is_used = 0 AND expires_at > '" + now + "'"
            print(f"Executing query: {query}")  # Debug print
            cursor.execute(query)
        except Exception as e:
            print(f"SQL Error: {str(e)}")
            # Continue even if this fails
        
        # Create token with 20-minute expiration - Make it vulnerable
        try:
            token_expiry = (datetime.now() + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S')
            
            query = "INSERT INTO password_reset_tokens (user_id, email, token, expires_at) VALUES (" + str(user['id']) + ", '" + email + "', '" + reset_token + "', '" + token_expiry + "')"
            print(f"Executing query: {query}")  # Debug print
            cursor.execute(query)
            db.commit()
        except Exception as e:
            print(f"SQL Error: {str(e)}")
            raise
        
        # Send email with token
        try:
            send_password_reset_email(data.email, reset_token)
        except Exception as e:
            print(f"Email error: {str(e)}")
            # Continue even if email fails
    
    # Always return the same message for security (don't indicate if email exists)
    return {"message": "If an account with this email exists, a password reset link has been sent."}

@app.post("/reset-password", response_model=MessageResponse)
def reset_password(data: ResetPasswordRequest, db = Depends(get_db)):
    """Reset password using the token sent via email"""
    # Basic validation
    if not data.email or not data.token or not data.new_password:
        raise HTTPException(status_code=400, detail="All fields are required")
    
    cursor = db.cursor()
    # Find the token - Vulnerable to SQL Injection (intentionally)
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Remove any backslash escapes
        email = remove_backslash_escapes(data.email)
        token = remove_backslash_escapes(data.token)
        
        # This query is intentionally vulnerable to SQL injection
        raw_query = f"""
            SELECT * FROM password_reset_tokens 
            WHERE email = '{email}' 
            AND token = '{token}' 
            AND is_used = 0 
            AND expires_at > '{now}'
        """
        print(f"Executing query: {raw_query}")  # Debug print
        cursor.execute(raw_query)
        token_record = cursor.fetchone()
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        raise
    
    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Find the user associated with this token
    try:
        query = f"SELECT * FROM users WHERE id = {token_record['user_id']}"
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        user = cursor.fetchone()
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        raise
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Validate the new password - only check if it's in history
    if not check_password_history(user['id'], data.new_password, db):
        raise HTTPException(status_code=400, detail=f"Cannot reuse one of your last {config.PASSWORD_HISTORY_LENGTH} passwords")
    
    # Hash the new password
    hashed_password = hash_password(data.new_password, db)
    
    # Update user's password - Escaped to prevent syntax errors
    try:
        escaped_password = escape_string(hashed_password)
        query = f"UPDATE users SET password = '{escaped_password}' WHERE id = {user['id']}"
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        raise
    
    # Mark token as used
    try:
        query = f"UPDATE password_reset_tokens SET is_used = 1 WHERE id = {token_record['id']}"
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        # Continue even if this fails
    
    # Add the new password to history
    try:
        add_password_to_history(user['id'], hashed_password, db)
    except Exception as e:
        print(f"Error adding password to history: {str(e)}")
        # Continue even if this fails
    
    db.commit()
    
    return {"message": "Password has been reset successfully"}

@app.post("/change-password")
def change_password(data: ChangePasswordData, current_user = Depends(get_current_user), db = Depends(get_db)):
    # Basic validation
    if not data.oldPassword or not data.newPassword:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Both current and new passwords are required"
            }
        )
    
    # Verify the old password matches the user's current password
    if not verify_password(data.oldPassword, current_user['password'], db):
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "message": "Invalid current password"
            }
        )
    
    # Validate the new password with history check
    if not check_password_history(current_user['id'], data.newPassword, db):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": f"Cannot reuse one of your last {config.PASSWORD_HISTORY_LENGTH} passwords"
            }
        )
    
    # For SQL Injection demonstration, let's create a vulnerable version of the update query
    # We'll demonstrate SQL injection possibility in the new password field
    injection_results = []
    try:
        # Intentionally vulnerable query using string concatenation with the new password
        test_query = f"SELECT * FROM users WHERE id = {current_user['id']} AND password LIKE '{data.newPassword}%'"
        print(f"Executing test query: {test_query}")  # Debug print
        cursor = db.cursor()
        cursor.execute(test_query)
        result = cursor.fetchall()
        
        # Store results for returning to client
        for row in result:
            # Convert datetime objects to strings to make them JSON serializable
            serializable_row = {}
            for key, value in row.items():
                if isinstance(value, datetime):
                    serializable_row[key] = value.isoformat()
                else:
                    serializable_row[key] = value
            injection_results.append(serializable_row)
    except Exception as e:
        print(f"SQL Injection test error: {str(e)}")
        injection_results = [{"error": str(e)}]
    
    # Update password with new hash - Escaped to prevent syntax errors in the actual update
    try:
        new_hashed_password = hash_password(data.newPassword, db)
        escaped_password = escape_string(new_hashed_password)
        cursor = db.cursor()
        query = f"UPDATE users SET password = '{escaped_password}' WHERE id = {current_user['id']}"
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to update password: {str(e)}",
                "sql_injection_results": injection_results
            }
        )
    
    # Add the new password to history
    try:
        add_password_to_history(current_user['id'], new_hashed_password, db)
    except Exception as e:
        print(f"Error adding password to history: {str(e)}")
        # Continue even if this fails
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Password changed successfully",
        "sql_injection_results": injection_results
    }


@app.post("/verify-reset-token", response_model=MessageResponse)
def verify_reset_token(data: VerifyTokenRequest, db = Depends(get_db)):
    """Verify a password reset token before allowing password change"""
    # Basic validation
    if not data.email or not data.token:
        raise HTTPException(status_code=400, detail="Email and verification code are required")
    
    cursor = db.cursor()
    # Find the token - Vulnerable to SQL Injection (intentionally)
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Remove any backslash escapes
        email = remove_backslash_escapes(data.email)
        token = remove_backslash_escapes(data.token)
        
        # This query is intentionally vulnerable to SQL injection
        raw_query = f"""
            SELECT * FROM password_reset_tokens 
            WHERE email = '{email}' 
            AND token = '{token}' 
            AND is_used = 0 
            AND expires_at > '{now}'
        """
        print(f"Executing query: {raw_query}")  # Debug print
        cursor.execute(raw_query)
        token_record = cursor.fetchone()
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        raise
    
    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    
    # Find the user associated with this token
    try:
        query = f"SELECT * FROM users WHERE id = {token_record['user_id']}"
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        user = cursor.fetchone()
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        raise
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Do not mark token as used yet - it will be marked when password is reset
    
    return {"message": "Verification code is valid. Please set a new password."}

@app.post("/customers", response_model=MessageResponse)
def add_customer(data: CustomerData, current_user = Depends(get_current_user), db = Depends(get_db)):
    # Create new customer without sanitization - Vulnerable to SQL Injection and XSS
    # For this educational endpoint, we're keeping both XSS and SQL injection vulnerabilities
    try:
        cursor = db.cursor()
        # Intentionally vulnerable with direct string concatenation
        query = f"""
            INSERT INTO customers (name, internet_package, sector)
            VALUES ('{data.name}', '{data.internet_package}', '{data.sector}')
        """
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        db.commit()
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        raise
    
    return {"message": "Customer added successfully"}

@app.get("/customers", response_model=CustomerListResponse)
def get_customers(current_user = Depends(get_current_user), db = Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        raise
    
    # Convert datetime to string for serialization
    customer_responses = []
    for customer in customers:
        customer_responses.append({
            "id": customer['id'],
            "name": customer['name'],
            "internet_package": customer['internet_package'],
            "sector": customer['sector'],
            "date_added": customer['date_added'].strftime("%Y-%m-%d")
        })
    
    # Return in format matching CustomerListResponse
    return {"customers": customer_responses}

# Endpoint to get current user info
@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    return current_user

# Function to check if tables exist
def check_tables_exist(db):
    cursor = db.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        existing_tables = [list(table.values())[0] for table in tables]
        
        required_tables = [
            "users", "customers", "secrets", "password_history", 
            "login_attempts", "account_status", "password_reset_tokens"
        ]
        
        for table in required_tables:
            if table not in existing_tables:
                print(f"Table {table} does not exist, creating tables...")
                return False
                
        return True
    except Exception as e:
        print(f"Error checking tables: {e}")
        return False

# Initialize salt on application startup
@app.on_event("startup")
def initialize_application():
    db = get_db_connection()
    try:
        # Check if tables exist, if not run init.sql
        if not check_tables_exist(db):
            print("Creating database tables...")
            with open("init.sql", "r") as f:
                sql_commands = f.read()
                cursor = db.cursor()
                for command in sql_commands.split(';'):
                    if command.strip():
                        cursor.execute(command)
                db.commit()
        
        # Initialize salt if it doesn't exist
        get_or_create_salt(db)
        
        # Initialize JWT secret if it doesn't exist
        get_or_create_jwt_secret(db)
        
        # Create admin user if it doesn't exist
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            # Create admin with hashed password
            hashed_password = hash_password("admin", db)
            escaped_password = escape_string(hashed_password)
            cursor.execute(f"""
                INSERT INTO users (username, email, password)
                VALUES ('admin', 'admin@example.com', '{escaped_password}')
            """)
            db.commit()
            print("Created admin user with secure password")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)