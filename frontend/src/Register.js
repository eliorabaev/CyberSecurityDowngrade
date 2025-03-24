import React, { useState } from 'react';

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleRegister = async () => {
    // Simple validation
    if (password !== confirmPassword) {
      setMessage("Passwords do not match");
      return;
    }

    try {
      // Frontend-only implementation for now
      setMessage("Registration successful! This is a frontend demo.");
      
      // When backend is ready, uncomment this code:
      /*
      const response = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, email, password })
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Registration failed");
      }
      */
    } catch (error) {
      setMessage("An error occurred");
      console.error("Registration error:", error);
    }
  };

  return (
    <div className="login-box">
      <div className="form-content">
        <h1>Create Account</h1>
        <p>Please fill in your details</p>

        <input
          type="text"
          className="input-field"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="email"
          className="input-field"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          className="input-field"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          type="password"
          className="input-field"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />

        <button className="connect-button" onClick={handleRegister}>
          Register
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