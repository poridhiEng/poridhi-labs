# **Prometheus HTTPS Setup for Secure Scraping**

To secure the metrics endpoints, we will enable HTTPS for both Prometheus and Node Exporter using TLS. This guide walks you through configuring TLS, setting up Prometheus to scrape Node Exporter over HTTPS, and verifying that the metrics are securely transmitted.

## **Task Overview**

1. Install and configure Prometheus and Node Exporter.
2. Generate a TLS certificate for Node Exporter.
3. Configure Node Exporter to use HTTPS.
4. Update Prometheus to use HTTPS for scraping Node Exporter.
5. Verify the HTTPS configuration in the Prometheus UI.

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