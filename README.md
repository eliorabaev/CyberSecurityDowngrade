# Internet Service Provider Management System (Communication_LTD)

A web application for managing internet service customers with a FastAPI backend and React frontend, **deliberately containing security vulnerabilities for educational purposes**.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.2.0-green.svg)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-teal.svg)
![React](https://img.shields.io/badge/react-19.0.0-61DAFB.svg?logo=react&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg?logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg?logo=docker&logoColor=white)
![Security](https://img.shields.io/badge/security-VULNERABLE-red.svg)
![Maintenance](https://img.shields.io/badge/maintained-yes-brightgreen.svg)
![PBKDF2](https://img.shields.io/badge/PBKDF2-1,200,000%20iterations-red.svg)
![JWT](https://img.shields.io/badge/JWT-authentication-yellow.svg)
![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

## ⚠️ IMPORTANT SECURITY NOTICE ⚠️

**This application intentionally contains security vulnerabilities for educational and demonstration purposes.**

The following security vulnerabilities have been deliberately introduced:

1. **Cross-Site Scripting (XSS)**: The customer management endpoints do not perform HTML escaping or sanitization, making the application vulnerable to XSS attacks.

2. **SQL Injection**: The application has been modified to remove SQL safety measures in multiple routes, allowing SQL injection attacks.

**DO NOT USE THIS APPLICATION IN PRODUCTION ENVIRONMENTS OR WITH REAL DATA.**

This version is intended solely for:
- Educational demonstrations
- Security training workshops
- Vulnerability testing practice
- Understanding the impact of common web vulnerabilities

## Quick Start

⚠️ **Important Note for Users from the Original Repository**: If you're coming from the original repository at https://github.com/eliorabaev/CyberSecurity, you need to run the following command to properly rebuild the project with the vulnerable version:

```bash
docker compose down -v && docker compose up --build
```

This ensures all volumes are removed and the project is rebuilt from scratch with the vulnerable code.

For new installations:

```bash
# Clone the repository
git clone https://github.com/eliorabaev/CyberSecurityDowngrade.git && cd CyberSecurityDowngrade

# Start the backend (Docker required)
cd backend && cp .env.example .env

# Update Web3Forms API key in .env file (required for password reset)
# Get your free API key from https://web3forms.com
# Replace your_actual_api_key_here with your key
sed -i 's/enter_your_api_key_here/your_actual_api_key_here/' .env

# Start backend services
docker-compose up -d

# Start the frontend
cd ../frontend && cp .env.example .env && npm install && npm start
```

Default admin credentials: `admin` / `admin` (change immediately after first login)

## Project Requirements Checklist

This project implements all the required features as specified in the original requirements:

### Part A: Secure Development Principles

✅ 1. **User Registration**
   - User creation with username and email
   - Password storage using PBKDF2-HMAC-SHA256 with salt
   - Email collection for validation and password reset

✅ 2. **Password Change**
   - Current password verification
   - New password validation

✅ 3. **Login System**
   - Username and password input
   - Proper authentication flow
   - Appropriate user verification and responses

✅ 4. **Customer Management**
   - New customer creation with validated information
   - Customer data display

✅ 5. **Password Reset**
   - Forgot password flow with email verification
   - SHA-1 value generation for verification code
   - Verification code validation
   - New password creation

### Part B: Deliberate Security Vulnerabilities

✅ 1. **Cross-Site Scripting (XSS)**
   - Customer management interfaces are vulnerable to stored XSS attacks
   - Customer name and other fields are not sanitized before display

✅ 2. **SQL Injection**
   - Multiple endpoints vulnerable to SQL injection:
     - User registration system
     - Login functionality
     - Customer management
   - SQL injection results are displayed in the UI for educational purposes

## Note on Password Validation

The application includes comprehensive password validation through the `password_config.py` configuration file. This file contains important settings that control the password requirements:

```python
# Minimum password length
MIN_LENGTH = 10

# Maximum password length
MAX_LENGTH = 50

# Whether to require at least one uppercase letter
REQUIRE_UPPERCASE = True

# Whether to require at least one lowercase letter
REQUIRE_LOWERCASE = True

# Whether to require at least one number
REQUIRE_NUMBERS = True

# Whether to require at least one special character
REQUIRE_SPECIAL_CHARS = True

# Password history - number of previous passwords to check against
PASSWORD_HISTORY_LENGTH = 3

# List of common passwords that are not allowed (dictionary passwords)
DISALLOWED_PASSWORDS = [
    "password",
    "123456",
    # Many more entries...
]
```

The application verifies passwords against these configuration settings during:
- User registration
- Password change
- Password reset

This includes checking:
- Password complexity requirements
- Password history (preventing reuse of the last 3 passwords)
- Dictionary-based validation (preventing common passwords)

## Table of Contents
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Deliberate Security Vulnerabilities](#deliberate-security-vulnerabilities)
- [Prerequisites](#prerequisites)
- [Comprehensive Setup Guide](#comprehensive-setup-guide)
- [SQL Injection Testing Guide](#sql-injection-testing-guide)
- [XSS Vulnerability Testing Guide](#xss-vulnerability-testing-guide)
- [Authentication Process Flow](#authentication-process-flow)
- [API Documentation](#api-documentation)

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│                 │      │                  │      │                  │
│ React Frontend  │◄────►│ FastAPI Backend  │◄────►│  MySQL Database  │
│                 │      │                  │      │                  │
└─────────────────┘      └──────────────────┘      └──────────────────┘
```

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **PyJWT**: JSON Web Token implementation
- **MySQL**: Relational database system

### Frontend
- **React**: JavaScript library for building user interfaces
- **React Context API**: State management across components
- **HTML5/CSS3**: Modern layout and styling
- **Fetch API**: Network requests to backend services

### Infrastructure
- **Docker & Docker Compose**: Containerization and orchestration

## Deliberate Security Vulnerabilities

### XSS Vulnerability

The Customer Management features have been deliberately modified to remove output escaping and sanitization protections:

1. **Vulnerable Code**:
   ```javascript
   // Helper function to unsafely render HTML (vulnerable to XSS)
   const createUnsafeDisplay = (str) => {
     return <span dangerouslySetInnerHTML={{ __html: str }} />;
   };
   ```

2. **Testing XSS**:
   - Add a new customer with name: `<img src="x" onerror="alert('XSS')">`
   - View the customer list to see the script execute

### SQL Injection Vulnerability

The application has been modified to remove SQL protection measures:

1. **Vulnerable Code Examples**:
   ```python
   # Direct string concatenation without parameterization
   query = f"SELECT * FROM users WHERE username = '{username}'"
   ```
   
## XSS Vulnerability Testing Guide

To test the XSS vulnerabilities:

1. **Basic Alert Script:**
   ```html
   <img src="x" onerror="alert('XSS')">
   ```

2. **Cookie Stealing (Demonstration Only):**
   ```html
   <img src="x" onerror="console.log(document.cookie)">
   ```

3. **UI Manipulation:**
   ```html
   <div style="position:fixed;top:0;left:0;width:100%;height:100%;background:black;color:red;font-size:50px;text-align:center;padding-top:20%;">System Compromised</div>
   ```

## Prerequisites

- **Docker and Docker Compose** (v1.29+)
- **Git**
- **Node.js** (v14+) and **npm** (v6+)
- Modern web browser (Chrome, Firefox, Edge, or Safari)

## Comprehensive Setup Guide

### 1. Clone the repository

```bash
git clone https://github.com/eliorabaev/CyberSecurityDowngrade.git
cd CyberSecurityDowngrade
```

### 2. Backend Configuration

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file with appropriate values:

```
# Database Configuration
DB_USER=isp_user
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_NAME=internet_service_provider

# Docker specific variables
DB_ROOT_PASSWORD=root_password
DB_PORT=3307
API_PORT=8000

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# Web3Forms API Key (for email functionality)
# Replace with your actual Web3Forms API key for password reset emails
# Get your key from https://web3forms.com
WEB3FORMS_API_KEY=enter_your_api_key_here
```

### 3. Start the Backend Services

```bash
docker-compose up -d
```

### 4. Frontend Configuration

```bash
cd ../frontend
cp .env.example .env
```

### 5. Start the Frontend Development Server

```bash
npm install
npm start
```

### 6. Access the Application

- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

### 7. Default Administrator Access

- Username: `admin`
- Password: `admin`

## Authentication Process Flow

The system implements a JWT-based authentication flow:

1. **User Registration**:
   - Client submits username, email, and password
   - Password is hashed using PBKDF2-HMAC-SHA256
   - User record is created in database

2. **User Login**:
   - Client submits username and password
   - Server validates credentials
   - On success, server creates signed JWT with 1-hour expiration
   - Token is returned to client and stored in localStorage

3. **Password Reset Flow**:
   - User requests password reset by entering email
   - System generates SHA-1 verification code with 20-minute expiration
   - In development mode, code appears in server console
   - In production mode, code is sent via Web3Forms email service
   - User enters verification code for validation
   - After successful validation, user sets new password

## Testing Password Reset (Development Mode)

When testing the password reset functionality, there are two modes:

1. **Development Mode** (No API Key):
   - If no Web3Forms API Key is provided in the `.env` file
   - Verification codes will be printed to the server console
   - Look for messages like: `[DEV MODE] Password reset verification code for user@example.com: a1b2c3d4e5`

2. **Production Mode** (With API Key):
   - If a valid Web3Forms API Key is provided in the `.env` file
   - Verification codes will be sent to the email address associated with the account
   - You must use a real email address when registering to receive the verification code

To get a Web3Forms API Key:
1. Sign up at [Web3Forms.com](https://web3forms.com/)
2. Get your free API key from the dashboard
3. Update your `.env` file with the API key

## API Documentation

### Authentication Endpoints

- `POST /login`: User authentication with credentials
- `POST /register`: New user registration
- `POST /forgot-password`: Initiate password reset
- `POST /verify-reset-token`: Verify password reset code
- `POST /reset-password`: Complete password reset
- `GET /me`: Retrieve current user information
- `POST /change-password`: Change password for authenticated user

### Customer Management Endpoints

- `GET /customers`: Retrieve all customers
- `POST /customers`: Add a new customer

See the [API Documentation](http://localhost:8000/docs) for complete details.

## Final Security Warning

This application intentionally contains security vulnerabilities for educational and demonstration purposes only. **DO NOT use this version in production environments or with real user data.**

After completing your security demonstrations or training, consider implementing proper security measures to address these vulnerabilities, or switch to a secure version of the application.
