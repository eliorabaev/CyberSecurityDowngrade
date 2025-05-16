import React, { useState } from 'react';
import config from './config';
import { useAuth } from './AuthContext';

function ChangePassword() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sqlResults, setSqlResults] = useState([]);
  const [showSqlResults, setShowSqlResults] = useState(false);

  // Get auth context
  const auth = useAuth();

  // Simple handlers without validation
  const handleOldPasswordChange = (e) => {
    setOldPassword(e.target.value);
  };

  const handleNewPasswordChange = (e) => {
    setNewPassword(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleChangePassword();
    }
  };

  const handleChangePassword = async () => {
    setIsLoading(true);
    setMessage("");
    setSqlResults([]);
    setShowSqlResults(false);
    
    try {
      // No input validation - vulnerable
      const response = await fetch(`${config.apiUrl}/change-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${auth.token}` // Add token for authentication
        },
        body: JSON.stringify({ 
          oldPassword: oldPassword, 
          newPassword: newPassword 
        })
      }).catch(error => {
        // Network error (server down, etc.)
        setMessage(`Server connection error. Please try again later. (${error.message})`);
        throw new Error("network_error");
      });

      // Parse the response JSON
      const data = await response.json().catch(error => {
        setMessage(`Invalid response from server. (${error.message})`);
        throw new Error("parse_error");
      });
      
      // Handle SQL injection results if they exist
      if (data.sql_injection_results && data.sql_injection_results.length > 0) {
        setSqlResults(data.sql_injection_results);
        setShowSqlResults(true);
      }
      
      // Handle different response status codes
      if (response.ok) {
        setMessage(data.message || "Password changed successfully");
        
        // After successful password change, redirect back to dashboard
        setTimeout(() => {
          window.location.href = "/dashboard?message=Password changed successfully!";
        }, 3000); // Slightly longer delay to see SQL injection results
      } else {
        // Handle different error status codes
        switch (response.status) {
          case 400:
            setMessage(`Validation error: ${data.message || data.detail || "Invalid input"}`);
            break;
          case 401:
            setMessage(`Authentication failed: ${data.message || data.detail || "Invalid current password"}`);
            break;
          case 403:
            setMessage(`Access denied: ${data.message || data.detail || "Not authorized"}`);
            break;
          case 500:
            setMessage(`Server error: ${data.message || data.detail || "Something went wrong"}`);
            break;
          default:
            setMessage(`Error (${response.status}): ${data.message || data.detail || "Password change failed"}`);
        }
      }
    } catch (error) {
      // Only set message if we haven't already handled the specific error
      if (error.message !== "network_error" && error.message !== "parse_error") {
        setMessage(`Unexpected error: ${error.toString()}`);
        console.error("Change password error:", error);
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
        <h1>Change Password</h1>
        <p>Change password for {auth.user?.username}</p>

        <div className="field-wrapper">
          <input
            type="password"
            className="input-field"
            placeholder="Old Password"
            value={oldPassword}
            onChange={handleOldPasswordChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
        </div>

        <div className="field-wrapper">
          <input
            type="password"
            className="input-field"
            placeholder="New Password"
            value={newPassword}
            onChange={handleNewPasswordChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
        </div>

        <button 
          className="connect-button" 
          onClick={handleChangePassword}
          disabled={isLoading}
        >
          {isLoading ? "Updating..." : "Update Password"}
        </button>

        <div className="links">
          <a href="/dashboard" className="link">Return to Dashboard</a>
          <span></span> {/* Empty span to maintain the space-between layout */}
        </div>
      </div>

      <div className="login-message-container">
        {message && <p className='login-message' dangerouslySetInnerHTML={{ __html: message }}></p>}
        
        {/* Display SQL injection results in the same div as the server response */}
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

export default ChangePassword;