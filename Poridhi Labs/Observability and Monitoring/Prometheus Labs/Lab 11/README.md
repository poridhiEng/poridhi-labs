# Aggregation and Vector Matching in PromQL

PromQL (Prometheus Query Language) is a powerful tool for analyzing time-series metrics. It provides features for **aggregation** and **vector matching**, enabling detailed insights into system performance and behavior. With Aggregation and Vector Matching, you can perform complex queries and analyze metrics more effectively. We will use Prometheus to collect metrics from Node Exporter and perform aggregation and vector matching queries.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/e2a1a2e086407a3ed174a9c47936995572ca8acc/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/banaer.svg)



## **Objectives**
By the end of this lab, you will:
1. Install and configure Prometheus using scripts.
2. Set up Node Exporter for metric collection.
3. Access Prometheus via a LoadBalancer.
4. Understand aggregation and vector matching in PromQL.


## **What are Aggregation and Vector Matching?**

### **Aggregation**
Aggregation in PromQL simplifies metrics by summarizing them across dimensions using functions like `sum`, `avg`, `min`, `max`, and `count`. For example:
- **Total memory usage**: `sum(node_memory_MemAvailable_bytes)`
- **Average CPU usage**: `avg(rate(node_cpu_seconds_total[5m]))`

### **Vector Matching**
Vector matching aligns labels between metrics for operations like division or addition. Features include:
- `on`: Match specific labels only.
- `ignoring`: Ignore specified labels.
- `group_left`/`group_right`: Handle one-to-many or many-to-one relationships.


## **Prometheus Setup**

Use the script below to install and configure Prometheus.

1. Create and save the script as `prometheus.sh`:
    ```bash
    #!/bin/bash

    PROM_VERSION="2.53.2"
    PROM_USER="prometheus"
    PROM_DIR="/etc/prometheus"
    PROM_LIB_DIR="/var/lib/prometheus"
    PROM_BINARY_URL="https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-amd64.tar.gz"
    PROM_BIN_PATH="/usr/local/bin"

    sudo apt-get update && sudo apt-get install -y wget tar
    wget $PROM_BINARY_URL && tar -xvzf prometheus-${PROM_VERSION}.linux-amd64.tar.gz
    sudo mv prometheus-${PROM_VERSION}.linux-amd64/{prometheus,promtool} $PROM_BIN_PATH/
    sudo mkdir -p $PROM_DIR $PROM_LIB_DIR && sudo mv prometheus-${PROM_VERSION}.linux-amd64/{prometheus.yml,consoles,console_libraries} $PROM_DIR/

    sudo useradd --no-create-home --shell /bin/false $PROM_USER
    sudo chown -R $PROM_USER:$PROM_USER $PROM_DIR $PROM_LIB_DIR

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

    sudo systemctl daemon-reload
    sudo systemctl enable --now prometheus
    sudo systemctl status prometheus
    ```

2. Make the script executable and run it:
    ```bash
    chmod +x prometheus.sh
    ./prometheus.sh
    ```

## **Node Exporter Setup**

1. Create and save the script as `exporter.sh`:
    ```bash
    #!/bin/bash

    NODE_EXPORTER_VERSION="1.8.2"
    NODE_EXPORTER_USER="node_exporter"
    NODE_EXPORTER_BINARY_URL="https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
    NODE_EXPORTER_BIN_PATH="/usr/local/bin"

    sudo apt-get update && sudo apt-get install -y wget tar
    wget $NODE_EXPORTER_BINARY_URL && tar -xvzf node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz
    sudo mv node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter $NODE_EXPORTER_BIN_PATH/

    sudo useradd --no-create-home --shell /bin/false $NODE_EXPORTER_USER
    sudo chown $NODE_EXPORTER_USER:$NODE_EXPORTER_USER $NODE_EXPORTER_BIN_PATH/node_exporter

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

    sudo systemctl daemon-reload
    sudo systemctl enable --now node_exporter
    sudo systemctl status node_exporter
    ```

2. Make the script executable and run it:
    ```bash
    chmod +x exporter.sh
    ./exporter.sh
    ```

## **Access Prometheus via LoadBalancer**

1. Get the `eth0` IP of your VM:
   ```bash
   ifconfig
   ```
   ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2005/images/lab-59.png?raw=true)
   
2. Configure a LoadBalancer using your IP and port `9090`.

3. Access Prometheus through the provided URL. Verify the `node_exporter` target is **UP** under **Status > Targets**.

   ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/1.png?raw=true)

## **PromQL Aggregation Queries**

### 1. Summing Metrics

Perform a sum of available memory across all nodes.

```promql
sum(node_memory_MemAvailable_bytes)
```
![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/2.png?raw=true)


### 2. Averaging Metrics

Perform an average of free disk space per mountpoint.
```promql
avg(node_filesystem_avail_bytes) by (mountpoint)
```
![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/3.png?raw=true)


### 3. Counting Instances

Count the number of instances exporting memory metrics.

```promql
count(node_memory_MemAvailable_bytes)
```

### 4. Maximum Value

Finds the maximum memory available among all nodes.

```promql
max(node_memory_MemAvailable_bytes)
```
![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/4.png?raw=true)

### 5. Minimum Value

Finds the minimum memory available among all nodes.

```promql
min(node_memory_MemAvailable_bytes)
```

### 6. Standard Deviation

Calculates the standard deviation of available memory across instances.

```promql
stddev(node_memory_MemAvailable_bytes)
```

### 7. Total Disk Usage

Calculates the total used disk space across all nodes.

```promql
sum(node_filesystem_size_bytes - node_filesystem_free_bytes)
```

### 8. CPU Usage Percentage

Calculates the average percentage of CPU used across all nodes.

```promql
100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100
```
![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/5.png?raw=true)

## **PromQL Vector Matching Queries**

### 1. One-to-One Matching

Matches free and total disk space for the same mount point to calculate the percentage of free disk space. Here `One-to-One` refers to the fact that we are matching the same mount point for both free and total disk space.

```promql
(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100
```
![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/6.png?raw=true)

### 2. Ignoring Labels

Ignores the `fstype` label and matches vectors by `mountpoint` and `instance`.

```promql
node_filesystem_avail_bytes / ignoring(fstype) node_filesystem_size_bytes * 100
```
![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/7.png?raw=true)

### 3. Matching by Instance

Matches CPU usage by `instance`, focusing on `user` vs. `idle` modes after aggregating over `cpu`.

```promql
sum(rate(node_cpu_seconds_total{mode="user"}[1m])) by (instance)
/
sum(rate(node_cpu_seconds_total{mode="idle"}[1m])) by (instance)
```
![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/8.png?raw=true)

### 4. Many-to-One Matching (`group_left`)

Matches multiple disk reads to a single instance. In this case, `Many-to-One` refers to the fact that we are matching multiple disk reads to a single instance.

```promql
rate(node_disk_reads_completed_total[5m]) / on(instance) group_left() rate(node_disk_writes_completed_total[5m])
```

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/9.png?raw=true)

### 5. Network Traffic Comparison

Compares received and transmitted network traffic for performance analysis.

```promql
rate(node_network_receive_bytes_total[5m]) / rate(node_network_transmit_bytes_total[5m])
```

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2011/images/91.png?raw=true)

## **Conclusion**

In this lab, you:
-  Installed and configured Prometheus and Node Exporter.
- Used a LoadBalancer to access Prometheus.
- Learned aggregation and vector matching in PromQL.
- Executed queries to analyze system metrics.