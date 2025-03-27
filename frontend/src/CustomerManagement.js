import React, { useState, useEffect } from 'react';

function CustomerManagement() {
  // State for form inputs
  const [customerName, setCustomerName] = useState("");
  const [internetPackage, setInternetPackage] = useState("");
  const [sector, setSector] = useState("");
  const [message, setMessage] = useState({ text: "", type: "" });
  
  // State for storing customers
  const [customers, setCustomers] = useState([]);

  // Available internet packages and sectors for dropdowns
  const availablePackages = ["Basic (10 Mbps)", "Standard (50 Mbps)", "Premium (100 Mbps)", "Enterprise (500 Mbps)"];
  const availableSectors = ["North", "South", "East", "West", "Central"];

  // Handle form submission
  const handleAddCustomer = () => {
    // Simple validation
    if (!customerName || !internetPackage || !sector) {
      setMessage({ text: "Please fill in all fields", type: "error" });
      return;
    }

    // Create new customer object
    const newCustomer = {
      id: Date.now(), // simple unique ID
      name: customerName,
      package: internetPackage,
      sector: sector,
      dateAdded: new Date().toLocaleDateString()
    };

    // Add to customers array
    setCustomers([...customers, newCustomer]);
    
    // Clear form and show success message
    setCustomerName("");
    setInternetPackage("");
    setSector("");
    setMessage({ text: "Customer added successfully!", type: "success" });

    // Clear message after 3 seconds
    setTimeout(() => {
      setMessage("");
    }, 3000);
  };

  // Handle logout
  const handleLogout = () => {
    // In a real app, you would clear authentication tokens here
    window.location.href = "/";
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Customer Management</h1>
        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
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
          
          {customers.length === 0 ? (
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
                    <td>{customer.package}</td>
                    <td>{customer.sector}</td>
                    <td>{customer.dateAdded}</td>
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