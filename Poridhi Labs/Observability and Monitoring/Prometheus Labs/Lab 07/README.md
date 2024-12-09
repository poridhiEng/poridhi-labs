# **Prometheus HTTPS Setup for Secure Scraping**

Prometheus components don't have built-in security features like encryption or authentication. Without extra tools to secure them, all data between Prometheus and its components is sent as plain text, and anyone who knows the address can access them without restrictions. To secure the metrics endpoints, we will enable HTTPS for both Prometheus and Node Exporter using TLS. This guide walks you through configuring TLS, setting up Prometheus to scrape Node Exporter over HTTPS, and verifying that the metrics are securely transmitted.

## **Task Overview**

1. Install and configure Prometheus and Node Exporter.
2. Generate a TLS certificate for Node Exporter.
3. Configure Node Exporter to use HTTPS.
4. Update Prometheus to use HTTPS for scraping Node Exporter.
5. Verify the HTTPS configuration in the Prometheus UI.

## **Setup Prometheus and Node Exporter**

### **1. Setup Script for Prometheus**

Create a setup script to automate the installation of Prometheus.

#### **Create a Script as `prometheus.sh`**

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

#### **Run the Script:**

```bash
chmod +x prometheus.sh
sudo ./prometheus.sh
```

### **2. Setup Script for Node Exporter**

Similarly, create a setup script for Node Exporter.  

#### **Create a Script as `exporter.sh`**

```bash
#!/bin/bash

# Variables
NODE_EXPORTER_VERSION="1.8.2"
NODE_EXPORTER_USER="node_exporter"
NODE_EXPORTER_BINARY_URL="https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
NODE_EXPORTER_BIN_PATH="/usr/local/bin"

# Install wget and tar
sudo apt-get update && sudo apt-get install -y wget tar

# Download and extract Node Exporter
wget $NODE_EXPORTER_BINARY_URL && tar -xvzf node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz

# Move Node Exporter binary
sudo mv node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter $NODE_EXPORTER_BIN_PATH/

# Create a Node Exporter user (non-root)
sudo useradd --no-create-home --shell /bin/false $NODE_EXPORTER_USER

# Set ownership of the binary
sudo chown $NODE_EXPORTER_USER:$NODE_EXPORTER_USER $NODE_EXPORTER_BIN_PATH/node_exporter

# Create a systemd service file
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOT
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=$NODE_EXPORTER_USER
Group=$NODE_EXPORTER_USER
ExecStart=$NODE_EXPORTER_BIN_PATH/node_exporter

[Install]
WantedBy=multi-user.target
EOT

# Reload systemd, enable and start Node Exporter
sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter

# Check status
sudo systemctl status node_exporter
```

#### **Run the Script:**

```bash
chmod +x exporter.sh
sudo ./exporter.sh
```

### **3. Expose Prometheus UI and Node Exporter Metrics**

- Get the `IP` to create a load balancer:

  ```bash
  ifconfig
  ```

  Here copy the `IP` from `eth0` interface:

  ![alt text](./images/image.png)

- Create a load balancer from `Poridhi Lab` by providing the `IP` and `port: 9090`.

- Access the UI by opening the load balancer URL from browser. Go to *status > target*. We can see that prometheus has only one target and it is prometheus itself. Currently, it doesn't have `node_exporter` as its target to scrape. We have to configure the prometheus to scrape the `node_exporter`. 

  ![alt text](./images/image-1.png)

### **4. Configure Prometheus to Scrape Node Exporter**

Prometheus needs to be configured to scrape the metrics from Node Exporter.

- **Edit Prometheus Configuration:**

  ```bash
  sudo vi /etc/prometheus/prometheus.yml
  ```

- Add the following job under the `scrape_configs` section:

  ```yaml
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
  ```

  ![alt text](./images/image-2.png)

- **Restart Prometheus:**

  ```bash
  sudo systemctl daemon-reload
  sudo systemctl restart prometheus
  ```

- **Access/Reload the prometheus UI**

  Now you can see that the Prometheus is scraping the `node_exporter`. It may take a while to get the `up` state:

  ![alt text](./images/image-3.png)


## **1. Generate a TLS Certificate for Node Exporter**

Use the `openssl` command below to generate a self-signed certificate and private key for Node Exporter:

```bash
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
-keyout node_exporter.key -out node_exporter.crt \
-subj "/C=US/ST=California/L=Oakland/O=MyOrg/CN=localhost" \
-addext "subjectAltName = DNS:localhost"
```

This command generates a 2048-bit RSA key and a certificate valid for 365 days with `localhost` as the Common Name (CN).

### **2. Configure Node Exporter to Use HTTPS**

Move the generated certificate and key to a secure location and set appropriate permissions:

```bash
sudo mkdir -p /etc/node_exporter/ssl
sudo mv node_exporter.crt node_exporter.key /etc/node_exporter/ssl/
sudo chmod 600 /etc/node_exporter/ssl/*
sudo chown -R node_exporter:node_exporter /etc/node_exporter/ssl
```

Create a web configuration file for Node Exporter to enable TLS:

```bash
sudo vi /etc/node_exporter/ssl/web-config.yml
```

Add the following content:

```yaml
tls_server_config:
  cert_file: /etc/node_exporter/ssl/node_exporter.crt
  key_file: /etc/node_exporter/ssl/node_exporter.key
```

Update the Node Exporter systemd service to use the web configuration:

```bash
sudo vi /etc/systemd/system/node_exporter.service
```

Modify the `ExecStart` directive:

```ini
ExecStart=/usr/local/bin/node_exporter \
  --web.config.file=/etc/node_exporter/ssl/web-config.yml
```

Reload systemd and restart Node Exporter to apply the changes:

```bash
sudo systemctl daemon-reload
sudo systemctl restart node_exporter
sudo systemctl enable node_exporter
```

### **3. Configure Prometheus to Use HTTPS for Scraping Node Exporter**

To enable HTTPS for scraping, we need to copy the Node Exporter's certificate to the Prometheus server and update the Prometheus configuration.

#### **(a) Copy the Certificate**

Copy the certificate from Node Exporter to the Prometheus server:

```bash
sudo mkdir -p /etc/prometheus/ssl
sudo cp /etc/node_exporter/ssl/node_exporter.crt /etc/prometheus/ssl/
sudo chown -R prometheus:prometheus /etc/prometheus/ssl
sudo chmod 600 /etc/prometheus/ssl/node_exporter.crt
```

#### **(b) Update the Prometheus Configuration to Use HTTPS**

Edit the Prometheus configuration file:

```bash
sudo vi /etc/prometheus/prometheus.yml
```

Add the following scrape configuration for Node Exporter under `scrape_configs`:

```yaml
scrape_configs:
  - job_name: 'node_exporter'
    scheme: https
    static_configs:
      - targets: ['localhost:9100']
    tls_config:
      insecure_skip_verify: true
```

The `scheme: https` tells Prometheus to use HTTPS, and `insecure_skip_verify: true` is added because we are using a self-signed certificate.

#### **(c) Restart the Prometheus Service**

Restart Prometheus to apply the configuration changes:

```bash
sudo systemctl daemon-reload
sudo systemctl restart prometheus
sudo systemctl enable prometheus
```

### **4. Verify the HTTPS Configuration**

Access the Prometheus UI using the Prometheus button on the top bar. Navigate to **Status -> Targets** to view the status of the scraped targets.

- If the configuration is correct, both the Prometheus and Node Exporter targets should be listed as **UP**.
- If the Node Exporter target is **DOWN**, you may see an error code indicating the problem (e.g., `401 Unauthorized` or `TLS handshake failure`). Double-check the certificate and configuration settings.

## **Conclusion**

You've successfully configured Prometheus to scrape Node Exporter over HTTPS, ensuring secure communication. This setup enhances the monitoring environment's security by encrypting the data in transit. Now, both nodes should be displayed as being scraped over HTTPS in the Prometheus UI.