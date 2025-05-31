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
from validation_utils import validate_password
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
        return {"status": "error", "message": "Username and password are required"}

    client_ip = request.client.host if request.client else "unknown"
    
    # Check if IP is locked
    is_locked_ip, lock_message_ip = is_ip_locked(client_ip, db)
    if is_locked_ip:
        record_login_attempt(data.username, False, client_ip, db)
        return {"status": "error", "message": lock_message_ip}
    
    try:
        cursor = db.cursor()
        # Vulnerable SQL query with direct string concatenation
        query = "SELECT * FROM users WHERE username = '" + data.username + "'"
        print(f"Executing query: {query}")
        cursor.execute(query)
        result = cursor.fetchall()
        
        # No users found
        if len(result) == 0:
            record_login_attempt(data.username, False, client_ip, db)
            return {"status": "error", "message": "Invalid username or password"}
        
        # Exactly one user found
        elif len(result) == 1:
            user = result[0]
            # Check if account is locked
            is_locked, lock_message = is_account_locked(user['id'], db)
            if is_locked:
                record_login_attempt(data.username, False, client_ip, db)
                return {"status": "error", "message": lock_message}
            
            # Verify password
            if verify_password(data.password, user['password'], db):
                record_login_attempt(data.username, True, client_ip, db)
                reset_failed_attempts(user['id'], db)
                access_token = create_access_token(
                    data={"sub": user['username']},
                    expires_delta=timedelta(minutes=60),
                    db_connection=db
                )
                return {
                    "status": "success",
                    "message": "Login successful",
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            else:
                record_login_attempt(data.username, False, client_ip, db)
                increment_failed_attempts(user['id'], db)
                return {"status": "error", "message": "Invalid username or password"}
        
        # Multiple users found (SQL injection)
        else:
            record_login_attempt(data.username, False, client_ip, db)
            raw_results = []
            for row in result:
                raw_row = "{"
                for key, value in row.items():
                    if isinstance(value, str):
                        raw_row += f"'{key}': '{value}', "
                    elif value is None:
                        raw_row += f"'{key}': NULL, "
                    else:
                        raw_row += f"'{key}': {value}, "
                raw_row = raw_row.rstrip(", ") + "}"
                raw_results.append(raw_row)
            raw_output = "Results:\n" + "\n".join(raw_results)
            return {
                "status": "error",
                "message": f"Multiple users found: {len(result)}\n{raw_output[:500]}"
            }
    
    except Exception as e:
        record_login_attempt(data.username, False, client_ip, db)
        return {"status": "error", "message": f"SQL Error: {str(e)}\nQuery: {query}"}

@app.post("/register")
def register(data: RegisterData, db = Depends(get_db)):
    # Basic validation
    if not data.username or not data.email or not data.password:
        return {"status": "error", "message": "All fields are required"}
    
    # Email format validation
    if not is_valid_email(data.email):
        return {"status": "error", "message": "Invalid email format"}
    
    is_valid, password_msg = validate_password(data.password)
    if not is_valid:
        return {"status": "error", "message": password_msg}
    
    cursor = db.cursor()
    
    try:
        # VULNERABLE: Direct string concatenation in query
        # This query is constructed in a way that UNION attacks can work
        query = "SELECT * FROM users WHERE username = '" + data.username + "'"
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        # Check if user exists by username
        if result and len(result) > 0:
            # The key vulnerability: this will return data from UNION queries
            row_data = str(result[0])
            return {"status": "error", "message": f"User already exists: {row_data[:100]}"}
        
        # Check if email exists (using parameterized query for this check)
        cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
        if cursor.fetchone():
            return {"status": "error", "message": "Email already in use"}
        
        # Insert new user with properly hashed password
        hashed_password = hash_password(data.password, db)
        
        # Another vulnerability in the insert query
        insert_query = f"INSERT INTO users (username, email, password) VALUES ('{data.username}', '{data.email}', '{hashed_password}')"
        cursor.execute(insert_query)
        db.commit()
        
        # Get the ID of the new user
        cursor.execute("SELECT id FROM users WHERE username = %s", (data.username,))
        new_user = cursor.fetchone()
        user_id = new_user['id'] if new_user else None
        
        if user_id:
            add_password_to_history(user_id, hashed_password, db)
        
        return {"status": "success", "message": "Registration successful", "user_id": user_id}
        
    except Exception as e:
        # Error message includes the exception which may contain SQL info
        return {"status": "error", "message": f"Registration error: {str(e)}"}
    
@app.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db = Depends(get_db)):
    """Initiate password reset process by sending a reset token via email"""
    # Validate email input
    from validation_utils import validate_email
    is_valid, error_message = validate_email(data.email)
    if not is_valid:
        return {"status": "error", "message": error_message}
    
    cursor = db.cursor()
    
    try:
        # SECURE: Use parameterized query to prevent SQL injection
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (data.email,))
        user = cursor.fetchone()
        
    except Exception as e:
        # SECURE: Don't leak database error details
        print(f"Database error in forgot_password: {str(e)}")  # Log for debugging
        return {"status": "error", "message": "An error occurred processing your request"}
    
    # Generate token
    reset_token = generate_reset_token()
    
    if user:
        try:
            # SECURE: Use parameterized query to expire existing tokens
            expire_query = "UPDATE password_reset_tokens SET is_used = 1 WHERE user_id = %s AND is_used = 0"
            cursor.execute(expire_query, (user['id'],))
            
            # Create new token with 20-minute expiration
            token_expiry = datetime.now() + timedelta(minutes=20)
            
            # SECURE: Use parameterized query for insert
            insert_query = """
                INSERT INTO password_reset_tokens (user_id, email, token, expires_at) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (user['id'], data.email, reset_token, token_expiry))
            db.commit()
            
            # Send email with token
            try:
                send_password_reset_email(data.email, reset_token)
            except Exception as e:
                print(f"Email error: {str(e)}")
                # Still commit the token to database even if email fails
                
        except Exception as e:
            # SECURE: Don't leak database info in the error
            print(f"Error creating reset token: {str(e)}")  # Log for debugging
            return {"status": "error", "message": "An error occurred processing your request"}
    
    # Return generic message for security (don't indicate if email exists)
    return {"status": "success", "message": "If an account with this email exists, a password reset link has been sent."}

@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db = Depends(get_db)):
    """Reset password using the token sent via email"""
    # Validate all required fields
    if not data.email or not data.token or not data.new_password:
        return {"status": "error", "message": "All fields are required"}
    
    # Validate email format
    from validation_utils import validate_email
    is_valid_email, email_error = validate_email(data.email)
    if not is_valid_email:
        return {"status": "error", "message": email_error}
    
    cursor = db.cursor()
    
    try:
        now = datetime.now()
        
        # SECURE: Use parameterized query to find token
        query = """
            SELECT * FROM password_reset_tokens 
            WHERE email = %s 
            AND token = %s 
            AND is_used = 0 
            AND expires_at > %s
        """
        cursor.execute(query, (data.email, data.token, now))
        token_record = cursor.fetchone()
        
    except Exception as e:
        # SECURE: Don't leak database error details
        print(f"Token validation error: {str(e)}")  # Log for debugging
        return {"status": "error", "message": "An error occurred processing your request"}
    
    if not token_record:
        return {"status": "error", "message": "Invalid or expired reset token"}
    
    # Find the user associated with this token
    try:
        # SECURE: Use parameterized query for user lookup
        user_query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(user_query, (token_record['user_id'],))
        user = cursor.fetchone()
    except Exception as e:
        # SECURE: Don't expose error details
        print(f"User lookup error: {str(e)}")  # Log for debugging
        return {"status": "error", "message": "An error occurred processing your request"}
    
    if not user:
        return {"status": "error", "message": "User not found"}

    # Validate the new password
    is_valid, password_msg = validate_password(data.new_password)
    if not is_valid:
        return {"status": "error", "message": password_msg}
    
    # Validate the new password against history
    try:
        is_valid_password = check_password_history(user['id'], data.new_password, db)
        if not is_valid_password:
            return {"status": "error", "message": f"Cannot reuse one of your last {config.PASSWORD_HISTORY_LENGTH} passwords"}
    except Exception as e:
        # SECURE: Don't expose internal validation details
        print(f"Password history validation error: {str(e)}")  # Log for debugging
        return {"status": "error", "message": "An error occurred validating your password"}
    
    # Hash the new password
    try:
        hashed_password = hash_password(data.new_password, db)
    except Exception as e:
        print(f"Password hashing error: {str(e)}")  # Log for debugging
        return {"status": "error", "message": "An error occurred processing your request"}
    
    # Update user's password
    try:
        # SECURE: Use parameterized query for password update
        update_query = "UPDATE users SET password = %s WHERE id = %s"
        cursor.execute(update_query, (hashed_password, user['id']))
    except Exception as e:
        # SECURE: Don't leak SQL error details
        print(f"Password update error: {str(e)}")  # Log for debugging
        return {"status": "error", "message": "An error occurred updating your password"}
    
    # Mark token as used
    try:
        # SECURE: Use parameterized query for token update
        token_query = "UPDATE password_reset_tokens SET is_used = 1 WHERE id = %s"
        cursor.execute(token_query, (token_record['id'],))
    except Exception as e:
        print(f"Error marking token as used: {str(e)}")
        # Continue even if this fails - no return here
    
    # Add the new password to history
    try:
        add_password_to_history(user['id'], hashed_password, db)
    except Exception as e:
        print(f"Error adding password to history: {str(e)}")
        # Continue even if this fails - no return here
    
    db.commit()
    
    return {"status": "success", "message": "Password has been reset successfully"}

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
    
    if not verify_password(data.oldPassword, current_user['password'], db):
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "message": "Invalid current password"
            }
        )

    is_valid, password_msg = validate_password(data.newPassword, current_user['id'], db)
    if not is_valid:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": password_msg,
                "sql_injection_results": injection_results if 'injection_results' in locals() else []
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
    try:
        cursor = db.cursor()
        query = """
            INSERT INTO customers (name, internet_package, sector)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (data.name, data.internet_package, data.sector))
        db.commit()
    except Exception as e:
        print(f"SQL Error: {str(e)}")
        raise
    
    return {"message": f"Customer '{data.name}' added successfully"}


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

        # Create test user if it doesn't exist
        cursor.execute("SELECT * FROM users WHERE username = 'test1'")
        test_exists = cursor.fetchone()

        if not test_exists:
            # Create test user with hashed password
            hashed_password = hash_password("test", db)
            escaped_password = escape_string(hashed_password)
            cursor.execute(f"""
                INSERT INTO users (username, email, password)
                VALUES ('test1', 'test@example.com', '{escaped_password}')
            """)
            db.commit()
            print("Created test1 user with secure password")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)