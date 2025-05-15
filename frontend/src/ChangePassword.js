import React, { useState } from 'react';
import config from './config';
import { useAuth } from './AuthContext';

function ChangePassword() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Get auth context
  const auth = useAuth();

  // Simple handlers without validation
  const handleOldPasswordChange = (e) => {
    setOldPassword(e.target.value);
  };

  const handleNewPasswordChange = (e) => {
    setNewPassword(e.target.value);
  };

  const handleChangePassword = async () => {
    setIsLoading(true);
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
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(data.message);
        
        // After successful password change, redirect back to dashboard
        setTimeout(() => {
          window.location.href = "/dashboard?message=Password changed successfully!";
        }, 1500);
      } else {
        // Expose backend error message directly
        setMessage(data.detail || "Password change failed");
      }
    } catch (error) {
      // Expose detailed error information
      setMessage(`Error: ${error.toString()}`);
      console.error("Change password error:", error);
    } finally {
      setIsLoading(false);
    }
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
      </div>
    </div>
  );
}

export default ChangePassword;