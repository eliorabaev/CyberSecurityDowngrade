import React, { useState, useEffect } from 'react';

function CustomerManagement({ successMessage }) {
  // State for form inputs
  const [customerName, setCustomerName] = useState("");
  const [internetPackage, setInternetPackage] = useState("");
  const [sector, setSector] = useState("");
  const [message, setMessage] = useState({ text: successMessage || "", type: successMessage ? "success" : "" });
  
  // State for storing customers
  const [customers, setCustomers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Available internet packages and sectors for dropdowns
  const availablePackages = ["Basic (10 Mbps)", "Standard (50 Mbps)", "Premium (100 Mbps)", "Enterprise (500 Mbps)"];
  const availableSectors = ["North", "South", "East", "West", "Central"];

  // Fetch customers on component mount
  useEffect(() => {
    fetchCustomers();
  }, []);

  // Function to fetch customers from API
  const fetchCustomers = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/customers");
      if (response.ok) {
        const data = await response.json();
        setCustomers(data.customers || []);
      } else {
        setMessage({ text: "Failed to load customers", type: "error" });
      }
    } catch (error) {
      console.error("Error fetching customers:", error);
      setMessage({ text: "Error connecting to server", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle form submission
  const handleAddCustomer = async () => {
    // Simple validation
    if (!customerName || !internetPackage || !sector) {
      setMessage({ text: "Please fill in all fields", type: "error" });
      return;
    }

    try {
      // Send customer data to API
      const response = await fetch("http://localhost:8000/customers", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name: customerName,
          internet_package: internetPackage,
          sector: sector
        })
      });

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
        const errorData = await response.json();
        setMessage({ text: errorData.detail || "Failed to add customer", type: "error" });
      }
    } catch (error) {
      console.error("Error adding customer:", error);
      setMessage({ text: "Error connecting to server", type: "error" });
    }
  };

  // Handle logout
  const handleLogout = () => {
    // In a real app, you would clear authentication tokens here
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
          <button className="change-password-button" onClick={handleChangePassword}>
            Change Password
          </button>
          <button className="logout-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
      
      <div className="dashboard-message">
        {message.text && <p className={`message ${message.type}`}>{message.text}</p>}
      </div>
      
      <div className="dashboard-content">
        <div className="customer-form-container">
          <h2>Add New Customer</h2>
          
          <div className="form-row">
            <div className="form-group">
              <input
                type="text"
                className="input-field"
                placeholder="Customer Name"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
              />
            </div>
            
            <div className="form-group">
              <select
                className="input-field"
                value={internetPackage}
                onChange={(e) => setInternetPackage(e.target.value)}
              >
                <option value="">Select Internet Package</option>
                {availablePackages.map((pkg, index) => (
                  <option key={index} value={pkg}>{pkg}</option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <select
                className="input-field"
                value={sector}
                onChange={(e) => setSector(e.target.value)}
              >
                <option value="">Select Sector</option>
                {availableSectors.map((sec, index) => (
                  <option key={index} value={sec}>{sec}</option>
                ))}
              </select>
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
                        {customer.name}
                      </div>
                    </td>
                    <td>{customer.internet_package}</td>
                    <td>{customer.sector}</td>
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