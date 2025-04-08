import React, { useState, useEffect } from 'react';
import config from './config';
import { useAuth } from './AuthContext';

// Import the components
import Register from './Register';
import ForgotPassword from './ForgotPassword';
import ChangePassword from './ChangePassword';
import CustomerManagement from './CustomerManagement';

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [fieldErrors, setFieldErrors] = useState({
    username: '',
    password: ''
  });
  
  // Use the auth context
  const auth = useAuth();

  const handleLogin = async () => {
    try {
      // Reset errors
      setFieldErrors({
        username: '',
        password: ''
      });
      
      // Form validation
      const errors = {
        username: username ? '' : "Username is required",
        password: password ? '' : "Password is required"
      };
      
      setFieldErrors(errors);
      
      // Check if there are any validation errors
      if (!username || !password) {
        setMessage("Please enter both username and password");
        return;
      }
      
      // Send login request to backend
      const response = await fetch(`${config.apiUrl}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        // Store the token and user information
        auth.login({ username }, data.access_token);
        setMessage("Login successful");
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Login failed");
      }
    } catch (error) {
      setMessage("Error connecting to server");
      console.error("Login error:", error);
    }
  };

  // If logged in, redirect to CustomerManagement
  if (auth.isAuthenticated) {
    return <CustomerManagement />;
  }

  return (
    <div className="login-box">
      <div className="form-content">
        <h1>Welcome Admin</h1>
        <p>Sign in to continue</p>

        <div className="field-wrapper">
          <input
            type="text"
            className={`input-field ${fieldErrors.username ? 'input-error' : ''}`}
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          {fieldErrors.username && <div className="error-message">{fieldErrors.username}</div>}
        </div>
        
        <div className="field-wrapper">
          <input
            type="password"
            className={`input-field ${fieldErrors.password ? 'input-error' : ''}`}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {fieldErrors.password && <div className="error-message">{fieldErrors.password}</div>}
        </div>

        <button className="connect-button" onClick={handleLogin}>
          Connect
        </button>

        <div className="links">
          <a href="/forgot-password" className="link">Forgot Password?</a>
          <a href="/register" className="link">Register</a>
        </div>
      </div>

      <div className="login-message-container">
        {message && <p className='login-message'>{message}</p>}
      </div>
    </div>
  );
}

function App() {
  // State to track current path and any success messages
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [successMessage, setSuccessMessage] = useState(null);
  
  // Get auth context
  const auth = useAuth();

  // Parse URL for any success messages
  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const message = queryParams.get('message');
    
    if (message) {
      setSuccessMessage(message);
      
      // Remove the query parameter from the URL without refreshing the page
      const newUrl = window.location.pathname;
      window.history.replaceState({}, '', newUrl);
    }
  }, [window.location.search]);

  // Listen for changes to the URL
  useEffect(() => {
    const onLocationChange = () => {
      setCurrentPath(window.location.pathname);
    };

    // Listen for the popstate event (back/forward browser navigation)
    window.addEventListener('popstate', onLocationChange);

    return () => {
      window.removeEventListener('popstate', onLocationChange);
    };
  }, []);

  // Handle navigation
  const navigate = (path) => {
    window.history.pushState({}, '', path);
    setCurrentPath(path);
  };

  // Override the default behavior of anchor tags
  useEffect(() => {
    const handleClick = (e) => {
      // Find the closest anchor tag
      const anchor = e.target.closest('a');
      if (anchor && anchor.getAttribute('href') && anchor.getAttribute('href').startsWith('/')) {
        e.preventDefault();
        navigate(anchor.getAttribute('href'));
      }
    };

    document.addEventListener('click', handleClick);
    return () => {
      document.removeEventListener('click', handleClick);
    };
  }, []);

  // Show loading state while authentication is initializing
  if (auth.loading) {
    return <div>Loading...</div>;
  }

  // Return the appropriate component based on the current path
  switch (currentPath) {
    case '/register':
      return <Register />;
    case '/forgot-password':
      return <ForgotPassword />;
    case '/change-password':
      return auth.isAuthenticated ? <ChangePassword /> : <Login />;
    case '/dashboard':
      return auth.isAuthenticated ? <CustomerManagement successMessage={successMessage} /> : <Login />;
    default:
      return <Login />;
  }
}

export default App;