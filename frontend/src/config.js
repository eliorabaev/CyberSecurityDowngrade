// Configuration settings for the frontend application

// Get API URL from environment variables or use default
// In development with Create React App, env variables must start with REACT_APP_
const API_PORT = process.env.REACT_APP_API_PORT || '8000';
const API_HOST = process.env.REACT_APP_API_HOST || 'localhost';

// Configuration object
const config = {
  // API URL for backend requests
  apiUrl: `http://${API_HOST}:${API_PORT}`,
  
  // Default timeout for API requests in milliseconds
  defaultTimeoutMs: 10000,
  
  // Authentication settings
  authTokenKey: 'auth_token', // localStorage key for auth token
  
  // Available packages and sectors for dropdown menus
  availablePackages: [
    "Basic (10 Mbps)", 
    "Standard (50 Mbps)", 
    "Premium (100 Mbps)", 
    "Enterprise (500 Mbps)"
  ],
  
  availableSectors: [
    "North", 
    "South", 
    "East", 
    "West", 
    "Central"
  ]
};

export default config;