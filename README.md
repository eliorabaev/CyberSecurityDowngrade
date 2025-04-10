# Internet Service Provider Management System

A secure web application for managing internet service customers with a FastAPI backend and React frontend, featuring robust user authentication and session management.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

## Overview

This comprehensive system provides a secure and user-friendly interface for managing Internet Service Provider (ISP) customers. Built with security best practices at every level, it implements a layered defense approach to protect sensitive customer data while maintaining a smooth user experience.

## Key Features

- 🔐 **Enterprise-Grade Authentication**
  - JWT-based user sessions with token expiration
  - Password hashing with PBKDF2-HMAC-SHA256 (1,200,000 iterations)
  - Database-stored cryptographic salt for consistent security
  - Protection against brute force and replay attacks

- 👤 **Comprehensive User Management**
  - Secure registration with email validation
  - Login with sanitized error messages to prevent username enumeration
  - Self-service password management with secure validation
  - Role-based access for future extensibility

- 👥 **Customer Management**
  - Add new customers with validated information
  - View customers with secure data presentation
  - Input validation to prevent malicious data entry
  - Protection against XSS through automatic HTML escaping

- 🔒 **Full-Stack Security Implementation**
  - Server-side validation using Pydantic models
  - Client-side validation for user experience
  - Content Security Policy implementation
  - Automatic input sanitization and output escaping

- 🌐 **Production-Ready Architecture**
  - Responsive React-based interface
  - Dockerized deployment for consistency
  - Environment-based configuration
  - Separation of concerns between front and backend

## Architecture Diagram

```
┌─────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│                 │      │                  │      │                  │
│  React Frontend │◄────►│  FastAPI Backend │◄────►│  MySQL Database  │
│                 │      │                  │      │                  │
└─────────────────┘      └──────────────────┘      └──────────────────┘
       ▲                         ▲
       │                         │
       │                         │
       │     ┌──────────────┐    │
       └────►│    JWT Auth  │◄───┘
             │              │
             └──────────────┘
```

## Detailed Project Structure

```
/project_root/
├── README.md                # Project documentation
├── .gitignore               # Git ignore file
│
├── backend/
│   ├── .env                 # Backend environment variables (not in git)
│   ├── .env.example         # Example backend environment variables
│   ├── docker-compose.yml   # Docker Compose configuration
│   ├── Dockerfile           # Backend Docker configuration
│   ├── init.sql             # Database initialization script
│   ├── main.py              # FastAPI application entry point
│   │   ├── API routes       # HTTP endpoints
│   │   ├── Authentication   # Token validation
│   │   ├── Database models  # SQLAlchemy ORM definitions
│   │   ├── Pydantic models  # Request/response validation
│   │   └── Middleware       # CORS, error handling
│   ├── auth_utils.py        # JWT token generation and verification
│   ├── password_utils.py    # Secure password hashing and verification
│   │   ├── Salt management  # Database-stored salt generation/retrieval
│   │   ├── PBKDF2 hashing   # High-iteration password hashing
│   │   └── Verification     # Secure comparison functions
│   ├── validation_utils.py  # Input data validation
│   │   ├── Username rules   # Length, character restrictions
│   │   ├── Password rules   # Complexity requirements
│   │   └── Business rules   # Customer data validation
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── .env                 # Frontend environment variables (not in git)
    ├── .env.example         # Example frontend environment variables
    ├── package.json         # Frontend dependencies
    ├── package-lock.json    # Dependency lock file (not in git)
    ├── public/              # Static files
    │   ├── favicon.ico      # Application icon
    │   ├── index.html       # HTML entry point
    │   └── robots.txt       # Crawler instructions
    └── src/                 # React source code
        ├── App.js           # Main application component
        ├── App.css          # Main application styles
        ├── AuthContext.js   # Authentication context provider
        ├── config.js        # Configuration settings
        ├── index.js         # React entry point
        ├── index.css        # Global styles
        ├── utils/           # Utility functions
        │   └── validation.js # Client-side validation functions
        ├── ChangePassword.js # Password management component
        ├── CustomerManagement.js # Customer CRUD operations
        ├── ForgotPassword.js # Password recovery component
        └── Register.js      # User registration component
```

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework with automatic OpenAPI documentation
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **Pydantic**: Data validation and settings management
- **PyJWT**: JSON Web Token implementation
- **Cryptography**: Secure cryptographic recipes and primitives
- **Python-dotenv**: Environment variable management
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **React**: JavaScript library for building user interfaces
- **React Context API**: State management across components
- **HTML5/CSS3**: Modern layout and styling
- **Fetch API**: Network requests to backend services
- **localStorage**: Client-side token storage

### Database
- **MySQL**: Reliable relational database system
- **SQLAlchemy ORM**: Object-relational mapping for database access

### Infrastructure
- **Docker**: Containerization for consistent environments
- **Docker Compose**: Multi-container orchestration

## Detailed Security Implementation

### Authentication Security

#### Password Hashing Process
The system employs a secure password hashing implementation:

1. **Salt Generation & Storage**:
   - A 32-byte (256-bit) cryptographically secure random salt is generated at first application startup
   - The salt is stored in a dedicated `salt` table in the database with ID "main"
   - This approach ensures consistent salt usage across application instances

2. **Password Hashing Algorithm**:
   - PBKDF2-HMAC-SHA256 with 1,200,000 iterations (significantly above NIST recommendations)
   - 32-byte (256-bit) derived key length
   - Base64 encoding for database storage

3. **Verification Process**:
   - Constant-time comparison to prevent timing attacks
   - Same salt and parameters ensure consistent verification

#### JWT Authentication
The system implements secure JWT (JSON Web Token) authentication:

1. **Token Generation**:
   - RS256 (RSA Signature with SHA-256) algorithm
   - 1-hour expiration time to limit attack window
   - Username stored as subject claim
   - Secure secret key generated with `openssl rand -hex 32`

2. **Token Validation**:
   - Full signature validation
   - Expiration time checking
   - Token extraction from Authorization header

3. **Frontend Token Management**:
   - Secure storage in localStorage
   - Automatic inclusion in API request headers
   - Session termination on logout

### Data Security

#### Input Validation
The system implements multiple layers of validation:

1. **Frontend Validation**:
   - Real-time feedback for users
   - Regular expression pattern matching
   - Length and character restrictions

2. **API Validation**:
   - Pydantic models for request body validation
   - Type checking and constraint enforcement
   - Detailed error messaging for debugging

3. **Database Validation**:
   - SQLAlchemy column constraints
   - Unique constraints for username/email
   - Foreign key constraints for data integrity

#### Output Security
The system protects against XSS and injection attacks:

1. **HTML Escaping**:
   - Automatic escaping of HTML special characters
   - Custom `sanitize_string()` function
   - Pydantic validators for response models

2. **Safe Rendering**:
   - React's built-in XSS protection
   - Custom helper to handle sanitized content
   - Type-safe rendering in components

## Prerequisites

- Docker and Docker Compose v1.29+
- Git
- Node.js v14+ and npm v6+ (for frontend development)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Comprehensive Setup Guide

### 1. Clone the repository

```bash
git clone https://github.com/eliorabaev/CyberSecurity.git
cd CyberSecurity
```

### 2. Backend Configuration

Create and configure the backend environment variables:

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file with secure credentials:

```
# Database Configuration
DB_USER=your_username         # Choose your own username
DB_PASSWORD=your_password     # Choose your own secure password (min. 12 chars recommended)
DB_HOST=localhost             # Keep as localhost for local development
DB_NAME=internet_service_provider

# Docker specific variables
DB_ROOT_PASSWORD=your_root_password  # Change this for production (min. 16 chars recommended)
DB_PORT=3307                    # Change if port 3307 is already in use
API_PORT=8000                   # Change if port 8000 is already in use

# Frontend URL for CORS - update for production
FRONTEND_URL=http://localhost:3000

# Always use MySQL - future support for other databases planned
USE_MYSQL=true

# JWT Authentication
# Generate a secure secret key with: openssl rand -hex 32
JWT_SECRET_KEY=your_generated_jwt_secret_key
```

> **Security Note**: For production environments, use a password manager or secure secret generator to create unique, high-entropy passwords and keys.

### 3. Frontend Configuration

Configure the React frontend:

```bash
cd ../frontend
cp .env.example .env
```

The frontend `.env` file should contain:

```
# API connection settings - update for production
REACT_APP_API_HOST=localhost
REACT_APP_API_PORT=8000
```

### 4. Start the Backend Services

Launch the backend with Docker Compose:

```bash
cd ../backend
docker-compose up -d
```

This command:
- Builds the Python FastAPI backend container
- Initializes a MySQL database container
- Creates required volumes and networking
- Sets up a secure communication channel between containers

Verify the services are running:

```bash
docker-compose ps
```

You should see both services with status "Up".

### 5. Start the Frontend Development Server

For development or standalone frontend:

```bash
cd ../frontend
npm install
npm start
```

This will:
- Install all required dependencies
- Start the React development server on port 3000
- Open your default browser to the application

### 6. Access the Complete Application

- **Frontend UI**: http://localhost:3000
- **API Endpoints**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### 7. Default Administrator Access

The system creates a default admin user on first startup:
- Username: `admin`
- Password: `admin`

**⚠️ Important Security Action**: Change the default admin password immediately after first login using the Change Password feature.

## Authentication Process Flow

The system implements a secure JWT-based authentication flow:

1. **User Registration**:
   - Client submits username, email, and password
   - Server validates input data
   - Password is hashed using PBKDF2-HMAC-SHA256
   - User record is created in database
   - Success response is returned (no auto-login)

2. **User Login**:
   - Client submits username and password
   - Server validates credentials
   - Server creates signed JWT with 1-hour expiration
   - Token is returned to client
   - Client stores token in localStorage

3. **Authenticated Requests**:
   - Client includes token in Authorization header
   - Server validates token signature and expiration
   - Server extracts username from token
   - Server verifies user exists in database
   - Request is processed if authentication succeeds

4. **Password Change**:
   - Client submits old and new passwords with token
   - Server validates token and old password
   - New password is hashed and stored
   - Success response indicates completion

5. **Logout Process**:
   - Client removes token from localStorage
   - No server-side action required (stateless authentication)
   - User must re-authenticate to access protected resources

## Detailed API Documentation

### Authentication Endpoints

#### `POST /login`
Authenticates a user and provides a JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Error Responses:**
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials

#### `POST /register`
Creates a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "message": "Registration successful"
}
```

**Error Responses:**
- `400 Bad Request`: Validation error or existing username/email

#### `GET /me`
Retrieves information about the authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "username": "string",
  "email": "string"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token

#### `POST /change-password`
Changes the password for the authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "oldPassword": "string",
  "newPassword": "string"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid new password
- `401 Unauthorized`: Invalid old password or token

### Customer Management Endpoints

#### `GET /customers`
Retrieves a list of all customers.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "customers": [
    {
      "id": 1,
      "name": "string",
      "internet_package": "string",
      "sector": "string",
      "date_added": "YYYY-MM-DD"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token

#### `POST /customers`
Adds a new customer.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "string",
  "internet_package": "string",
  "sector": "string"
}
```

**Response (200 OK):**
```json
{
  "message": "Customer added successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid token

## Data Validation Rules

### Username Validation
- 3-20 characters in length
- Only English letters (a-z, A-Z) and numbers (0-9)
- No spaces or special characters
- Required field (cannot be empty)

### Password Validation
- Minimum 8 characters
- Maximum 50 characters
- Must include at least one uppercase letter
- Must include at least one lowercase letter
- Must include at least one number
- Must include at least one special character
- Required field (cannot be empty)

### Email Validation
- Must follow standard email format (user@domain.tld)
- Required field (cannot be empty)

### Customer Name Validation
- Only English letters (a-z, A-Z) and spaces
- Minimum 2 characters
- Maximum 100 characters
- Required field (cannot be empty)

### Internet Package Validation
- Must be one of the predefined options:
  - "Basic (10 Mbps)"
  - "Standard (50 Mbps)"
  - "Premium (100 Mbps)"
  - "Enterprise (500 Mbps)"
- Required field (cannot be empty)

### Sector Validation
- Must be one of the predefined options:
  - "North"
  - "South"
  - "East"
  - "West"
  - "Central"
- Required field (cannot be empty)
