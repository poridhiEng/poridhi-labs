# Health Monitoring of a Node.js Application using Bash Script

In modern application deployment, ensuring uptime and reliability is critical. This lab provides a comprehensive guide to running a Node.js application as a systemd service while implementing an automated health monitoring mechanism. By the end of this lab, you will have a resilient Node.js application that:

- Starts automatically on system boot.
- Restarts automatically in case of failure.
- Includes a health monitoring script that periodically checks service availability and restarts the application if necessary.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/b1c12b8951fc3c1315c213a3a32122b85e84d72c/Poridhi%20Labs/Systemd%20Labs/Lab%2002/images/health-check.svg)

## Task Overview

We will perform the following steps in this lab:
1. Set up a simple Node.js application.
2. Configure the application as a systemd service.
3. Implement an automated health check using a Bash script.
4. Schedule periodic health checks using cron.
5. Monitor the application's status and logs.
6. Introduce a failure scenario to verify that warnings are generated and the application is restarted.

## Setting Up the Node.js Application

### 1. Create the Application Directory

```bash
mkdir -p /root/code/node
cd /root/code/node
```

This creates a directory to host the Node.js application.

### 2. Create the Node.js Server

Create a file named `server.js` in the `node` directory and insert the following content:

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

Start the server manually:

```bash
node server.js
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Systemd%20Labs/Lab%2002/images/image.png)

Verify by accessing http://127.0.0.1:3311 in your browser or open a new terminal and run:

```bash
curl http://127.0.0.1:3311
```

You should see: `Node app is running!`.

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

**Key Parameters:**

- `ExecStart`: Path to your Node.js binary and application script (adjust as needed).
- `Restart=on-failure`: Automatically restarts the service if it crashes.


### 2. Enable and Start the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable node.service
sudo systemctl start node.service
sudo systemctl status node.service
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Systemd%20Labs/Lab%2002/images/image-1.png)

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

**Explanation:**

This Bash script is a health check and auto-recovery script for a Node.js service managed by `systemd`. Here's a quick breakdown of its functionality:

1. **Configuration**  
   - Sets the service URL (`SERVICE_URL`) to check if the Node.js service is running.  
   - Defines log files for general logs (`LOG_FILE`) and warnings (`WARNING_FILE`).  

2. **Logging Functions**  
   - `log_message()`: Logs general messages with timestamps.  
   - `log_warning()`: Logs warning messages with timestamps.  

3. **Service Check and Restart Functions**  
   - `check_systemd_service()`: Checks if `node.service` is active using `systemctl`.  
   - `restart_service()`: Attempts to restart `node.service`, logs success or failure.  

4. **Main Health Check (`main()`)**  
   - Ensures log files exist.  
   - Checks if `node.service` is running; if not, logs a warning and attempts a restart.  
   - Sends an HTTP request to `SERVICE_URL` and checks for a `200 OK` response.  
   - If the response is not `200`, logs a warning and attempts to restart the service.  

### **How the Script Works:**

1. **Service Status Check:** Uses `systemctl is-active` to verify if the service is running.
2. **HTTP Health Check:** Sends a `curl` request to `http://127.0.0.1:3311` and checks for a `200` response.
3. **Restart Logic:** Restarts the service if either check fails and logs the outcome.

### 2. Set Up Health Check Execution

1. Make the script executable:

```bash
sudo chmod +x /usr/local/bin/node_health_check.sh
```

2. Create log files and set permissions:

```bash
sudo touch /var/log/nodejs-health.log /var/log/nodejs-warnings.log
sudo chmod 644 /var/log/nodejs-health.log /var/log/nodejs-warnings.log
```

### 3. Schedule Health Checks with Cron

At first, install the cron package:

```bash
sudo apt update
sudo apt install cron -y
```

Now, edit the cron tab:

```bash
sudo crontab -e
```
**Add the following lines:**

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

## Start and Enable Cron Service

```bash
sudo systemctl start cron
sudo systemctl enable cron
```

Now, check the status of the cron service:

```bash
sudo systemctl status cron
```


## Monitoring and Maintenance

### 1. View Service Status

Check the status of the `node.service`:

```bash
sudo systemctl status node.service
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Systemd%20Labs/Lab%2002/images/image-5.png)

### 2. Check Logs

Open two new terminals for checking the logs and warnings:

```bash
tail -f /var/log/nodejs-health.log
tail -f /var/log/nodejs-warnings.log
```

Now, wait for few seconds and you will see the logs being populated in every 10 seconds by sending curl request to the server.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Systemd%20Labs/Lab%2002/images/image-2.png)

### 3. Run Manual Health Check

You can also run the health check manually and check the logs:

```bash
sudo /usr/local/bin/node_health_check.sh
```

## Introducing Intentional Failure

Now that the logs are being populated, let's introduce an intentional failure to verify that warnings are generated and the application is restarted.

1. **Stop the server manually:**
To verify that warnings are generated, stop the Node.js service manually:

    ```bash
    sudo systemctl stop node.service
    ```

2. **Wait 10 Seconds:** 
The cron job will detect the stopped service and attempt a restart.

3. **Check the warning logs:**
After a few seconds, check the warning logs.

    ```bash
    tail -f /var/log/nodejs-warnings.log
    ```
    
    The health check script should detect the failure and restart the service automatically.

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Systemd%20Labs/Lab%2002/images/image-3.png)

    Here, the nodejs service is crashed and the health check script is detecting the failure.

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Systemd%20Labs/Lab%2002/images/image-4.png)

    Here, we can see that the service is restarted automatically and the logs are being populated again.


## Conclusion

In this lab, we successfully implemented a robust health monitoring system for a Node.js application using systemd and a Bash script. We configured the application as a systemd service, set up an automated health check script, and scheduled periodic monitoring with cron. The health check mechanism continuously verifies the service’s availability and ensures automatic recovery in case of failure. By integrating logging, proactive monitoring, and self-healing capabilities, we have enhanced the application's reliability and resilience.

