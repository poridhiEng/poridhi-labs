# Payment Status Application

This is a simple web-based payment status management system that allows viewing payment status on a dashboard and updating it through an admin portal. The system uses HTML, CSS, and JavaScript with local storage for data persistence.

## Objective
To create a lightweight payment status tracking system with:
- Public dashboard for viewing payment status
- Admin portal for status management
- Persistent status storage
- Responsive design

## Project Structure
```
project/
├── admin-portal/
│   └── index.html      # Admin interface
├── index.html          # Main dashboard
├── styles.css          # Shared styles
├── admin.js           # Admin functionality
└── dashboard.js       # Dashboard functionality
```

## Setup and Installation

### Using Python HTTP Server
1. Clone or download the project files
2. Open terminal in the project directory
3. Run the Python HTTP server:
```bash
# For Python 3
python3 -m http.server 8000

# Access the application
Dashboard: http://localhost:8000
Admin Portal: http://localhost:8000/admin-portal/
```

## Code Documentation

### 1. Main Dashboard (index.html)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FakeEcommerce - Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>FakeEcommerce</h1>
        <h2>Order Summary</h2>
        <div class="payment-status">
            <p><strong>Order ID:</strong> <span>#12345</span></p>
            <p>
                <strong>Payment Status:</strong> 
                <span id="paymentStatusBadge" class="status-badge"></span>
            </p>
            <p><strong>Amount:</strong> <span>$99.99</span></p>
            <p><strong>Date:</strong> <span>January 13, 2025</span></p>
        </div>
    </div>
    <script src="dashboard.js"></script>
</body>
</html>
```

### 2. Admin Portal (admin-portal/index.html)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FakeEcommerce - Admin Panel</title>
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
    <div class="container">
        <h1>Admin Panel</h1>
        <h2>Manage Payment Status</h2>
        <div class="admin-controls">
            <p><strong>Order ID:</strong> <span>#12345</span></p>
            <p><strong>Current Status:</strong> 
                <span id="currentStatusBadge" class="status-badge"></span>
            </p>
            <div class="select-wrapper">
                <select id="paymentStatusSelect">
                    <option value="Pending">Pending</option>
                    <option value="Processing">Processing</option>
                    <option value="Paid">Paid</option>
                    <option value="Failed">Failed</option>
                </select>
            </div>
            <button onclick="updatePaymentStatus()" class="primary-button">Update Status</button>
        </div>
    </div>
    <script src="../admin.js"></script>
</body>
</html>
```

### 3. Admin JavaScript (admin.js)
```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const statusSelect = document.getElementById('paymentStatusSelect');
    const currentStatusBadge = document.getElementById('currentStatusBadge');
    
    // Get the saved payment status from localStorage
    const savedStatus = localStorage.getItem('paymentStatus') || 'Pending';
    
    // Update the select value and current status badge
    statusSelect.value = savedStatus;
    currentStatusBadge.textContent = savedStatus;
    currentStatusBadge.className = `status-badge status-${savedStatus.toLowerCase()}`;
});

function updatePaymentStatus() {
    // Get the selected status
    const statusSelect = document.getElementById('paymentStatusSelect');
    const currentStatusBadge = document.getElementById('currentStatusBadge');
    const newStatus = statusSelect.value;
    
    // Save to localStorage
    localStorage.setItem('paymentStatus', newStatus);
    
    // Update the current status badge
    currentStatusBadge.textContent = newStatus;
    currentStatusBadge.className = `status-badge status-${newStatus.toLowerCase()}`;
    
    // Show success message
    alert('Payment status updated successfully!');
}
```

### 4. Dashboard JavaScript (dashboard.js)
```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Get the payment status badge element
    const statusBadge = document.getElementById('paymentStatusBadge');
    
    // Get the saved payment status from localStorage
    const savedStatus = localStorage.getItem('paymentStatus') || 'Pending';
    
    // Update the badge text and classes
    statusBadge.textContent = savedStatus;
    statusBadge.className = `status-badge status-${savedStatus.toLowerCase()}`;
});
```

### 5. Styles (styles.css)
Key styling features:
```css
/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
    margin: 0;
    padding: 20px;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #2d3748;
    line-height: 1.5;
}

.container {
    width: 480px;
    background: white;
    padding: 32px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

h1 {
    color: #1a202c;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 24px;
    text-align: center;
}

h2 {
    color: #4a5568;
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e2e8f0;
}

.payment-status, .admin-controls {
    background: #f8fafc;
    padding: 24px;
    border-radius: 12px;
    margin: 20px 0;
}

.payment-status p, .admin-controls p {
    font-size: 15px;
    margin: 12px 0;
    color: #4a5568;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

strong {
    color: #2d3748;
    font-weight: 500;
}

.select-wrapper {
    position: relative;
    margin: 20px 0;
}

.select-wrapper::after {
    content: '▼';
    font-size: 12px;
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #4a5568;
    pointer-events: none;
}

select {
    width: 100%;
    padding: 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 15px;
    color: #4a5568;
    background-color: white;
    cursor: pointer;
    appearance: none;
    transition: all 0.2s ease;
}

select:hover {
    border-color: #cbd5e0;
}

select:focus {
    outline: none;
    border-color: #4f46e5;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

button {
    width: 100%;
    padding: 12px 20px;
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 15px;
    font-weight: 500;
    transition: all 0.2s ease;
    margin-top: 16px;
}

button:hover {
    background: #4338ca;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
}

button:active {
    transform: translateY(0px);
}

button.secondary {
    background: #f8fafc;
    color: #4a5568;
    border: 1px solid #e2e8f0;
}

button.secondary:hover {
    background: #f1f5f9;
    color: #1a202c;
}

/* Status badges */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 14px;
    font-weight: 500;
}

.status-pending {
    background-color: #fef3c7;
    color: #92400e;
}

.status-processing {
    background-color: #e0f2fe;
    color: #075985;
}

.status-paid {
    background-color: #dcfce7;
    color: #166534;
}

.status-failed {
    background-color: #fee2e2;
    color: #991b1b;
}

/* Responsive adjustments */
@media (max-width: 520px) {
    body {
        padding: 16px;
    }
    
    .container {
        width: 100%;
        padding: 24px;
    }
    
    .payment-status, .admin-controls {
        padding: 20px;
    }
}
```

## Dockerfile

```dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "http.server", "8000"]
```
