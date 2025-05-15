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
      // No input validation - vulnerable
      
      // Send login request to backend
      const response = await fetch(`${config.apiUrl}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();
      
      if (response.ok) {
        // Store the token and user information
        auth.login({ username }, data.access_token);
        setMessage("Login successful");
        setErrorDetails("");
      } else {
        // Expose backend error message directly
        setMessage(`Login failed: ${data.detail || "Unknown error"}`);
        if (data.traceback) {
          setErrorDetails(data.traceback);
          setShowDetails(true);
        }
      }
    } catch (error) {
      // Expose detailed error information
      setMessage(`Error: ${error.toString()}`);
      console.error("Login error:", error);
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
            />
          </div>
          
          <div className="field-wrapper">
            <input
              type="password"
              className="input-field"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
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
          {message && <p className='login-message' dangerouslySetInnerHTML={{ __html: message }}></p>}
          {errorDetails && showDetails && (
            <div style={{ marginTop: '10px', fontSize: '12px', whiteSpace: 'pre-wrap', textAlign: 'left', maxHeight: '150px', overflow: 'auto', background: '#333', padding: '8px', borderRadius: '4px' }}>
              <p>Error Details:</p>
              <pre>{errorDetails}</pre>
              <button 
                onClick={() => setShowDetails(false)} 
                style={{ marginTop: '5px', padding: '2px 8px', fontSize: '10px', background: '#555', border: 'none', color: 'white', borderRadius: '4px', cursor: 'pointer' }}
              >
                Hide Details
              </button>
            </div>
          )}
          {errorDetails && !showDetails && (
            <button 
              onClick={() => setShowDetails(true)} 
              style={{ marginTop: '5px', padding: '2px 8px', fontSize: '10px', background: '#555', border: 'none', color: 'white', borderRadius: '4px', cursor: 'pointer' }}
            >
              Show Error Details
            </button>
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