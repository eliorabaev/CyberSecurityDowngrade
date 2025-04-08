import React, { useState } from 'react';
import config from './config';

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({
    email: ''
  });
  const [touchedFields, setTouchedFields] = useState({
    email: false
  });

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      return { isValid: false, errorMessage: "Email is required" };
    }
    if (!emailRegex.test(email)) {
      return { isValid: false, errorMessage: "Please enter a valid email address" };
    }
    return { isValid: true, errorMessage: '' };
  };

  const handleBlur = (field) => {
    setTouchedFields({
      ...touchedFields,
      [field]: true
    });

    if (field === 'email' && email) {
      const validation = validateEmail(email);
      setFieldErrors({...fieldErrors, email: validation.errorMessage});
    }
  };

  const handleForgotPassword = async () => {
    // Mark email as touched
    setTouchedFields({
      email: true
    });

    // Validate email
    const emailValidation = validateEmail(email);
    
    if (emailValidation.errorMessage) {
      setFieldErrors({ email: emailValidation.errorMessage });
      return;
    }

    setIsLoading(true);
    try {
      // Frontend-only implementation for now
      setMessage("If an account with this email exists, password reset instructions have been sent. This is a frontend demo.");
      
      // When backend is ready, uncomment this code:
      /*
      const response = await fetch(`${config.apiUrl}/forgot-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email })
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Request failed");
      }
      */
    } catch (error) {
      setMessage("An error occurred");
      console.error("Forgot password error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-box">
      <div className="form-content">
        <h1>Forgot Password</h1>
        <p>Enter your email to receive a password reset link</p>

        <div className="field-wrapper">
          <input
            type="email"
            className={`input-field ${touchedFields.email && fieldErrors.email ? 'input-error' : ''}`}
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onBlur={() => handleBlur('email')}
            disabled={isLoading}
          />
          {touchedFields.email && fieldErrors.email && 
            <div className="error-message">{fieldErrors.email}</div>
          }
        </div>

        <button 
          className="connect-button" 
          onClick={handleForgotPassword}
          disabled={isLoading}
        >
          {isLoading ? "Sending..." : "Send Reset Link"}
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

export default ForgotPassword;