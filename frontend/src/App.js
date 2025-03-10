import React, { useState } from 'react';

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async () => {
    try {
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.message);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Login failed");
      }
    } catch (error) {
      setMessage("An error occurred");
      console.error("Login error:", error);
    }
  };

  return (
    <div className="login-box">
      <h1>Welcome Admin</h1>
      <p>Sign in to continue</p>

      <input
        type="text"
        className="input-field"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        className="input-field"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button className="connect-button" onClick={handleLogin}>
        Connect
      </button>

      <div className="links">
        <a href="/forgot-password" className="link">Forgot Password?</a>
        <a href="/register" className="link">Register</a>
      </div>

      {message && <p className='login-message'>{message}</p>}
    </div>
  );
}

export default App;
