
# Service Discovery and Relabeling in Prometheus

In this lab, we'll explore Service Discovery and Relabeling in Prometheus. Service Discovery allows Prometheus to automatically find and scrape metrics from dynamic environments without manual configuration, making it ideal for distributed systems or cloud-based applications.

Relabeling modifies the labels attached to the collected metrics, enabling you to rename, remove, or add labels to suit your monitoring needs. This helps in organizing and querying data efficiently.

We'll install Prometheus, configure it to scrape metrics from a dynamically updated source using a JSON file, and experiment with different relabeling strategies to adjust the labels for practical use.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/87e2faa5791ef084229170ef8156365973343c89/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2020/images/banner.svg)

## **Objective**
By the end of this lab, you will:
1. Install Prometheus and set it up to scrape metrics from a custom JSON file.
2. Learn the concept of service discovery and relabeling in Prometheus.
3. Understand how to manipulate labels during metric collection using relabeling.
4. Test different relabeling strategies with practical examples.

## **Service Discovery**

Service discovery in Prometheus automatically identifies and scrapes metrics from dynamic sources, such as cloud services or containerized environments. Relabeling is a key feature of service discovery, enabling the transformation of target labels (e.g., renaming or adding labels) to align with specific monitoring and querying requirements.

## **Prometheus Setup**

### **Install Prometheus**
Create a script (prometheus.sh) to install Prometheus:

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

### **Run the installation script:**
```bash
chmod +x prometheus.sh
./prometheus.sh
```


## **Configure Prometheus to Scrape Metrics**

### **Create the JSON File**

We will now create a JSON file with dummy nodes, each containing multiple labels. Here's an example JSON file (`/etc/prometheus/nodes.json`):

```json
[
  {
    "labels": {
      "instance": "node1",
      "job": "node_exporter",
      "region": "us-west",
      "environment": "production",
      "size": "large",
      "team": "backend",
      "type": "database"
    },
    "targets": ["localhost:9100"]
  },
  {
    "labels": {
      "instance": "node3",
      "job": "node_exporter",
      "region": "us-central",
      "environment": "development",
      "size": "small",
      "team": "devops",
      "type": "cache"
    },
    "targets": ["localhost:9300"]
  },
  {
    "labels": {
      "instance": "node4",
      "job": "node_exporter",
      "region": "eu-west",
      "environment": "production",
      "size": "large",
      "team": "data-science",
      "type": "analytics"
    },
    "targets": ["localhost:9400"]
  },
  {
    "labels": {
      "instance": "node5",
      "job": "node_exporter",
      "region": "ap-south",
      "environment": "staging",
      "size": "medium",
      "team": "security",
      "type": "firewall"
    },
    "targets": ["localhost:9500"]
  },
  {
    "labels": {
      "instance": "node6",
      "job": "node_exporter",
      "region": "us-west",
      "environment": "production",
      "size": "large",
      "team": "backend",
      "type": "database"
    },
    "targets": ["localhost:9600"]
  }
]
```

This JSON file contains dummy nodes with various labels. Each node has a list of targets, which are the IP addresses and ports of the nodes to be scraped.

### **Edit the Prometheus Configuration File**

1. **Edit the Prometheus configuration file:**
   ```bash
   sudo vim /etc/prometheus/prometheus.yml
   ```

2. **Add the following configuration to scrape the metrics from the JSON file:**

   ```yaml
   scrape_configs:
     - job_name: 'node_exporter'
       file_sd_configs:
         - files:
            - '/etc/prometheus/nodes.json'
   ```

3. **Validate and restart Prometheus:**
   ```bash
   promtool check config /etc/prometheus/prometheus.yml
   sudo systemctl restart prometheus
   ```

## **Access Prometheus**
Find the `eth0` IP address for the `Poridhi's VM` currently you are running by using the command:

```bash
ifconfig
```
![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2005/images/lab-59.png?raw=true)
    
Go to Poridhi's `LoadBalancer`and Create a `LoadBalancer` with the `eht0` IP and port `9090`.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2005/images/new-11.png?raw=true)

By using the Provided `URL` by `LoadBalancer`, you can access the Prometheus web interface from any browser.

Click on the **"Status"** tab in the top menu and select **"Service Discovery"** in Prometheus GUI. Here you will see `node_exporter`, when you click on it you will see the `Discovered Labels` and `Target Labels`.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2020/images/image.png?raw=true)

## **Relabeling In Prometheus**

Now, let's explore various relabeling options. Below are some common examples:

### **1. Renaming a Label (Extracting Part of the Instance Label)**

Open the `prometheus.yml` file:
```bash
sudo vim /etc/prometheus/prometheus.yml
```

Update the `prometheus.yml` file with the following configuration to extract part of the `instance` label using a regular expression and renames it to the `host` label. The `regex` ensures that only the first part of the `instance` (before any `/` or `-`) is captured and stored in the `host` label.

```yaml
scrape_configs:
  - job_name: 'node_exporter'
    file_sd_configs:
      - files:
        - '/etc/prometheus/nodes.json'
    relabel_configs:
      - source_labels: ['instance']
        target_label: 'host'
        regex: '([^/-]+).*'
```

Restart the Prometheus service to apply the changes:
```bash
sudo systemctl restart prometheus
```

Now in the Prometheus `Service Discovery` tab, you will see the `host` label instead of the `instance` label.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2020/images/1.png?raw=true)

### **2. Changing Label Value Based on a Condition**

Open the `prometheus.yml` file:
```bash
sudo vim /etc/prometheus/prometheus.yml
```

Update the `prometheus.yml` file with the following configuration to change the `type` label value based on a condition. The `regex` checks if the `type` label matches either `database` or `firewall`. If so, it sets the `metric_type` label to `critical`.

```yaml
scrape_configs:
  - job_name: 'node_exporter'
    file_sd_configs:
      - files:
        - '/etc/prometheus/nodes.json'
    relabel_configs:
      - source_labels: ['type']
        regex: 'database|firewall'
        target_label: 'metric_type'
        replacement: 'critical'
```

Restart the Prometheus service to apply the changes:

```bash
sudo systemctl restart prometheus
```

Now in the Prometheus `Service Discovery` tab, you will see the `metric_type` label instead of the `type` label.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2020/images/2.png?raw=true)

### **3. Combining Multiple Labels into a Single Label**

Open the `prometheus.yml` file:
```bash
sudo vim /etc/prometheus/prometheus.yml
```

Update the `prometheus.yml` file with the following configuration to combine the `region` and `environment` labels into a single label called `region_environment`.

```yaml
scrape_configs:
  - job_name: 'node_exporter'
    file_sd_configs:
      - files:
        - '/etc/prometheus/nodes.json'
    relabel_configs:
      - source_labels: ['region', 'environment']
        target_label: 'region_environment'
```

Restart the Prometheus service to apply the changes:

```bash
sudo systemctl restart prometheus
```

Now in the Prometheus `Service Discovery` tab, you will see the `region_environment` label instead of the `region` and `environment` labels.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2020/images/3.png?raw=true)

### **4. Modifying Label Values Based on Conditions (Environment Change)**

Open the `prometheus.yml` file:
```bash
sudo vim /etc/prometheus/prometheus.yml
```

Update the `prometheus.yml` file with the following configuration to modify the `region` label value based on the `environment` label. The `regex` checks if the `environment` label is set to `production`. If so, it sets the `region` label to `prod-region`.

```yaml
scrape_configs:
  - job_name: 'node_exporter'
    file_sd_configs:
      - files:
        - '/etc/prometheus/nodes.json'
    relabel_configs:
      - source_labels: ['environment']
        target_label: 'region'
        replacement: 'prod-region'
        regex: 'production'
```

Restart the Prometheus service to apply the changes:

```bash
sudo systemctl restart prometheus
```

Now in the Prometheus `Service Discovery` tab, you will see the `region` label instead of the `region` label.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2020/images/4.png?raw=true)

### **5. Keeping Only Specific Labels (Filter Out Non-Matching Labels)**

Open the `prometheus.yml` file:
```bash
sudo vim /etc/prometheus/prometheus.yml
```

Update the `prometheus.yml` file with the following configuration to keep only the targets where the `environment` label is set to `production`.

```yaml
scrape_configs:
  - job_name: 'node_exporter'
    file_sd_configs:
      - files:
        - '/etc/prometheus/nodes.json'
    relabel_configs:
      - source_labels: ['environment']
        target_label: 'environment'
        regex: 'production'
        action: 'keep'
```

Restart the Prometheus service to apply the changes:

```bash
sudo systemctl restart prometheus
```

Now in the Prometheus `Service Discovery` tab, you will see the targets where the `environment` label is set to `production`.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2020/images/5.png?raw=true)

### **6. Dropping Labels Based on a Condition**

Open the `prometheus.yml` file:
```bash
sudo vim /etc/prometheus/prometheus.yml
```

Update the `prometheus.yml` file with the following configuration to drop the targets where the `type` label is set to `cache`.

```yaml
scrape_configs:
  - job_name: 'node_exporter'
    file_sd_configs:
      - files:
        - '/etc/prometheus/nodes.json'
    relabel_configs:
      - source_labels: ['type']
        target_label: 'type'
        regex: 'cache'
        action: 'drop'
```

Restart the Prometheus service to apply the changes:

```bash
sudo systemctl restart prometheus
```

Now in the Prometheus `Service Discovery` tab, you will see the targets where the `type` label is not set to `cache`.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2020/images/6.png?raw=true)

### **Conclusion**

In this section, we have explored different relabeling strategies in Prometheus. Each of the examples demonstrates a common use case for altering labels to suit your monitoring and querying needs. By using relabeling, you can tailor the metrics collected by Prometheus to fit specific organizational requirements or to manage dynamic environments efficiently.