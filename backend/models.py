from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from database import Base

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))

# Customer model
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    internet_package = Column(String(50))
    sector = Column(String(50))
    date_added = Column(DateTime, default=datetime.now)

# Secret model for storing application secrets
class Secret(Base):
    __tablename__ = "secrets"
    
    id = Column(String(10), primary_key=True)
    value = Column(String(255), nullable=False)

# Password history model
class PasswordHistory(Base):
    __tablename__ = "password_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# Login attempt tracking model
class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True)
    attempt_time = Column(DateTime, default=datetime.now)
    successful = Column(Boolean, default=False)
    ip_address = Column(String(45), nullable=True)  # Supports IPv6 addresses

# Account status model
class AccountStatus(Base):
    __tablename__ = "account_status"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime, nullable=True)
    failed_attempts = Column(Integer, default=0)

# Password reset token model
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(100), nullable=False)
    token = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)