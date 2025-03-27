import React, { useState } from 'react';

function ChangePassword() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChangePassword = async () => {
    // Simple validation
    if (!oldPassword || !newPassword) {
      setMessage("Please enter both old and new password");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          oldPassword: oldPassword, 
          newPassword: newPassword 
        })
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
        
        // After successful password change, redirect back to dashboard
        setTimeout(() => {
          window.location.href = "/dashboard?message=Password changed successfully!";
        }, 1500);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Password change failed");
      }
    } catch (error) {
      console.error("Change password error:", error);
      setMessage("Error connecting to server");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-box">
      <div className="form-content">
        <h1>Change Password</h1>
        <p>Enter your old password and a new password</p>

        <input
          type="password"
          className="input-field"
          placeholder="Old Password"
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
          disabled={isLoading}
        />
        <input
          type="password"
          className="input-field"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          disabled={isLoading}
        />

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
        {message && <p className='login-message'>{message}</p>}
      </div>
    </div>
  );
}

export default ChangePassword;