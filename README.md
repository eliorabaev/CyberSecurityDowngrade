# Internet Service Provider Management System

A secure web application for managing internet service customers with a FastAPI backend and React frontend, featuring robust user authentication and session management.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

## Features

- 🔐 **Secure Authentication**: JWT-based user sessions with token management
- 👤 **User Management**: Register, login, and password management
- 👥 **Customer Management**: Add and view internet service customers
- 🔒 **Data Validation**: Comprehensive client and server-side validation
- 🌐 **Responsive UI**: Modern, responsive React-based interface

## Project Structure

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
│   ├── main.py              # FastAPI application
│   ├── auth_utils.py        # JWT authentication utilities
│   ├── password_utils.py    # Password hashing and verification utilities
│   ├── validation_utils.py  # Input validation utilities
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── .env                 # Frontend environment variables (not in git)
    ├── .env.example         # Example frontend environment variables
    ├── package.json         # Frontend dependencies
    ├── package-lock.json    # Dependency lock file (not in git)
    ├── public/              # Static files
    │   ├── favicon.ico
    │   ├── index.html
    │   └── robots.txt
    └── src/                 # React source code
        ├── App.js           # Main application component
        ├── App.css          # Main application styles
        ├── AuthContext.js   # Authentication context provider
        ├── config.js        # Configuration settings
        ├── index.js         # React entry point
        ├── index.css        # Global styles
        ├── utils/           # Utility functions
        │   └── validation.js # Client-side validation functions
        ├── ChangePassword.js
        ├── CustomerManagement.js
        ├── ForgotPassword.js
        └── Register.js
```

## Prerequisites

- Docker and Docker Compose
- Git
- Node.js and npm (for frontend development)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/eliorabaev/CyberSecurity.git
cd CyberSecurity
```

### 2. Set up environment variables

Create a `.env` file in the backend directory based on the `.env.example` template:

```bash
cd backend
cp .env.example .env
```

Then edit the `.env` file to set your database credentials and JWT secret:

```
# Database Configuration
DB_USER=your_username         # Choose your own username
DB_PASSWORD=your_password     # Choose your own secure password
DB_HOST=localhost             # Keep as localhost for local development
DB_NAME=internet_service_provider

# Docker specific variables
DB_ROOT_PASSWORD=root_password  # Change this for production
DB_PORT=3307                    # Change if port 3307 is already in use
API_PORT=8000                   # Change if port 8000 is already in use

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# Always use MySQL
USE_MYSQL=true

# Salt for password hashing
# This should be a long, random string
# You can generate one using: openssl rand -base64 32
PASSWORD_SALT=your_random_salt_string

# JWT Authentication
# Generate a secure secret key: openssl rand -hex 32
JWT_SECRET_KEY=your_jwt_secret_key
```

Also set up the frontend environment variables:

```bash
cd ../frontend
cp .env.example .env
```

The frontend `.env` file should contain:

```
# API connection settings
REACT_APP_API_HOST=localhost
REACT_APP_API_PORT=8000
```

### 3. Start the application with Docker Compose

```bash
cd ../backend  # Navigate to backend directory
docker-compose up -d
```

This will:
- Build the backend API container
- Start a MySQL database container
- Set up the required volumes and networking

### 4. Setup the Frontend

If you want to develop or run the frontend separately:

```bash
cd ../frontend
npm install
npm start
```

### 5. Access the application

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Default Login

The system creates a default admin user on startup:
- Username: `admin`
- Password: `admin`

**Important:** Change the default password after first login for security reasons.

## Authentication Flow

The system uses JWT (JSON Web Tokens) for secure, stateless authentication:

1. **Login**: User provides credentials → Server validates → Server issues JWT token
2. **Session Management**: Token is stored in client's localStorage
3. **Authentication**: Token is sent with every API request in the Authorization header
4. **Validation**: Server validates token for each protected endpoint
5. **Logout**: Token is removed from localStorage

## API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/login` | POST | No | Authenticate a user and receive JWT token |
| `/register` | POST | No | Create a new user account |
| `/me` | GET | Yes | Get current authenticated user info |
| `/change-password` | POST | Yes | Update user password (user-specific) |
| `/customers` | GET | Yes | Retrieve all customers |
| `/customers` | POST | Yes | Add a new customer |

### Authentication Headers

For protected endpoints, include the JWT token in request headers:

```
Authorization: Bearer <your_jwt_token>
```

## Frontend Components

The frontend uses React context for global state management, particularly for authentication:

- **AuthContext**: Manages user authentication state across components
- **Protected Routes**: Automatically redirects unauthorized users
- **User-Specific Actions**: Actions like password changes only affect the logged-in user

## Security Features

- **JWT Authentication**: Secure, stateless authentication with expiring tokens
- **Password Hashing**: Passwords are securely hashed using PBKDF2-HMAC-SHA256 with a high iteration count
- **Token-Based User Sessions**: Each user has their own session with personalized actions
- **Input Validation**: All inputs are validated on both client and server sides
- **Authorization Checks**: API endpoints verify user identity before performing actions
- **Secure Authentication**: Login system provides minimal error information to prevent username enumeration

## Validation Rules

- **Username**: 3-20 characters, only English letters and numbers (no spaces or special characters)
- **Password**: At least 8 characters, must include uppercase, lowercase, numbers, and special characters
- **Customer Name**: Only English letters and spaces allowed

## Troubleshooting

### Authentication Issues

If you encounter authentication problems:

1. Check browser console for token-related errors
2. Verify that the JWT_SECRET_KEY is properly set in your backend .env file
3. Check token expiration (default is 60 minutes)
4. Clear localStorage and try logging in again

### Database Connection Issues

If you encounter database connection problems:

1. Check your `.env` file for correct credentials
2. Verify that the MySQL container is running:
   ```bash
   cd backend
   docker-compose ps
   ```
3. Check container logs:
   ```bash
   docker-compose logs db
   docker-compose logs backend
   ```

### API Connection From Frontend

If the frontend can't connect to the API:

1. Verify the API URL in the frontend's `.env` file
2. Check CORS settings in `main.py` if you're using different hosts or ports
3. Ensure authentication headers are properly formatted

### Password Salt Issues

If you encounter authentication problems after setting up:

1. Make sure you've set a valid `PASSWORD_SALT` value in your `.env` file
2. The salt must be a valid base64-encoded string
3. If you change the salt after users are created, existing users won't be able to log in

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for providing an excellent API framework
- React for the powerful frontend library
- MySQL for reliable database services