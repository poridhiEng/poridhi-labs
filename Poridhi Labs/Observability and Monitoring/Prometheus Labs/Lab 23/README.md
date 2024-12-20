# **Installation of Alertmanager**

Alertmanager is a component of the Prometheus ecosystem responsible for handling alerts generated by Prometheus. It manages alerts by grouping, deduplicating, and routing them to various receivers such as email, Slack, or PagerDuty. 

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c518615a372f39dfff6c0dae756e7a1c7a01901d/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2023/images/logo1.svg)


**Why do we need Alertmanager?**  
- Prometheus triggers alerts but cannot send notifications directly.  
- Alertmanager ensures alerts are efficiently managed and delivered to the right channels such as `Email`, `Slack`, or `PagerDuty` 
- It allows features like **silencing**, **inhibition**, and **routing** to reduce alert fatigue.


## **Objective**  
In this lab, you will:  
1. Understand the architecture of Alertmanager.  
2. Install Alertmanager using two methods:  
   - **Method 1**: Install with systemd for standalone setups.  
   - **Method 2**: Install using Docker for containerized environments.  

## **Alertmanager Architecture**

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c518615a372f39dfff6c0dae756e7a1c7a01901d/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2023/images/logo2.svg)

The architecture of Alertmanager can be broken down into the following components:

- **Alerts**  
   Prometheus generates alerts based on monitoring data and sends them to Alertmanager via its API. Alerts include key details like `alertname`, `severity`, and `instance`.

- **Dispatching**  
   Alerts are grouped based on common labels (e.g., `alertname`, `instance`) as defined in the `route` section. Grouping reduces alert noise by consolidating similar alerts into a single notification.

- **Inhibition**  
   Prevents lower-priority alerts (e.g., `warning`) from triggering when higher-priority alerts (e.g., `critical`) for the same issue are active. This focuses attention on critical issues.

- **Silencing**  
   Temporarily mutes alerts during known issues or maintenance windows. Silences can be applied manually via the Alertmanager UI or API.

- **Routing**  
   Routes alerts to specific receivers (e.g., Slack, email, PagerDuty) based on conditions like `severity` or `alertname`. Routing ensures the right team or channel gets notified.

- **Receivers**  
   Final destinations where alerts are delivered, such as:  
   - **Slack**: Alerts are posted in a channel using a webhook.  
   - **Email**: Notifications are sent via an SMTP server.

## **Install Alertmanager**

### **Method 1: Install Alertmanager with systemd**

1. **Download Alertmanager**:
   ```bash
   wget https://github.com/prometheus/alertmanager/releases/download/v0.28.0-rc.0/alertmanager-0.28.0-rc.0.linux-amd64.tar.gz
   ```

2. **Extract the archive**:
   ```bash
   tar -xvzf alertmanager-0.28.0-rc.0.linux-amd64.tar.gz
   cd alertmanager-0.28.0-rc.0.linux-amd64
   ```

3. **Move binaries to `/usr/local/bin`**:
   ```bash
   sudo mv alertmanager amtool /usr/local/bin/
   ```

4. **Create directories for Alertmanager**:
   ```bash
   sudo mkdir -p /etc/alertmanager /var/lib/alertmanager
   ```

5. **Create `alertmanager.yml` configuration file**:  
   ```bash
   sudo vim /etc/alertmanager/alertmanager.yml
   ```

   **Demo Configuration**:  
   ```yaml
   route:
     group_by: ['alertname']
     group_wait: 30s
     group_interval: 5m
     repeat_interval: 1h
     receiver: 'web.hook'

   receivers:
     - name: 'web.hook'
       webhook_configs:
         - url: 'http://127.0.0.1:5001/'

   inhibit_rules:
     - source_match:
         severity: 'critical'
       target_match:
         severity: 'warning'
       equal: ['alertname', 'dev', 'instance']
   ```

    Here we are using demo `url` for testing purpose in `webhook_configs`. Later on we will discuss it in lot more details.

6. **Create a systemd service file**:
   ```bash
   sudo vim /etc/systemd/system/alertmanager.service
   ```

   Add the following content:
   ```ini
   [Unit]
   Description=Alertmanager Service
   After=network.target

   [Service]
   ExecStart=/usr/local/bin/alertmanager \
     --config.file=/etc/alertmanager/alertmanager.yml \
     --storage.path=/var/lib/alertmanager
   Restart=always
   User=root
   Group=root

   [Install]
   WantedBy=multi-user.target
   ```

7. **Reload systemd and start Alertmanager**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now alertmanager
   ```

8. **Check Alertmanager status**:
   ```bash
   sudo systemctl status alertmanager
   ```

9. **Verify Alertmanager UI:**
   - Find the `eth0` IP address for the `Poridhi's VM` currently you are running by using the command:

    ```bash
    ifconfig
    ```

    ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2005/images/lab-59.png?raw=true)
    
   - Go to Poridhi's `LoadBalancer`and Create a `LoadBalancer` with the `eht0` IP and port `9093`.

   - By using the Provided `URL` by `LoadBalancer`, you can access the Alertmanager web interface from any browser.

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c518615a372f39dfff6c0dae756e7a1c7a01901d/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2023/images/image.png)

### **Method 2: Install Alertmanager with Docker**

1. **Pull the Alertmanager Docker image**:
   ```bash
   docker pull prom/alertmanager:v0.28.0-rc.0
   ```

2. **Create a directory for Alertmanager configuration**:  
   Run the following commands to create the directory:

   ```bash
   mkdir -p ~/alertmanager
   ```

3. **Create the configuration file**:  
   Open the `alertmanager.yml` file for editing:

   ```bash
   vim ~/alertmanager/alertmanager.yml
   ```

4. **Add the following configuration**:  
   This configuration uses a webhook for testing purposes.

   ```yaml
   route:
     group_by: ['alertname']
     group_wait: 30s
     group_interval: 5m
     repeat_interval: 1h
     receiver: 'web.hook'

   receivers:
     - name: 'web.hook'
       webhook_configs:
         - url: 'http://127.0.0.1:5001/'

   inhibit_rules:
     - source_match:
         severity: 'critical'
       target_match:
         severity: 'warning'
       equal: ['alertname', 'dev', 'instance']
   ```

5. **Run Alertmanager Container**:
   ```bash
   docker run -d \
     --name=alertmanager \
     -p 9093:9093 \
     -v ~/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
     prom/alertmanager:v0.28.0-rc.0
   ```

   Check the container state in docker

   ```bash
   docker ps
   ```

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c518615a372f39dfff6c0dae756e7a1c7a01901d/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2023/images/1.jpg)

6. **Verify Alertmanager UI:**
   - Find the `eth0` IP address for the `Poridhi's VM` currently you are running by using the command:

     ```bash
     ifconfig
     ```
    
    - Go to Poridhi's `LoadBalancer`and Create a `LoadBalancer` with the `eht0` IP and port `9093`.

   - By using the Provided `URL` by `LoadBalancer`, you can access the Alertmanager web interface from any browser.

7. **Check Docker logs** (optional for debugging):
   ```bash
   docker logs alertmanager
   ```

## **Conclusion**

In this lab, you:  
1. Learned about **Alertmanager** and its architecture.  
2. Installed Alertmanager using **systemd** and **Docker**.  
