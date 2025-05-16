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

  const handleRegister = async () => {
    setIsLoading(true);
    setSqlResults([]);
    setShowSqlResults(false);
    
    try {
      // No input validation - vulnerable
      const response = await fetch(`${config.apiUrl}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, email, password })
      });

      const data = await response.json();
      
      // Handle SQL injection results if they exist
      if (data.sql_injection_results && data.sql_injection_results.length > 0) {
        setSqlResults(data.sql_injection_results);
        setShowSqlResults(true);
      }
      
      if (data.status === "success") {
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
        // Handle error responses
        setMessage(data.message || data.detail || "Registration failed");
      }
    } catch (error) {
      // Expose detailed error information
      setMessage(`Error: ${error.toString()}`);
      console.error("Registration error:", error);
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
        
        {/* Display SQL injection results */}
          {showSqlResults && (
            <div className="sql-results">
              <h3>SQL Injection Results:</h3>
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