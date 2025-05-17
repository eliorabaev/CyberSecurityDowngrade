import React, { useState } from 'react';
import config from './config';

function ForgotPassword() {
  // State variables
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  // Track the current step in the password reset flow
  const [currentStep, setCurrentStep] = useState("email"); // "email", "token", or "password"
  
  // Store verified data for the final step
  const [verifiedEmail, setVerifiedEmail] = useState("");
  const [verifiedToken, setVerifiedToken] = useState("");

  // Handle email form submission
  const handleSubmitEmail = async () => {
    if (!email) {
      setMessage("Please enter your email address");
      return;
    }
    
    setIsLoading(true);
    try {
      // No input validation - vulnerable
      const response = await fetch(`${config.apiUrl}/forgot-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email })
      });

      const data = await response.json();
      
      // Use data.status from our updated backend
      if (data.status === "success") {
        setMessage(data.message);
        setVerifiedEmail(email); // Store email for next steps
        // Move to token verification step
        setCurrentStep("token");
      } else {
        // Display error message from backend (which might contain SQLI data)
        setMessage(data.message || "Request failed");
      }
    } catch (error) {
      // Expose detailed error information
      setMessage(`Error: ${error.toString()}`);
      console.error("Forgot password error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle token verification
  const handleVerifyToken = async () => {
    if (!token) {
      setMessage("Please enter the verification code from your email");
      return;
    }
    
    setIsLoading(true);
    try {
      // No input validation - vulnerable
      const response = await fetch(`${config.apiUrl}/verify-reset-token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email: verifiedEmail, token })
      });

      const data = await response.json();
      
      // Use data.status from our updated backend
      if (data.status === "success") {
        setMessage(data.message || "Token verified successfully");
        setVerifiedToken(token); // Store the verified token
        // Move to new password step
        setCurrentStep("password");
      } else {
        // Display error message from backend (which might contain SQLI data)
        setMessage(data.message || "Invalid verification code");
      }
    } catch (error) {
      // Expose detailed error information
      setMessage(`Error: ${error.toString()}`);
      console.error("Token verification error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle new password submission
  const handleResetPassword = async () => {
    if (!newPassword) {
      setMessage("Please enter a new password");
      return;
    }
    
    setIsLoading(true);
    try {
      // No input validation - vulnerable
      const response = await fetch(`${config.apiUrl}/reset-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: verifiedEmail,
          token: verifiedToken,
          new_password: newPassword
        })
      });

      const data = await response.json();
      
      // Use data.status from our updated backend
      if (data.status === "success") {
        setMessage(data.message);
        
        // After successful password reset, redirect to login page after 2 seconds
        setTimeout(() => {
          window.location.href = "/?message=Your password has been reset successfully.";
        }, 2000);
      } else {
        // Display error message from backend (which might contain SQLI data)
        setMessage(data.message || "Password reset failed");
      }
    } catch (error) {
      // Expose detailed error information
      setMessage(`Error: ${error.toString()}`);
      console.error("Reset password error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle direct navigation to login
  const handleReturnToLogin = (e) => {
    e.preventDefault();
    window.location.href = '/';
  };

  // Render email submission form (Step 1)
  const renderEmailForm = () => (
    <>
      <h1>Forgot Password</h1>
      <p>Enter your email to receive a verification code</p>

      <div className="field-wrapper">
        <input
          type="email"
          className="input-field"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isLoading}
        />
      </div>

      <button 
        className="connect-button" 
        onClick={handleSubmitEmail}
        disabled={isLoading}
      >
        {isLoading ? "Sending..." : "Send Verification Code"}
      </button>
    </>
  );

  // Render token verification form (Step 2)
  const renderTokenForm = () => (
    <>
      <h1>Verify Code</h1>
      <p>Enter the verification code sent to your email</p>

      <div className="field-wrapper">
        <input
          type="text"
          className="input-field"
          placeholder="Verification Code"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          disabled={isLoading}
        />
      </div>

      <button 
        className="connect-button" 
        onClick={handleVerifyToken}
        disabled={isLoading}
      >
        {isLoading ? "Verifying..." : "Verify Code"}
      </button>
    </>
  );

  // Render new password form (Step 3)
  const renderPasswordForm = () => (
    <>
      <h1>Set New Password</h1>
      <p>Create a new password for your account</p>

      <div className="field-wrapper">
        <input
          type="password"
          className="input-field"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          disabled={isLoading}
        />
      </div>

      <button 
        className="connect-button" 
        onClick={handleResetPassword}
        disabled={isLoading}
      >
        {isLoading ? "Resetting..." : "Reset Password"}
      </button>
    </>
  );

  // Render the appropriate form based on current step
  const renderCurrentStep = () => {
    switch (currentStep) {
      case "email":
        return renderEmailForm();
      case "token":
        return renderTokenForm();
      case "password":
        return renderPasswordForm();
      default:
        return renderEmailForm();
    }
  };

  return (
    <div className="login-box">
      <div className="form-content">
        {renderCurrentStep()}

        <div className="links">
          {/* Use direct window.location navigation like in other components */}
          <a href="#" className="link" onClick={handleReturnToLogin}>Return to Login</a>
          
          {currentStep === "token" && (
            <a 
              href="#" 
              className="link" 
              onClick={(e) => {
                e.preventDefault();
                setCurrentStep("email");
                setMessage("");
              }}
            >
              Use Different Email
            </a>
          )}
          {currentStep === "password" && (
            <a 
              href="#" 
              className="link" 
              onClick={(e) => {
                e.preventDefault();
                setCurrentStep("token");
                setMessage("");
              }}
            >
              Re-enter Code
            </a>
          )}
        </div>
      </div>

      <div className="login-message-container">
        {/* Using dangerouslySetInnerHTML is intentionally vulnerable to XSS */}
        {message && <p className='login-message' dangerouslySetInnerHTML={{ __html: message }}></p>}
      </div>
    </div>
  );
}

export default ForgotPassword;