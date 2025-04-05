import React, { useState } from 'react';
import config from './config';
import { validatePassword } from './utils/validation';
import { useAuth } from './AuthContext';

function ChangePassword() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [fieldErrors, setFieldErrors] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Get auth context
  const auth = useAuth();

  // Handle changes to old password (clear error when field is filled)
  const handleOldPasswordChange = (e) => {
    const value = e.target.value;
    setOldPassword(value);
    
    // If form was submitted and there was an error that's now fixed
    if (formSubmitted && fieldErrors.oldPassword && value) {
      setFieldErrors({...fieldErrors, oldPassword: ''});
    }
  };

  // Handle changes to new password (clear error when validation passes)
  const handleNewPasswordChange = (e) => {
    const value = e.target.value;
    setNewPassword(value);
    
    // If form was submitted and there was an error that's now fixed
    if (formSubmitted && fieldErrors.newPassword) {
      const validation = validatePassword(value);
      if (validation.isValid) {
        setFieldErrors({...fieldErrors, newPassword: ''});
      }
    }
    
    // Also check if confirm password error should be cleared
    if (formSubmitted && fieldErrors.confirmPassword && value === confirmPassword) {
      setFieldErrors(prev => ({...prev, confirmPassword: ''}));
    }
  };

  // Handle changes to confirm password (clear error when matches)
  const handleConfirmPasswordChange = (e) => {
    const value = e.target.value;
    setConfirmPassword(value);
    
    // If form was submitted and there was an error that's now fixed
    if (formSubmitted && fieldErrors.confirmPassword && value === newPassword) {
      setFieldErrors({...fieldErrors, confirmPassword: ''});
    }
  };

  const handleChangePassword = async () => {
    // Mark form as submitted to show validation errors
    setFormSubmitted(true);
    
    // Validate all fields
    const errors = {
      oldPassword: oldPassword ? '' : "Old password is required",
      newPassword: newPassword ? validatePassword(newPassword).errorMessage : "New password is required",
      confirmPassword: confirmPassword !== newPassword ? "Passwords do not match" : ''
    };

    setFieldErrors(errors);

    // Check if there are any validation errors
    if (Object.values(errors).some(error => error !== '')) {
      setMessage("Please fix the form errors before submitting");
      return;
    }

    setIsLoading(true);
    try {
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
        <p>Change password for {auth.user?.username}</p>

        <div className="field-wrapper">
          <input
            type="password"
            className={`input-field ${formSubmitted && fieldErrors.oldPassword ? 'input-error' : ''}`}
            placeholder="Old Password"
            value={oldPassword}
            onChange={handleOldPasswordChange}
            disabled={isLoading}
          />
          {formSubmitted && fieldErrors.oldPassword && 
            <div className="error-message">{fieldErrors.oldPassword}</div>
          }
        </div>

        <div className="field-wrapper">
          <input
            type="password"
            className={`input-field ${formSubmitted && fieldErrors.newPassword ? 'input-error' : ''}`}
            placeholder="New Password"
            value={newPassword}
            onChange={handleNewPasswordChange}
            disabled={isLoading}
          />
          {formSubmitted && fieldErrors.newPassword && 
            <div className="error-message">{fieldErrors.newPassword}</div>
          }
          <div className="requirements-text">
            Password must be at least 8 characters and include uppercase, lowercase, 
            numbers, and special characters.
          </div>
        </div>

        <div className="field-wrapper">
          <input
            type="password"
            className={`input-field ${formSubmitted && fieldErrors.confirmPassword ? 'input-error' : ''}`}
            placeholder="Confirm New Password"
            value={confirmPassword}
            onChange={handleConfirmPasswordChange}
            disabled={isLoading}
          />
          {formSubmitted && fieldErrors.confirmPassword && 
            <div className="error-message">{fieldErrors.confirmPassword}</div>
          }
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
        {message && <p className='login-message'>{message}</p>}
      </div>
    </div>
  );
}

export default ChangePassword;