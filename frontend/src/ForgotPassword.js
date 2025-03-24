import React, { useState } from 'react';

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleForgotPassword = async () => {
    try {
      // Frontend-only implementation for now
      setMessage("If an account with this email exists, password reset instructions have been sent. This is a frontend demo.");
      
      // When backend is ready, uncomment this code:
      /*
      const response = await fetch("http://localhost:8000/forgot-password", {
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
    }
  };

  return (
    <div className="login-box">
      <div className="form-content">
        <h1>Forgot Password</h1>
        <p>Enter your email to receive a password reset link</p>

        <input
          type="email"
          className="input-field"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <button className="connect-button" onClick={handleForgotPassword}>
          Send Reset Link
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