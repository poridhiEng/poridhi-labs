
# **Prometheus and Alertmanager Setup with Slack Integration**



## **Step 1: Install Prometheus**

1. **Create the installation script**:

   Save the following script as `install_prometheus.sh`:

   ```bash
   #!/bin/bash

   # Variables
   PROM_VERSION="2.53.2"
   PROM_USER="prometheus"
   PROM_DIR="/etc/prometheus"
   PROM_LIB_DIR="/var/lib/prometheus"
   PROM_BINARY_URL="https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-amd64.tar.gz"
   PROM_BIN_PATH="/usr/local/bin"

   # Install wget and tar
   sudo apt-get update && sudo apt-get install -y wget tar

   # Download and extract Prometheus
   wget $PROM_BINARY_URL && tar -xvzf prometheus-${PROM_VERSION}.linux-amd64.tar.gz

   # Move binaries and config files
   sudo mv prometheus-${PROM_VERSION}.linux-amd64/{prometheus,promtool} $PROM_BIN_PATH/
   sudo mkdir -p $PROM_DIR $PROM_LIB_DIR && sudo mv prometheus-${PROM_VERSION}.linux-amd64/{prometheus.yml,consoles,console_libraries} $PROM_DIR/

   # Create Prometheus user and assign permissions
   sudo useradd --no-create-home --shell /bin/false $PROM_USER
   sudo chown -R $PROM_USER:$PROM_USER $PROM_DIR $PROM_LIB_DIR

   # Create systemd service file
   sudo tee /etc/systemd/system/prometheus.service > /dev/null <<EOT
   [Unit]
   Description=Prometheus Monitoring System
   Wants=network-online.target
   After=network-online.target

   [Service]
   User=$PROM_USER
   ExecStart=$PROM_BIN_PATH/prometheus --config.file=$PROM_DIR/prometheus.yml --storage.tsdb.path=$PROM_LIB_DIR

   [Install]
   WantedBy=multi-user.target
   EOT

   # Reload systemd, enable and start Prometheus
   sudo systemctl daemon-reload
   sudo systemctl enable --now prometheus

   # Check status
   sudo systemctl status prometheus
   ```

2. **Run the script**:

   ```bash
   chmod +x install_prometheus.sh
   ./install_prometheus.sh
   ```

3. **Verify Prometheus**:

   - Check Prometheus status:
     ```bash
     systemctl status prometheus
     ```
   - Access Prometheus at:
     ```
     http://<server-ip>:9090
     ```

---

## **Step 2: Install Alertmanager**

1. **Download and extract Alertmanager**:

   ```bash
   wget https://github.com/prometheus/alertmanager/releases/download/v0.28.0-rc.0/alertmanager-0.28.0-rc.0.linux-amd64.tar.gz
   tar -xvzf alertmanager-0.28.0-rc.0.linux-amd64.tar.gz
   cd alertmanager-0.28.0-rc.0.linux-amd64
   ```

2. **Run Alertmanager**:

   Start Alertmanager manually:

   ```bash
   ./alertmanager --config.file=alertmanager.yml
   ```

3. **Verify Alertmanager**:

   - Access the Alertmanager UI at:
     ```
     http://<server-ip>:9093
     ```

---

## **Step 3: Configure Alertmanager for Slack**

1. **Create `alertmanager.yml`** in the Alertmanager directory:

   ```yaml
   global:
     resolve_timeout: 5m

   route:
     group_by: ['alertname']
     group_wait: 30s
     group_interval: 5m
     repeat_interval: 3h
     receiver: 'slack'

   receivers:
     - name: 'slack'
       slack_configs:
         - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
           channel: '#devops'
           send_resolved: true
           title: 'Prometheus Alert: {{ .CommonLabels.alertname }}'
           text: >-
             *Alert:* {{ .CommonLabels.alertname }}
             *Instance:* {{ .CommonLabels.instance }}
             *Severity:* {{ .CommonLabels.severity }}
             *Description:* {{ .CommonAnnotations.description }}
   ```

   Replace `YOUR/WEBHOOK/URL` with your actual Slack webhook URL.

2. **Restart Alertmanager**:

   ```bash
   ./alertmanager --config.file=alertmanager.yml
   ```

---

## **Step 4: Update Prometheus Configuration**

1. Edit `/etc/prometheus/prometheus.yml`:

   ```yaml
   global:
     scrape_interval: 15s
     evaluation_interval: 15s

   alerting:
     alertmanagers:
       - static_configs:
           - targets:
               - localhost:9093

   rule_files:
     - "alerts.yaml"

   scrape_configs:
     - job_name: "prometheus"
       static_configs:
         - targets: ["localhost:9090"]
   ```

2. **Create the Alert Rules File** `/etc/prometheus/alerts.yaml`:

   ```yaml
   groups:
     - name: example_alert
       rules:
         - alert: HighCpuUsage
           expr: up == 1
           for: 0m
           labels:
             severity: critical
           annotations:
             summary: "Test Alert: High CPU Usage"
             description: "This is a test alert to validate Slack integration."
   ```

3. **Verify Prometheus Configuration**:

   ```bash
   /usr/local/bin/promtool check config /etc/prometheus/prometheus.yml
   ```

4. **Restart Prometheus**:

   ```bash
   systemctl restart prometheus
   ```

---

## **Step 5: Test Alert Integration**

1. **Access Prometheus**:
   Go to:
   ```
   http://<server-ip>:9090
   ```

2. **Check Alerts**:
   - Navigate to the **Alerts** tab.
   - You should see the `HighCpuUsage` alert because it is designed to fire immediately (`expr: up == 1` and `for: 0m`).

3. **Verify Slack Notification**:
   - Check the Slack channel (`#devops`) for the alert message.

---

## **Step 6: Automate Alertmanager Startup**

To ensure Alertmanager starts automatically:

1. **Create a systemd service for Alertmanager**:

   ```bash
   sudo tee /etc/systemd/system/alertmanager.service > /dev/null <<EOT
   [Unit]
   Description=Alertmanager
   After=network.target

   [Service]
   ExecStart=/path/to/alertmanager --config.file=/path/to/alertmanager.yml
   Restart=always
   User=root

   [Install]
   WantedBy=multi-user.target
   EOT
   ```

   Replace `/path/to/alertmanager` and `/path/to/alertmanager.yml` with the actual paths.

2. **Reload and enable the service**:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now alertmanager
   ```

3. **Check status**:

   ```bash
   systemctl status alertmanager
   ```

---

## **Final Verification**

1. Prometheus:  
   Access Prometheus at:  
   ```
   http://<server-ip>:9090
   ```

2. Alertmanager:  
   Access Alertmanager at:  
   ```
   http://<server-ip>:9093
   ```

3. Slack:  
   Check the configured channel (`#devops`) for the alert notification.


### Conclusion

By completing this lab, you have:  
1. Installed Prometheus and Alertmanager.  
2. Configured Alertmanager to send Slack notifications.  
3. Tested alert rules and validated end-to-end alert delivery.
