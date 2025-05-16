import React, { useState } from 'react';
import config from './config';

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sqlResults, setSqlResults] = useState([]);
  const [showSqlResults, setShowSqlResults] = useState(false);

  const handleUsernameChange = (e) => {
    setUsername(e.target.value);
  };

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleRegister();
    }
  };

  const handleRegister = async () => {
    setIsLoading(true);
    setSqlResults([]);
    setShowSqlResults(false);
    setMessage("");
    
    try {
      // No input validation - vulnerable
      const response = await fetch(`${config.apiUrl}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, email, password })
      }).catch(error => {
        // Network error (server down, etc.)
        setMessage(`Server connection error. Please try again later. (${error.message})`);
        throw new Error("network_error");
      });

      const data = await response.json().catch(error => {
        setMessage(`Invalid response from server. (${error.message})`);
        throw new Error("parse_error");
      });
      
      // Handle SQL injection results if they exist
      if (data.sql_injection_results && data.sql_injection_results.length > 0) {
        setSqlResults(data.sql_injection_results);
        setShowSqlResults(true);
      }
      
      // Handle response based on status code
      if (response.ok) {
        setMessage(data.message || "Registration successful");
        
        // Clear fields after successful registration
        setUsername("");
        setEmail("");
        setPassword("");
        
        // Redirect to login page after 5 seconds (longer to view SQL results)
        setTimeout(() => {
          window.location.href = "/";
        }, 5000);
      } else {
        // Handle different error status codes
        switch (response.status) {
          case 400:
            setMessage(`Validation error: ${data.message || "All fields are required"}`);
            break;
          case 409:
            setMessage(`Registration failed: ${data.message || "Username or email already exists"}`);
            break;
          case 500:
            setMessage(`Server error: ${data.message || "Something went wrong"}`);
            break;
          default:
            setMessage(`Error (${response.status}): ${data.message || data.detail || "Registration failed"}`);
        }
      }
    } catch (error) {
      // Only set message if we haven't already handled the specific error
      if (error.message !== "network_error" && error.message !== "parse_error") {
        setMessage(`Unexpected error: ${error.toString()}`);
        console.error("Registration error:", error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Format JSON for display
  const formatJson = (json) => {
    return JSON.stringify(json, null, 2);
  };

  return (
    <div className="login-box">
      <div className="form-content">
        <h1>Create Account</h1>
        <p>Please fill in your details</p>

        <div className="field-wrapper">
          <input
            type="text"
            className="input-field"
            placeholder="Username"
            value={username}
            onChange={handleUsernameChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
        </div>

        <div className="field-wrapper">
          <input
            type="email"
            className="input-field"
            placeholder="Email"
            value={email}
            onChange={handleEmailChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
        </div>

        <div className="field-wrapper">
          <input
            type="password"
            className="input-field"
            placeholder="Password"
            value={password}
            onChange={handlePasswordChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
        </div>

        <button 
          className="connect-button" 
          onClick={handleRegister}
          disabled={isLoading}
        >
          {isLoading ? "Registering..." : "Register"}
        </button>

        <div className="links">
          <a href="/" className="link">Already have an account?</a>
          <a href="/" className="link">Login</a>
        </div>
      </div>

      <div className="login-message-container">
        {message && <p className='login-message' dangerouslySetInnerHTML={{ __html: message }}></p>}
        
        {/* Display SQL injection results in the same div as the server response */}
        {showSqlResults && (
          <div className="sql-results">
            <pre>
              {formatJson(sqlResults)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default Register;