import React, { useState } from 'react';

// Import the components we created
import Register from './Register';
import ForgotPassword from './ForgotPassword';
import ChangePassword from './ChangePassword';
import CustomerManagement from './CustomerManagement'; // Import the new component

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false); // New state to track login status

  const handleLogin = async () => {
    try {
      // For demonstration, we'll use a simple check
      // In a real app, you would validate against your backend
      if (username && password) {
        setIsLoggedIn(true);
        setMessage("Login successful!");
      } else {
        setMessage("Please enter both username and password");
      }
      
      // Commented backend code for future use
      /*
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
        setIsLoggedIn(true);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Login failed");
      }
      */
    } catch (error) {
      setMessage("An error occurred");
      console.error("Login error:", error);
    }
  };

  // If logged in, redirect to CustomerManagement
  if (isLoggedIn) {
    return <CustomerManagement />;
  }

  return (
    <div className="login-box">
      <div className="form-content">
        <h1>Welcome Admin</h1>
        <p>Sign in to continue</p>

        <input
          type="text"
          className="input-field"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          className="input-field"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

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
  // Simple routing logic based on URL path
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  // Listen for changes to the URL
  React.useEffect(() => {
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
  React.useEffect(() => {
    const handleClick = (e) => {
      // Find the closest anchor tag
      const anchor = e.target.closest('a');
      if (anchor && anchor.getAttribute('href').startsWith('/')) {
        e.preventDefault();
        navigate(anchor.getAttribute('href'));
      }
    };

    document.addEventListener('click', handleClick);
    return () => {
      document.removeEventListener('click', handleClick);
    };
  }, []);

  // Return the appropriate component based on the current path
  switch (currentPath) {
    case '/register':
      return <Register />;
    case '/forgot-password':
      return <ForgotPassword />;
    case '/change-password':
      return <ChangePassword />;
    case '/dashboard':
      return <CustomerManagement />;
    default:
      return <Login />;
  }
}

export default App;