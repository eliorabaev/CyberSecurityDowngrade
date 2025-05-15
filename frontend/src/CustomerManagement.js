import React, { useState, useEffect } from 'react';
import config from './config';
import { useAuth } from './AuthContext';

function CustomerManagement({ successMessage }) {
  // State for form inputs
  const [customerName, setCustomerName] = useState("");
  const [internetPackage, setInternetPackage] = useState("");
  const [sector, setSector] = useState("");
  const [message, setMessage] = useState({ text: successMessage || "", type: successMessage ? "success" : "" });
  
  // State for storing customers
  const [customers, setCustomers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Use auth context
  const auth = useAuth();

  // Available internet packages and sectors for dropdowns from config
  const availablePackages = config.availablePackages;
  const availableSectors = config.availableSectors;

  // Fetch customers on component mount
  useEffect(() => {
    fetchCustomers();
  }, []);

  // Function to fetch customers from API
  const fetchCustomers = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${config.apiUrl}/customers`, {
        headers: {
          "Authorization": `Bearer ${auth.token}`  // Add token for authentication
        }
      });
      
      if (response.status === 401) {
        // Token expired or invalid
        handleAuthError();
        return;
      }
      
      if (response.ok) {
        const data = await response.json();
        // Use raw data without sanitization - XSS vulnerability
        setCustomers(data.customers || []);
      } else {
        // Expose backend error message directly
        const errorData = await response.json();
        setMessage({ text: errorData.detail || "Failed to load customers", type: "error" });
      }
    } catch (error) {
      // Expose detailed error information
      setMessage({ text: `Error: ${error.toString()}`, type: "error" });
      console.error("Error fetching customers:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle authentication errors
  const handleAuthError = () => {
    auth.logout();
    window.location.href = "/?message=Your session has expired. Please log in again.";
  };

  // Simple handlers without validation
  const handleCustomerNameChange = (e) => {
    setCustomerName(e.target.value);
  };

  const handleInternetPackageChange = (e) => {
    setInternetPackage(e.target.value);
  };

  const handleSectorChange = (e) => {
    setSector(e.target.value);
  };

  // Helper function to unsafely render HTML (vulnerable to XSS)
  const createUnsafeDisplay = (str) => {
    return <span dangerouslySetInnerHTML={{ __html: str }} />;
  };

  // Handle form submission
  const handleAddCustomer = async () => {
    try {
      // No input validation - vulnerable

      // Send customer data to API
      const response = await fetch(`${config.apiUrl}/customers`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${auth.token}` // Add token for authentication
        },
        body: JSON.stringify({
          name: customerName,
          internet_package: internetPackage,
          sector: sector
        })
      });

      if (response.status === 401) {
        // Token expired or invalid
        handleAuthError();
        return;
      }

      if (response.ok) {
        const data = await response.json();
        
        // Clear form and show success message
        setCustomerName("");
        setInternetPackage("");
        setSector("");
        setMessage({ text: data.message || "Customer added successfully!", type: "success" });
        
        // Refresh the customer list
        fetchCustomers();
      } else {
        // Expose backend error message directly
        const errorData = await response.json();
        setMessage({ text: errorData.detail || "Failed to add customer", type: "error" });
      }
    } catch (error) {
      // Expose detailed error information
      setMessage({ text: `Error: ${error.toString()}`, type: "error" });
      console.error("Error adding customer:", error);
    }
  };

  // Handle logout
  const handleLogout = () => {
    auth.logout();
    window.location.href = "/";
  };

  // Handle navigation to change password
  const handleChangePassword = () => {
    window.location.href = "/change-password";
  };

  // Clear success message after 3 seconds if it was passed in
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setMessage({ text: "", type: "" });
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Customer Management</h1>
        <div className="header-buttons">
          <span className="user-info">Logged in as: {auth.user?.username}</span>
          <button className="change-password-button" onClick={handleChangePassword}>
            Change Password
          </button>
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
      
      <div className="dashboard-message">
        {message.text && <p className={`message ${message.type}`} dangerouslySetInnerHTML={{ __html: message.text }}></p>}
      </div>
      
      <div className="dashboard-content">
        <div className="customer-form-container">
          <h2>Add New Customer</h2>
          
          <div className="form-row">
            <div className="form-group">
              <div className="field-wrapper">
                <input
                  type="text"
                  className="input-field"
                  placeholder="Customer Name"
                  value={customerName}
                  onChange={handleCustomerNameChange}
                />
              </div>
            </div>
            
            <div className="form-group">
              <div className="field-wrapper">
                <select
                  className="input-field"
                  value={internetPackage}
                  onChange={handleInternetPackageChange}
                >
                  <option value="">Select Internet Package</option>
                  {availablePackages.map((pkg, index) => (
                    <option key={index} value={pkg}>{pkg}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="form-group">
              <div className="field-wrapper">
                <select
                  className="input-field"
                  value={sector}
                  onChange={handleSectorChange}
                >
                  <option value="">Select Sector</option>
                  {availableSectors.map((sec, index) => (
                    <option key={index} value={sec}>{sec}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          
          <div className="button-container">
            <button className="connect-button" onClick={handleAddCustomer}>
              Add Customer
            </button>
          </div>
        </div>
        
        <div className="customer-table-container">
          <h2>Customer List</h2>
          
          {isLoading ? (
            <p className="loading">Loading customers...</p>
          ) : customers.length === 0 ? (
            <p className="no-data">No customers added yet</p>
          ) : (
            <table className="customer-table">
              <thead>
                <tr>
                  <th className="customer-name-col">Customer Name</th>
                  <th>Internet Package</th>
                  <th>Sector</th>
                  <th>Date Added</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.id}>
                    <td className="customer-name-cell">
                      <div className="truncate-text" title={customer.name}>
                        {createUnsafeDisplay(customer.name)}
                      </div>
                    </td>
                    <td>{createUnsafeDisplay(customer.internet_package)}</td>
                    <td>{createUnsafeDisplay(customer.sector)}</td>
                    <td>{customer.date_added}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default CustomerManagement;