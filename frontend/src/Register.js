import React, { useState } from 'react';
import config from './config';
import { validateUsername, validatePassword, validatePasswordMatch } from './utils/validation';

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [fieldErrors, setFieldErrors] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

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

  // Handle changes to username (clear error when validation passes)
  const handleUsernameChange = (e) => {
    const value = e.target.value;
    setUsername(value);
    
    // If form was submitted and there was an error that's now fixed
    if (formSubmitted && fieldErrors.username) {
      const validation = validateUsername(value);
      if (validation.isValid) {
        setFieldErrors({...fieldErrors, username: ''});
      }
    }
  };

  // Handle changes to email (clear error when validation passes)
  const handleEmailChange = (e) => {
    const value = e.target.value;
    setEmail(value);
    
    // If form was submitted and there was an error that's now fixed
    if (formSubmitted && fieldErrors.email) {
      const validation = validateEmail(value);
      if (validation.isValid) {
        setFieldErrors({...fieldErrors, email: ''});
      }
    }
  };

  // Handle changes to password (clear error when validation passes)
  const handlePasswordChange = (e) => {
    const value = e.target.value;
    setPassword(value);
    
    // If form was submitted and there was an error that's now fixed
    if (formSubmitted && fieldErrors.password) {
      const validation = validatePassword(value);
      if (validation.isValid) {
        setFieldErrors({...fieldErrors, password: ''});
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
    if (formSubmitted && fieldErrors.confirmPassword && value === password) {
      setFieldErrors({...fieldErrors, confirmPassword: ''});
    }
  };

  const handleRegister = async () => {
    // Mark form as submitted to show validation errors
    setFormSubmitted(true);

    // Validate all fields before submission
    const usernameValidation = validateUsername(username);
    const emailValidation = validateEmail(email);
    const passwordValidation = validatePassword(password);
    const confirmValidation = validatePasswordMatch(password, confirmPassword);

    const errors = {
      username: usernameValidation.errorMessage,
      email: emailValidation.errorMessage,
      password: passwordValidation.errorMessage,
      confirmPassword: confirmValidation.errorMessage
    };

    setFieldErrors(errors);

    // Check if there are any validation errors
    if (Object.values(errors).some(error => error !== '')) {
      setMessage("Please fix the form errors before submitting");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${config.apiUrl}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, email, password })
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
        
        // Clear fields after successful registration
        setUsername("");
        setEmail("");
        setPassword("");
        setConfirmPassword("");
        setFieldErrors({
          username: '',
          email: '',
          password: '',
          confirmPassword: ''
        });
        setFormSubmitted(false);
        
        // Redirect to login page after 2 seconds
        setTimeout(() => {
          window.location.href = "/";
        }, 2000);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Registration failed");
      }
    } catch (error) {
      console.error("Registration error:", error);
      setMessage("Error connecting to server");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-box">
      <div className="form-content">
        <h1>Create Account</h1>
        <p>Please fill in your details</p>

        <div className="field-wrapper">
          <input
            type="text"
            className={`input-field ${formSubmitted && fieldErrors.username ? 'input-error' : ''}`}
            placeholder="Username"
            value={username}
            onChange={handleUsernameChange}
            disabled={isLoading}
          />
          {formSubmitted && fieldErrors.username && 
            <div className="error-message">{fieldErrors.username}</div>
          }
          <div className="requirements-text">
            Username must be 3-20 characters using only English letters and numbers.
          </div>
        </div>

        <div className="field-wrapper">
          <input
            type="email"
            className={`input-field ${formSubmitted && fieldErrors.email ? 'input-error' : ''}`}
            placeholder="Email"
            value={email}
            onChange={handleEmailChange}
            disabled={isLoading}
          />
          {formSubmitted && fieldErrors.email && 
            <div className="error-message">{fieldErrors.email}</div>
          }
        </div>

        <div className="field-wrapper">
          <input
            type="password"
            className={`input-field ${formSubmitted && fieldErrors.password ? 'input-error' : ''}`}
            placeholder="Password"
            value={password}
            onChange={handlePasswordChange}
            disabled={isLoading}
          />
          {formSubmitted && fieldErrors.password && 
            <div className="error-message">{fieldErrors.password}</div>
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
            placeholder="Confirm Password"
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
        {message && <p className='login-message'>{message}</p>}
      </div>
    </div>
  );
}

export default Register;