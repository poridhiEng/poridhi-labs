# **Recording Rules in Prometheus**

Recording rules in Prometheus enable the periodic evaluation of PromQL expressions and store the resulting values in the database. This enhances the performance of queries by avoiding the need to evaluate complex expressions on-the-fly, especially when using visualization tools like Grafana.

The architecture can be illustrated as follows:

![Recording Rule Architecture](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/record-rule.svg?raw=true)


image.png?raw=true


**Explanation of the Architecture:**
1. **Data Source:** Metrics are collected from data sources such as servers, applications, and exporters.
2. **Recording Rules:** Prometheus processes these metrics using predefined expressions in the recording rules, which simplify and precompute frequently-used or complex queries.
3. **Prometheus Database:** The results of the recording rules are stored as new metrics in the Prometheus database, enabling faster querying and visualization.
4. **Visualization Tools:** Tools like Grafana can directly query these precomputed metrics, significantly reducing dashboard latency and improving user experience.

### **Benefits of Recording Rules**

By defining recording rules, you can:
- Reduce query latency.
- Simplify complex expressions for reuse.
- Enable sequential and parallel processing of rules within groups.



## **Configuration for Recording Rules**

### **`prometheus.yml` Structure**

The `prometheus.yml` file is the main configuration file for Prometheus. Below is an example of its structure:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']

rule_files:
  - "rules.yml"
```

The `rule_files` directive in the Prometheus configuration specifies the list of external YAML files that contain recording and alerting rules. These files are loaded by Prometheus to periodically evaluate defined PromQL expressions and store the results.

### **`rules.yml` Structure**

The `rules.yml` file contains recording and alerting rules. It uses the following structure:

```yaml
groups:
  - name: <group_name-1>
    interval: <evaluation_interval>
    rules:
      - record: <rule_name-1>
        expr: <PromQL_expression-1>
        labels:
          <label_key>: <label_value>

      - record: <rule_name-2>
        expr: <PromQL_expression-2>
        ...    

  - name: <group_name-2>
    interval: <evaluation_interval>
    ...
```

1. **`groups`**: Contains one or more rule groups.
2. **`interval`**: Defines how often the rules in the group are evaluated. If omitted, the global evaluation interval is used.
3. **`rules`**: Defines individual rules within a group.
   - **`record`**: Name of the rule.
   - **`expr`**: PromQL expression to be evaluated.
   - **`labels`** (optional): Adds or modifies labels for the result.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/rule-exec.svg)

**Groups** in Prometheus are evaluated in parallel to maximize efficiency, meaning multiple rule groups can be processed at the same time. However, within each **group**, the **rules** are executed sequentially, in the order they are listed. This sequential execution ensures that if one rule depends on the result of a preceding rule, the dependency is correctly handled.


## **Examples**

### **Example 1: Memory Free Percentage**

```yaml
- record: node_memory_free_percent
  expr: (node_memory_MemFree_bytes / node_memory_MemTotal_bytes) * 100
```

This rule calculates the percentage of free memory available on a node.

### **Example 2: Filesystem Free Percentage**

```yaml
- record: node_filesystem_free_percent
  expr: (node_filesystem_free_bytes / node_filesystem_size_bytes) * 100
```

**Explanation:**
- These rules simplify repetitive calculations and speed up dashboard rendering by precomputing the metrics.



## **Task description**

You are tasked with monitoring the memory and filesystem usage of your server nodes. Configure Prometheus to periodically evaluate these metrics and store them as recording rules. Validate the setup by querying the recorded metrics.



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


### **3. Expose Prometheus UI**

- Get the `IP` to create a load balancer:

  ```bash
  ifconfig
  ```

  Here copy the `IP` from `eth0` interface:

  ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/image.png?raw=true)

- Create a load balancer from `Poridhi Lab` by providing the `IP` and `port: 9090`.


- Access the UI by opening the load balancer URL from browser. Go to *status > target*. We can see that prometheus has only one target and it is prometheus itself. Currently, it doesn't have `node_exporter` as its target to scrape. We have to configure the prometheus to scrape the `node_exporter`. 

  ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/image-1.png?raw=true)


### **4. Configure Prometheus Target**

Add the Node Exporter as a target in `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
```

![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/image-2.png?raw=true)

Restart Prometheus:

```bash
sudo systemctl restart prometheus
```

### **5. Create a Rule File**

Navigate to the Prometheus configuration directory (e.g., `/etc/prometheus/`) and create a new rule file named `rules.yml`.

```bash
cd /etc/prometheus
sudo vi rules.yml
```

### **6. Define Recording Rules**

Add the following rules to `rules.yml`:

```yaml
groups:
  - name: node_rules
    interval: 30s
    rules:
      - record: node_memory_free_percent
        expr: (node_memory_MemFree_bytes / node_memory_MemTotal_bytes) * 100

      - record: node_filesystem_free_percent
        expr: (node_filesystem_free_bytes / node_filesystem_size_bytes) * 100
```


### **7. Update Prometheus Configuration**

Edit `prometheus.yml` to include the rule file:

```yaml
rule_files:
  - "rules.yml"
```

![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/image-3.png?raw=true)

### **8. Reload Prometheus**

Restart Prometheus to apply the changes:

```bash
sudo systemctl restart prometheus
```

### **9. Validate Targets**

Access the Prometheus web interface and navigate to **Status > Target**. Verify the targets are listed and in the "UP" state.

![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/image-4.png?raw=true)


### **10. Validate Rules**

Access the Prometheus web interface and navigate to **Status > Rules**. Verify the rules are listed and in the "OK" state.

![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/image-5.png?raw=true)

### **11. Query Metrics**

Use the Prometheus expression browser to query the recorded metrics:

- Query `node_memory_free_percent` to see the memory free percentage.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/image-6.png?raw=true)

- Query `node_filesystem_free_percent` to see the filesystem free percentage.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2017/images/image-7.png?raw=true)



## **Best Practices**

1. **Group Rules by Job**: Define separate groups for each job (e.g., `node`, `docker`) to organize rules logically.
2. **Sequential Rule Execution**: Ensure dependent rules are placed sequentially within the same group.
3. **Descriptive Rule Names**: Follow the naming convention `level:metric:operation`.
   - Example: `job_node_memory_free:avg`.
4. **Use Globs for Multiple Rule Files**: Use patterns like `rules/*.yml` to include multiple rule files automatically.
5. **Test Rules Before Deployment**: Use the Prometheus expression browser to test PromQL expressions before adding them as recording rules.



## **Conclusion**

Recording rules improve Prometheus query efficiency and simplify the reuse of complex metrics. By organizing and managing rules effectively, you can optimize your monitoring setup and ensure smoother integrations with visualization tools.



