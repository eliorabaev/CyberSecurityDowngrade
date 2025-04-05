import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css';
import { AuthProvider } from './AuthContext';

// Identify the DOM element where the app will be mounted
const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);

// Render the App component wrapped in AuthProvider
root.render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);