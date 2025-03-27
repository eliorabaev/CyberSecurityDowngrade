// Replace the Login function in App.js with this updated version

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = async () => {
    try {
      // Form validation
      if (!username || !password) {
        setMessage("Please enter both username and password");
        return;
      }
      
      // Send login request to backend
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
        setIsLoggedIn(true);
      } else {
        const errorData = await response.json();
        setMessage(errorData.detail || "Login failed");
      }
    } catch (error) {
      setMessage("Error connecting to server");
      console.error("Login error:", error);
    }
  };

  // If logged in, redirect to CustomerManagement
  if (isLoggedIn) {
    return <CustomerManagement />;
  }

  return (
    <div className="login-box">
      <div className="form-content">
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
      </div>

      <div className="login-message-container">
        {message && <p className='login-message'>{message}</p>}
      </div>
    </div>
  );
}