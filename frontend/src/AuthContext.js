import React, { createContext, useState, useContext, useEffect } from 'react';

// Create the Auth Context
const AuthContext = createContext(null);

// Auth Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  
  // Check if token exists on load
  useEffect(() => {
    if (token) {
      // For simplicity, just parse the token to get the username
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser({ username: payload.sub });
      } catch (e) {
        console.error("Invalid token", e);
        localStorage.removeItem('token');
        setToken(null);
      }
    }
    setLoading(false);
  }, []);
  
  const login = (userData, authToken) => {
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('token', authToken);
  };
  
  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };
  
  // Value provided to consumers of this context
  const value = {
    user,
    token,
    login,
    logout,
    isAuthenticated: !!user,
    loading
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};