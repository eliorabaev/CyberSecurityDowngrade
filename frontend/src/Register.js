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
  const [touchedFields, setTouchedFields] = useState({
    username: false,
    email: false,
    password: false,
    confirmPassword: false
  });
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

  // Mark field as touched when user leaves it
  const handleBlur = (field) => {
    setTouchedFields({
      ...touchedFields,
      [field]: true
    });

    // Validate on blur
    if (field === 'username' && username) {
      const validation = validateUsername(username);
      setFieldErrors({...fieldErrors, username: validation.errorMessage});
    }
    else if (field === 'email' && email) {
      const validation = validateEmail(email);
      setFieldErrors({...fieldErrors, email: validation.errorMessage});
    }
    else if (field === 'password' && password) {
      const validation = validatePassword(password);
      setFieldErrors({...fieldErrors, password: validation.errorMessage});
    }
    else if (field === 'confirmPassword' && confirmPassword) {
      if (password) {
        const validation = validatePasswordMatch(password, confirmPassword);
        setFieldErrors({...fieldErrors, confirmPassword: validation.errorMessage});
      }
    }
  };

  const handleRegister = async () => {
    // Mark all fields as touched
    setTouchedFields({
      username: true,
      email: true,
      password: true,
      confirmPassword: true
    });

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
        setTouchedFields({
          username: false,
          email: false,
          password: false,
          confirmPassword: false
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

        <div className="field-wrapper">
          <input
            type="text"
            className={`input-field ${touchedFields.username && fieldErrors.username ? 'input-error' : ''}`}
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onBlur={() => handleBlur('username')}
            disabled={isLoading}
          />
          {touchedFields.username && fieldErrors.username && 
            <div className="error-message">{fieldErrors.username}</div>
          }
          <div className="requirements-text">
            Username must be 3-20 characters using only English letters and numbers.
          </div>
        </div>

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

        <div className="field-wrapper">
          <input
            type="password"
            className={`input-field ${touchedFields.password && fieldErrors.password ? 'input-error' : ''}`}
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onBlur={() => handleBlur('password')}
            disabled={isLoading}
          />
          {touchedFields.password && fieldErrors.password && 
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
            className={`input-field ${touchedFields.confirmPassword && fieldErrors.confirmPassword ? 'input-error' : ''}`}
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            onBlur={() => handleBlur('confirmPassword')}
            disabled={isLoading}
          />
          {touchedFields.confirmPassword && fieldErrors.confirmPassword && 
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