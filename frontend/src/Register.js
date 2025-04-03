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
  const [isLoading, setIsLoading] = useState(false);

  // Handle input validation on change
  const handleUsernameChange = (e) => {
    const value = e.target.value;
    setUsername(value);
    if (value) {
      const validation = validateUsername(value);
      setFieldErrors({...fieldErrors, username: validation.errorMessage});
    } else {
      setFieldErrors({...fieldErrors, username: ''});
    }
  };

  const handlePasswordChange = (e) => {
    const value = e.target.value;
    setPassword(value);
    if (value) {
      const validation = validatePassword(value);
      setFieldErrors({...fieldErrors, password: validation.errorMessage});
    } else {
      setFieldErrors({...fieldErrors, password: ''});
    }
  };

  const handleConfirmPasswordChange = (e) => {
    const value = e.target.value;
    setConfirmPassword(value);
    if (value) {
      const validation = validatePasswordMatch(password, value);
      setFieldErrors({...fieldErrors, confirmPassword: validation.errorMessage});
    } else {
      setFieldErrors({...fieldErrors, confirmPassword: ''});
    }
  };

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

  const handleEmailChange = (e) => {
    const value = e.target.value;
    setEmail(value);
    if (value) {
      const validation = validateEmail(value);
      setFieldErrors({...fieldErrors, email: validation.errorMessage});
    } else {
      setFieldErrors({...fieldErrors, email: ''});
    }
  };

  const handleRegister = async () => {
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

        <div className="input-container">
          <input
            type="text"
            className={`input-field ${fieldErrors.username ? 'input-error' : ''}`}
            placeholder="Username"
            value={username}
            onChange={handleUsernameChange}
            disabled={isLoading}
          />
          {fieldErrors.username && <div className="error-message">{fieldErrors.username}</div>}
        </div>

        <div className="input-container">
          <input
            type="email"
            className={`input-field ${fieldErrors.email ? 'input-error' : ''}`}
            placeholder="Email"
            value={email}
            onChange={handleEmailChange}
            disabled={isLoading}
          />
          {fieldErrors.email && <div className="error-message">{fieldErrors.email}</div>}
        </div>

        <div className="input-container">
          <input
            type="password"
            className={`input-field ${fieldErrors.password ? 'input-error' : ''}`}
            placeholder="Password"
            value={password}
            onChange={handlePasswordChange}
            disabled={isLoading}
          />
          {fieldErrors.password && <div className="error-message">{fieldErrors.password}</div>}
        </div>

        <div className="input-container">
          <input
            type="password"
            className={`input-field ${fieldErrors.confirmPassword ? 'input-error' : ''}`}
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={handleConfirmPasswordChange}
            disabled={isLoading}
          />
          {fieldErrors.confirmPassword && <div className="error-message">{fieldErrors.confirmPassword}</div>}
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