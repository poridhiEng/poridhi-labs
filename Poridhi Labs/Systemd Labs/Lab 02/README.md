# Health Monitoring of Node.js Application using Bash Script

This lab provides a step-by-step approach to running a Node.js application as a systemd service while implementing automated health monitoring. The setup ensures the following:
- The application starts automatically on system boot.
- It restarts automatically upon failure.
- It includes a health monitoring mechanism to check service availability and restart if necessary.

By following this documentation, you will be able to deploy a resilient Node.js application on a Linux system.

## Setting Up the Node.js Application

### 1. Create the Application Directory
```bash
mkdir -p /root/code/node
cd /root/code/node
```

### 2. Create the Node.js Server
Create a file named `server.js` and insert the following content:

```javascript
const http = require('http');
const hostname = '127.0.0.1';
const port = 3311;

http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Node app is running!');
}).listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});
```

### 3. Test the Server
```bash
node server.js
```
Verify by accessing http://127.0.0.1:3311 in your browser or using:
```bash
curl http://127.0.0.1:3311
```

## Configuring systemd Service

### 1. Create a systemd Service File
Create a new service file at `/etc/systemd/system/node.service`:

```ini
[Unit]
Description=Start Node.js App
After=network.target

[Service]
ExecStart=/usr/local/nvm/versions/node/v18.16.1/bin/node /root/code/node/server.js
KillMode=control-group
WorkingDirectory=/root/code/node
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

> **Note:** Adjust `ExecStart` path to match your Node.js installation.

### 2. Enable and Start the Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable node.service
sudo systemctl start node.service
sudo systemctl status node.service
```

## Implementing Health Monitoring

### 1. Create a Health Check Script
Create `/usr/local/bin/node_health_check.sh`:

```bash
#!/bin/bash

# Configuration
SERVICE_URL="http://127.0.0.1:3311"
LOG_FILE="/var/log/nodejs-health.log"
WARNING_FILE="/var/log/nodejs-warnings.log"

# Function to log messages
log_message() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" >> "$LOG_FILE"
}

# Function to log warnings
log_warning() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] WARNING: $1" >> "$WARNING_FILE"
}

# Function to check if systemd service is running
check_systemd_service() {
    systemctl is-active --quiet node.service
    return $?
}

# Function to restart the service
restart_service() {
    log_message "Attempting to restart node.service..."
    sudo systemctl restart node.service
    sleep 5  # Wait for service to restart
    
    if check_systemd_service; then
        log_message "Service successfully restarted"
        return 0
    else
        log_warning "Failed to restart Node.js service - System remains down"
        return 1
    fi
}

# Main health check
main() {
    # Create log files if they don't exist
    touch "$LOG_FILE"
    touch "$WARNING_FILE"
    
    # Check if service is running
    if ! check_systemd_service; then
        log_warning "Node.js service is not running - System crashed"
        restart_service
        exit 1
    fi

    # Make HTTP request to check service
    response=$(curl -s -w "%{http_code}" "$SERVICE_URL" -o /dev/null)
    
    if [ "$response" = "200" ]; then
        log_message "Health check passed - Service is responding normally"
    else
        log_warning "Service is not responding properly (HTTP $response) - System may be crashed"
        restart_service
    fi
}

# Run main function
main
```

### 2. Set Up Health Check Execution
```bash
sudo chmod +x /usr/local/bin/node_health_check.sh
sudo touch /var/log/nodejs-health.log /var/log/nodejs-warnings.log
sudo chmod 644 /var/log/nodejs-health.log /var/log/nodejs-warnings.log
```

### 3. Schedule Health Checks with Cron
```bash
sudo crontab -e
```
Add the following line:
```
* * * * * /usr/local/bin/node_health_check.sh
* * * * * sleep 10 && /usr/local/bin/node_health_check.sh
* * * * * sleep 20 && /usr/local/bin/node_health_check.sh
* * * * * sleep 30 && /usr/local/bin/node_health_check.sh
* * * * * sleep 40 && /usr/local/bin/node_health_check.sh
* * * * * sleep 50 && /usr/local/bin/node_health_check.sh
```

#### Explanation

- The script runs once per minute (`* * * * *`).
- `sleep X &&` ensures it runs at **10, 20, 30, 40, and 50 seconds** after each minute starts.
- This effectively runs the script every **10 seconds**.

## Monitoring and Maintenance

### 1. View Service Status
```bash
sudo systemctl status node.service
```

### 2. Check Logs
```bash
tail -f /var/log/nodejs-health.log
tail -f /var/log/nodejs-warnings.log
```

### 3. Run Manual Health Check
```bash
sudo /usr/local/bin/node_health_check.sh
```

## Conclusion

By following this guide, you have successfully configured a Node.js application as a systemd service with automated health monitoring. Your application is now more robust and resilient to failures. Happy coding!

