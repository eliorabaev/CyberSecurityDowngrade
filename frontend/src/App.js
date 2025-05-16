import React, { useState, useEffect } from 'react';
import config from './config';
import { useAuth } from './AuthContext';

// Import the components
import Register from './Register';
import ForgotPassword from './ForgotPassword';
import ChangePassword from './ChangePassword';
import CustomerManagement from './CustomerManagement';

function App() {
  // State to track current path and any success messages
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [successMessage, setSuccessMessage] = useState(null);
  
  // Login states
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [errorDetails, setErrorDetails] = useState("");
  const [showDetails, setShowDetails] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
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

  // Handle login
  const handleLogin = async () => {
    try {
      setIsLoading(true);
      setMessage("");
      setErrorDetails("");
      
      // Send login request to backend
      const response = await fetch(`${config.apiUrl}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      }).catch(error => {
        // Network error (server down, etc.)
        setMessage(`Server connection error. Please try again later.`);
        setErrorDetails(`Technical details: ${error.message}`);
        throw new Error("network_error");
      });

      // Parse the response JSON
      const data = await response.json().catch(error => {
        setMessage("Invalid response from server");
        setErrorDetails(`Failed to parse response: ${error.message}`);
        throw new Error("parse_error");
      });
      
      // Handle different response status codes
      if (response.ok) {
        // Login successful
        auth.login({ username }, data.access_token);
        setMessage(data.message || "Login successful");
      } else {
        // Handle different error status codes
        switch (response.status) {
          case 400:
            setMessage(`Validation error: ${data.message || data.detail || "Invalid input"}`);
            break;
          case 401:
            setMessage(`Authentication failed: ${data.message || data.detail || "Invalid username or password"}`);
            break;
          case 403:
            setMessage(`Account locked: ${data.message || data.detail || "Your account is locked"}`);
            break;
          case 429:
            setMessage(`Too many attempts: ${data.message || data.detail || "Please try again later"}`);
            break;
          case 500:
            setMessage(`Server error: ${data.message || data.detail || "Something went wrong"}`);
            if (data.traceback) {
              setErrorDetails(data.traceback);
            }
            break;
          default:
            setMessage(`Error: ${data.message || data.detail || "Unknown error occurred"}`);
        }
      }
    } catch (error) {
      // Only set message if we haven't already handled the specific error
      if (error.message !== "network_error" && error.message !== "parse_error") {
        setMessage(`Unexpected error: ${error.toString()}`);
        console.error("Login error:", error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Login component
  const renderLogin = () => {
    return (
      <div className="login-box">
        <div className="form-content">
          <h1>Welcome Admin</h1>
          <p>Sign in to continue</p>

          <div className="field-wrapper">
            <input
              type="text"
              className="input-field"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading}
            />
          </div>
          
          <div className="field-wrapper">
            <input
              type="password"
              className="input-field"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleLogin();
                }
              }}
            />
          </div>

          <button 
            className="connect-button" 
            onClick={handleLogin}
            disabled={isLoading}
          >
            {isLoading ? "Connecting..." : "Connect"}
          </button>

          <div className="links">
            <a href="/forgot-password" className="link">Forgot Password?</a>
            <a href="/register" className="link">Register</a>
          </div>
        </div>

        <div className="login-message-container">
          {/* Using dangerouslySetInnerHTML is intentionally vulnerable to XSS */}
          {message && <p className='login-message' dangerouslySetInnerHTML={{ __html: message }}></p>}
          
          {/* Display error details if available */}
          {errorDetails && (
            <div className="error-details">
              <p>
                <button 
                  onClick={() => setShowDetails(!showDetails)} 
                  className="details-toggle"
                >
                  {showDetails ? "Hide Details" : "Show Details"}
                </button>
              </p>
              
              {showDetails && (
                <pre className="error-details-content">{errorDetails}</pre>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Show loading state while authentication is initializing
  if (auth.loading) {
    return <div>Loading...</div>;
  }

  // Return the appropriate component based on the current path
  if (auth.isAuthenticated) {
    switch (currentPath) {
      case '/change-password':
        return <ChangePassword />;
      case '/dashboard':
      default:
        return <CustomerManagement successMessage={successMessage} />;
    }
  } else {
    // If not authenticated, show login or registration pages
    switch (currentPath) {
      case '/register':
        return <Register />;
      case '/forgot-password':
        return <ForgotPassword />;
      default:
        return renderLogin();
    }
  }
}

export default App;