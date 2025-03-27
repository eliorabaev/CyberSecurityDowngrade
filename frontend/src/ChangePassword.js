import React, { useState } from 'react';

function ChangePassword() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleChangePassword = async () => {
    // Simple validation
    if (!oldPassword || !newPassword) {
      setMessage("Please enter both old and new password");
      return;
    }

    try {
      // Frontend-only implementation for now
      // In real app, you would send request to the backend
      
      // Simulating successful password change
      setMessage("Password changed successfully!");
      
      // After 1 second, redirect back to admin panel with success message
      setTimeout(() => {
        // Navigate back to dashboard with success message
        window.location.href = "/dashboard?message=Password changed successfully!";
      }, 1000);
      
      // When backend is ready, uncomment this code:
      /*
      const response = await fetch("http://localhost:8000/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Include authentication header when available
          // "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ oldPassword, newPassword })
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
        
        // After successful password change, redirect back to dashboard
        setTimeout(() => {
          window.location.href = "/dashboard?message=Password changed successfully!";
        }, 1000);
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
        <p>Enter your old password and a new password</p>

        <input
          type="password"
          className="input-field"
          placeholder="Old Password"
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
        />
        <input
          type="password"
          className="input-field"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
        />

        <button className="connect-button" onClick={handleChangePassword}>
          Update Password
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