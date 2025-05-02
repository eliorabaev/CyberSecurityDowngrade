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
  
  // Validation rules
  validation: {
    username: {
      pattern: /^[a-zA-Z0-9]+$/, // Only English letters and numbers
      minLength: 3,
      maxLength: 20,
      errorMessages: {
        pattern: "Username can only contain English letters and numbers without spaces",
        minLength: "Username must be at least 3 characters",
        maxLength: "Username cannot exceed 20 characters",
        required: "Username is required"
      }
    },
    password: {
      minLength: 8,
      maxLength: 50,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecial: true,
      specialChars: "!@#$%^&*()_-+=<>?/[]{}|",
      errorMessages: {
        minLength: "Password must be at least 10 characters",
        maxLength: "Password cannot exceed 50 characters",
        requireUppercase: "Password must include at least one uppercase letter",
        requireLowercase: "Password must include at least one lowercase letter",
        requireNumbers: "Password must include at least one number",
        requireSpecial: "Password must include at least one special character",
        required: "Password is required"
      }
    },
    customerName: {
      pattern: /^[a-zA-Z\s]+$/, // Only English letters and spaces
      minLength: 2,
      maxLength: 50,
      errorMessages: {
        pattern: "Customer name can only contain English letters and spaces",
        minLength: "Customer name must be at least 2 characters",
        maxLength: "Customer name cannot exceed 50 characters",
        required: "Customer name is required"
      }
    }
  },
  
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