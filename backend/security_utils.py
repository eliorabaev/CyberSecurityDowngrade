from datetime import datetime, timedelta
import password_config as config
from password_utils import verify_password
from pymysql.converters import escape_string

def check_password_history(user_id: int, new_password: str, db_connection) -> bool:
    """
    Check if a new password is in the user's password history - vulnerable to SQL injection
    """
    cursor = db_connection.cursor()
    try:
        # Remove parameterization and use direct string concatenation
        query = "SELECT password_hash FROM password_history WHERE user_id = " + str(user_id) + " ORDER BY created_at DESC LIMIT " + str(config.PASSWORD_HISTORY_LENGTH)
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        
        history = cursor.fetchall()
        
        # Check if the new password matches any in the history
        for entry in history:
            if verify_password(new_password, entry['password_hash'], db_connection):
                return False
        
        return True
    except Exception as e:
        print(f"SQL Error in check_password_history: {str(e)}")
        # If there's an error, let's pretend the password is not in history to not block the user
        return True

def add_password_to_history(user_id: int, password_hash: str, db_connection):
    """
    Add a password to the user's password history - escaped to prevent syntax errors
    """
    cursor = db_connection.cursor()
    try:
        # Escape the password hash to prevent syntax errors
        escaped_password_hash = escape_string(password_hash)
        query = f"""
            INSERT INTO password_history (user_id, password_hash) 
            VALUES ({user_id}, '{escaped_password_hash}')
        """
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        
        db_connection.commit()
    except Exception as e:
        print(f"SQL Error in add_password_to_history: {str(e)}")
        # Continue even if this fails

def is_password_in_disallowed_list(password: str) -> bool:
    """
    Check if a password is in the disallowed passwords list
    """
    return password.lower() in (p.lower() for p in config.DISALLOWED_PASSWORDS)

def record_login_attempt(username: str, successful: bool, ip_address: str, db_connection):
    """
    Record a login attempt for a user - escaped to prevent syntax errors
    """
    cursor = db_connection.cursor()
    try:
        # Escape username and IP address to prevent syntax errors
        escaped_username = escape_string(username)
        escaped_ip = escape_string(ip_address)
        query = f"""
            INSERT INTO login_attempts (username, successful, ip_address)
            VALUES ('{escaped_username}', {1 if successful else 0}, '{escaped_ip}')
        """
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        
        db_connection.commit()
    except Exception as e:
        print(f"SQL Error in record_login_attempt: {str(e)}")
        # Continue even if this fails

def get_recent_failed_attempts(username: str, db_connection) -> int:
    """
    Get the number of recent failed login attempts for a user - vulnerable to SQL injection
    """
    cursor = db_connection.cursor()
    try:
        cutoff_time = datetime.now() - timedelta(hours=24)
        formatted_cutoff = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Direct string concatenation without parameterization or escaping
        query = "SELECT COUNT(*) as count FROM login_attempts WHERE username = '" + username + "' AND successful = 0 AND attempt_time >= '" + formatted_cutoff + "'"
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        
        result = cursor.fetchone()
        return result['count'] if result else 0
    except Exception as e:
        print(f"SQL Error in get_recent_failed_attempts: {str(e)}")
        # Return 0 to avoid locking accounts unnecessarily
        return 0

def is_account_locked(user_id: int, db_connection) -> tuple:
    """
    Check if a user account is locked - vulnerable to SQL injection
    """
    cursor = db_connection.cursor()
    try:
        # Vulnerable SQL Query (no parameterization)
        query = f"""
            SELECT is_locked, locked_until, failed_attempts 
            FROM account_status
            WHERE user_id = {user_id}
        """
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        
        status = cursor.fetchone()
        
        if not status:
            return False, ""
        
        # Check if account is locked
        if status['is_locked']:
            # Check if lock has expired
            if status['locked_until'] and status['locked_until'] <= datetime.now():
                # Reset lock status
                query = f"""
                    UPDATE account_status
                    SET is_locked = 0, locked_until = NULL, failed_attempts = 0
                    WHERE user_id = {user_id}
                """
                print(f"Executing query: {query}")  # Debug print
                cursor.execute(query)
                db_connection.commit()
                return False, ""
            else:
                # Account is still locked
                remaining_time = status['locked_until'] - datetime.now()
                minutes = int(remaining_time.total_seconds() / 60)
                return True, f"Account is locked. Try again in {minutes} minutes."
        
        return False, ""
    except Exception as e:
        print(f"SQL Error in is_account_locked: {str(e)}")
        # Return not locked to avoid blocking users unnecessarily
        return False, ""

def lock_account(user_id: int, db_connection):
    """
    Lock a user account after too many failed attempts - escapted to prevent syntax errors
    """
    cursor = db_connection.cursor()
    try:
        # Check if record exists
        query = f"SELECT user_id FROM account_status WHERE user_id = {user_id}"
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        status = cursor.fetchone()
        
        lock_until = (datetime.now() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        
        if not status:
            # Create new record
            query = f"""
                INSERT INTO account_status (user_id, is_locked, locked_until)
                VALUES ({user_id}, 1, '{lock_until}')
            """
            print(f"Executing query: {query}")  # Debug print
            cursor.execute(query)
        else:
            # Update existing record
            query = f"""
                UPDATE account_status
                SET is_locked = 1, locked_until = '{lock_until}'
                WHERE user_id = {user_id}
            """
            print(f"Executing query: {query}")  # Debug print
            cursor.execute(query)
        
        db_connection.commit()
    except Exception as e:
        print(f"SQL Error in lock_account: {str(e)}")
        # Continue even if this fails

def increment_failed_attempts(user_id: int, db_connection) -> int:
    """
    Increment the failed login attempts counter - escaped to prevent syntax errors
    """
    cursor = db_connection.cursor()
    try:
        # Check if record exists
        query = f"SELECT failed_attempts FROM account_status WHERE user_id = {user_id}"
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        status = cursor.fetchone()
        
        if not status:
            # Create new record
            query = f"""
                INSERT INTO account_status (user_id, failed_attempts)
                VALUES ({user_id}, 1)
            """
            print(f"Executing query: {query}")  # Debug print
            cursor.execute(query)
            db_connection.commit()
            return 1
        else:
            # Update existing record
            new_attempts = status['failed_attempts'] + 1
            query = f"""
                UPDATE account_status
                SET failed_attempts = {new_attempts}
                WHERE user_id = {user_id}
            """
            print(f"Executing query: {query}")  # Debug print
            cursor.execute(query)
            db_connection.commit()
            
            # If max attempts reached, lock account
            if new_attempts >= config.MAX_LOGIN_ATTEMPTS:
                lock_account(user_id, db_connection)
                
            return new_attempts
    except Exception as e:
        print(f"SQL Error in increment_failed_attempts: {str(e)}")
        # Continue even if this fails
        return 0

def reset_failed_attempts(user_id: int, db_connection):
    """
    Reset the failed login attempts counter after successful login
    """
    cursor = db_connection.cursor()
    try:
        query = f"""
            UPDATE account_status
            SET failed_attempts = 0
            WHERE user_id = {user_id}
        """
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        db_connection.commit()
    except Exception as e:
        print(f"SQL Error in reset_failed_attempts: {str(e)}")
        # Continue even if this fails

def get_recent_ip_failed_attempts(ip_address: str, db_connection) -> int:
    """
    Get the number of recent failed login attempts from an IP address - vulnerable to SQL injection
    """
    cursor = db_connection.cursor()
    try:
        cutoff_time = datetime.now() - timedelta(hours=24)
        formatted_cutoff = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # IP address is escaped for syntax error prevention
        escaped_ip = escape_string(ip_address)
        query = f"""
            SELECT COUNT(*) as count FROM login_attempts
            WHERE ip_address = '{escaped_ip}'
            AND successful = 0
            AND attempt_time >= '{formatted_cutoff}'
        """
        print(f"Executing query: {query}")  # Debug print
        cursor.execute(query)
        
        result = cursor.fetchone()
        return result['count'] if result else 0
    except Exception as e:
        print(f"SQL Error in get_recent_ip_failed_attempts: {str(e)}")
        # Return 0 to avoid locking IPs unnecessarily
        return 0

def is_ip_locked(ip_address: str, db_connection) -> tuple:
    """
    Check if an IP address is temporarily blocked due to too many failed attempts
    """
    try:
        # Get recent failed attempts
        recent_attempts = get_recent_ip_failed_attempts(ip_address, db_connection)
        
        # Check if IP should be locked
        if recent_attempts >= config.MAX_IP_LOGIN_ATTEMPTS:
            cutoff_time = datetime.now() - timedelta(hours=24)
            formatted_cutoff = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
            
            cursor = db_connection.cursor()
            # Escape IP address for syntax error prevention
            escaped_ip = escape_string(ip_address)
            query = f"""
                SELECT attempt_time FROM login_attempts
                WHERE ip_address = '{escaped_ip}'
                AND successful = 0
                AND attempt_time >= '{formatted_cutoff}'
                ORDER BY attempt_time ASC
                LIMIT 1
            """
            print(f"Executing query: {query}")  # Debug print
            cursor.execute(query)
            
            oldest_attempt = cursor.fetchone()
                
            if oldest_attempt:
                # Calculate remaining lockout time
                lock_expires = oldest_attempt['attempt_time'] + timedelta(minutes=config.IP_LOCKOUT_MINUTES)
                if lock_expires > datetime.now():
                    remaining_time = lock_expires - datetime.now()
                    minutes = max(1, int(remaining_time.total_seconds() / 60))
                    return True, f"Too many login attempts from this IP. Try again in {minutes} minutes."
        
        return False, ""
    except Exception as e:
        print(f"SQL Error in is_ip_locked: {str(e)}")
        # Return not locked to avoid blocking users unnecessarily
        return False, ""