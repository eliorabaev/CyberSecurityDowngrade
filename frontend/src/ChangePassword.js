import React, { useState } from 'react';

function ChangePassword() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleChangePassword = async () => {
    // Simple validation
    if (newPassword !== confirmPassword) {
      setMessage("New passwords do not match");
      return;
    }

    try {
      // Frontend-only implementation for now
      setMessage("Password changed successfully! This is a frontend demo.");
      
      // When backend is ready, uncomment this code:
      /*
      const response = await fetch("http://localhost:8000/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Include authentication header when available
          // "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ currentPassword, newPassword })
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Password change failed");
      }
      */
    } catch (error) {
      setMessage("An error occurred");
      console.error("Change password error:", error);
    }
  };

  return (
    <div className="login-box">
      <div className="form-content">
        <h1>Change Password</h1>
        <p>Enter your current password and a new password</p>

        <input
          type="password"
          className="input-field"
          placeholder="Current Password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
        />
        <input
          type="password"
          className="input-field"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
        />
        <input
          type="password"
          className="input-field"
          placeholder="Confirm New Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />

        <button className="connect-button" onClick={handleChangePassword}>
          Update Password
        </button>

        <div className="links">
          <a href="/" className="link">Return to Login</a>
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