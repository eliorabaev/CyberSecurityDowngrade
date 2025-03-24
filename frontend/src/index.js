import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css';

// Identify the DOM element where the app will be mounted
const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);

// Render the <App /> component
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);