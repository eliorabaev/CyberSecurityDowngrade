from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import password_config as config
from password_utils import hash_password, verify_password
from models import PasswordHistory, LoginAttempt, AccountStatus

def check_password_history(user_id: int, new_password: str, db: Session) -> bool:
    """
    Check if a new password is in the user's password history
    
    Args:
        user_id (int): The user's ID
        new_password (str): The new password to check
        db (Session): SQLAlchemy database session
        
    Returns:
        bool: True if password is not in history, False if it is
    """
    # Get the user's password history
    history = db.query(PasswordHistory)\
        .filter(PasswordHistory.user_id == user_id)\
        .order_by(PasswordHistory.created_at.desc())\
        .limit(config.PASSWORD_HISTORY_LENGTH)\
        .all()
    
    # Check if the new password matches any in the history
    for entry in history:
        if verify_password(new_password, entry.password_hash, db):
            return False
    
    return True

def add_password_to_history(user_id: int, password_hash: str, db: Session):
    """
    Add a password to the user's password history
    
    Args:
        user_id (int): The user's ID
        password_hash (str): The hashed password to add
        db (Session): SQLAlchemy database session
    """
    # Create a new password history entry
    new_entry = PasswordHistory(
        user_id=user_id,
        password_hash=password_hash
    )
    
    db.add(new_entry)
    db.commit()

def is_password_in_disallowed_list(password: str) -> bool:
    """
    Check if a password is in the disallowed passwords list
    
    Args:
        password (str): The password to check
        
    Returns:
        bool: True if password is disallowed, False otherwise
    """
    return password.lower() in (p.lower() for p in config.DISALLOWED_PASSWORDS)

def record_login_attempt(username: str, successful: bool, ip_address: str, db: Session):
    """
    Record a login attempt for a user
    
    Args:
        username (str): The username attempting to login
        successful (bool): Whether the attempt was successful
        ip_address (str): The IP address of the request
        db (Session): SQLAlchemy database session
    """
    # Create a new login attempt record
    new_attempt = LoginAttempt(
        username=username,
        successful=successful,
        ip_address=ip_address
    )
    
    db.add(new_attempt)
    db.commit()

def get_recent_failed_attempts(username: str, db: Session) -> int:
    """
    Get the number of recent failed login attempts for a user
    
    Args:
        username (str): The username to check
        db (Session): SQLAlchemy database session
        
    Returns:
        int: Number of recent failed attempts
    """
    # Only count attempts in the last 24 hours
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    # Query for failed attempts
    attempts = db.query(LoginAttempt)\
        .filter(
            LoginAttempt.username == username,
            LoginAttempt.successful == False,
            LoginAttempt.attempt_time >= cutoff_time
        )\
        .count()
    
    return attempts

def is_account_locked(user_id: int, db: Session) -> tuple:
    """
    Check if a user account is locked
    
    Args:
        user_id (int): The user's ID
        db (Session): SQLAlchemy database session
        
    Returns:
        tuple: (is_locked, lock_message)
    """
    # Get the account status
    status = db.query(AccountStatus)\
        .filter(AccountStatus.user_id == user_id)\
        .first()
    
    if not status:
        return False, ""
    
    # Check if account is locked
    if status.is_locked:
        # Check if lock has expired
        if status.locked_until and status.locked_until <= datetime.now():
            # Reset lock status
            status.is_locked = False
            status.locked_until = None
            status.failed_attempts = 0
            db.commit()
            return False, ""
        else:
            # Account is still locked
            remaining_time = status.locked_until - datetime.now()
            minutes = int(remaining_time.total_seconds() / 60)
            return True, f"Account is locked. Try again in {minutes} minutes."
    
    return False, ""

def lock_account(user_id: int, db: Session):
    """
    Lock a user account after too many failed attempts
    
    Args:
        user_id (int): The user's ID
        db (Session): SQLAlchemy database session
    """
    # Get or create account status
    status = db.query(AccountStatus)\
        .filter(AccountStatus.user_id == user_id)\
        .first()
    
    if not status:
        status = AccountStatus(user_id=user_id)
        db.add(status)
    
    # Lock account for 30 minutes
    status.is_locked = True
    status.locked_until = datetime.now() + timedelta(minutes=30)
    db.commit()

def increment_failed_attempts(user_id: int, db: Session) -> int:
    """
    Increment the failed login attempts counter
    
    Args:
        user_id (int): The user's ID
        db (Session): SQLAlchemy database session
        
    Returns:
        int: New number of failed attempts
    """
    # Get or create account status
    status = db.query(AccountStatus)\
        .filter(AccountStatus.user_id == user_id)\
        .first()
    
    if not status:
        status = AccountStatus(user_id=user_id, failed_attempts=1)
        db.add(status)
        db.commit()
        return 1
    
    # Increment failed attempts
    status.failed_attempts += 1
    db.commit()
    
    # If max attempts reached, lock account
    if status.failed_attempts >= config.MAX_LOGIN_ATTEMPTS:
        lock_account(user_id, db)
        
    return status.failed_attempts

def reset_failed_attempts(user_id: int, db: Session):
    """
    Reset the failed login attempts counter after successful login
    
    Args:
        user_id (int): The user's ID
        db (Session): SQLAlchemy database session
    """
    # Get account status
    status = db.query(AccountStatus)\
        .filter(AccountStatus.user_id == user_id)\
        .first()
    
    if status:
        status.failed_attempts = 0
        db.commit()