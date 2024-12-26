# Pushing Metrics to Push Gateway

Pushing metrics to a Pushgateway is a fundamental step in exporting metrics for Prometheus. This process allows ephemeral or batch jobs to expose their metrics for collection and monitoring. 

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/pushgateway2.svg)

There are two primary methods for pushing metrics: **HTTP Requests** and **Prometheus Client Libraries**.


1. **HTTP Requests:** Metrics can be sent directly to the Pushgateway via HTTP POST or PUT requests. This method involves constructing a specific URL path that defines the job name and optional label-value pairs, which act as grouping keys. These keys organize metrics into logical groups for easier updates or deletions. Tools like `curl`, Postman, or any HTTP client can be used for this approach. 

2. **Prometheus Client Libraries:** This method integrates directly with programming languages such as Python, Java, or Go. Metrics are registered, updated, and pushed using prebuilt functions. It provides more flexibility and programmatic control compared to HTTP requests.

Both methods enable efficient handling of metrics, allowing for updates, grouping, and even deletion, ensuring that metrics remain consistent and relevant to the intended monitoring use cases.



## Task Description

In this hands-on lab, we will cover the following tasks:

- Install and configure **Prometheus** using a setup script.  
- Install and configure **Pushgateway** using a setup script.  
- Expose Prometheus and Pushgateway UIs using load balancers.  
- Configure Prometheus to scrape metrics from Pushgateway.  
- Push metrics to Pushgateway using HTTP requests and organize them using job and label-based grouping.  
- Verify pushed metrics through the Pushgateway UI, Prometheus UI, and PromQL queries.  
- Push metrics to Pushgateway using Client Libraries.



## **Setup Prometheus and Push Gateway**

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




### **2. Setup Script for Push Gateway**

Create a setup script to automate the installation of push gateway.

#### **Create a Script as `pushgateway.sh`:**

```bash
#!/bin/bash

# Variables
PUSH_VERSION="1.10.0"
PUSH_USER="pushgateway"
PUSH_BINARY_URL="https://github.com/prometheus/pushgateway/releases/download/v${PUSH_VERSION}/pushgateway-${PUSH_VERSION}.linux-amd64.tar.gz"
PUSH_BIN_PATH="/usr/local/bin"

# Install wget and tar
sudo apt-get update && sudo apt-get install -y wget tar

# Download and extract Push Gateway
wget $PUSH_BINARY_URL && tar -xvzf pushgateway-${PUSH_VERSION}.linux-amd64.tar.gz

# Move binaries
cd pushgateway-${PUSH_VERSION}.linux-amd64
sudo mv pushgateway $PUSH_BIN_PATH/

# Create Push Gateway user and assign permissions
sudo useradd --no-create-home --shell /bin/false $PUSH_USER
sudo chown $PUSH_USER:$PUSH_USER $PUSH_BIN_PATH/pushgateway

# Create systemd service file
sudo tee /etc/systemd/system/pushgateway.service > /dev/null <<EOT
[Unit]
Description=Prometheus Push Gateway
After=network.target

[Service]
User=$PUSH_USER
Group=$PUSH_USER
ExecStart=$PUSH_BIN_PATH/pushgateway
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOT

# Reload systemd, enable and start Push Gateway
sudo systemctl daemon-reload
sudo systemctl enable --now pushgateway

# Check status
sudo systemctl status pushgateway

```

#### **Run the Script:**

```bash
chmod +x pushgateway.sh
sudo ./pushgateway.sh
```



### **3. Expose Prometheus UI**

- Get the `IP` to create a load balancer:

  ```bash
  ifconfig
  ```

  Here copy the `IP` from `eth0` interface:

  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image.png)

- Create a load balancer from `Poridhi Lab` by providing the `IP` and `port: 9090`.


- Access the UI by opening the load balancer URL from browser. Go to *status > target*. We can see that prometheus has only one target and it is prometheus itself. 

  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-1.png)




### **4. Expose Push Gateway UI**

- Get the `IP` to create a load balancer:

  ```bash
  ifconfig
  ```

- Create a load balancer from `Poridhi Lab` by providing the `IP` and `port: 9091`.


- Access the UI by opening the load balancer URL from browser. 

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-2.png)




### **5. Configure Prometheus to Push Gateway**

Prometheus needs to be configured to scrape the metrics from Push Gateway.

- **Edit Prometheus Configuration:**

  ```bash
  sudo vi /etc/prometheus/prometheus.yml
  ```

- Add the following job under the `scrape_configs` section:

  ```yaml
  - job_name: 'pushgateway'
    static_configs:
      - targets: ['<pushgateway-server>:9091']
    honor_labels: true
  ```

  We are using `localhost` as `<pushgateway-server>` as it is in the same host as prometheus.

  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-4.png)



- **Restart Prometheus:**

  ```bash
  sudo systemctl daemon-reload
  sudo systemctl restart prometheus
  ```

- **Access/Reload the prometheus UI**

  Now you can see that the Prometheus is scraping the `pushgateway`. It may take a while to get the `up` state:

  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-5.png)




## **Pushing Metrics to Push Gateway with HTTP Requests**

### **1. Pushing Metrics via HTTP Requests**

Metrics can be pushed to Pushgateway using HTTP POST or PUT requests. The URL format includes the Pushgateway address, port, `/metrics/`, and a job name, optionally followed by label-value pairs. For example:
`http://<pushgateway-address>:<port>/metrics/job/<job_name>/label/<label_key>/<label_value>`
The data is passed as binary, commonly using tools like `curl`. POST replaces metrics with the same name, while PUT replaces all metrics in the group.

#### **Send a Single Metric**
Use an HTTP POST request to send a metric to Pushgateway.

- Command:
  ```bash
  echo "example_metric 4421" | curl --data-binary @- http://localhost:9091/metrics/job/db_backup
  ```
- Explanation:
  - **`example_metric`**: The name of the metric.
  - **`4421`**: The metric value.
  - **`/job/db_backup`**: Sets the `job` label as `db_backup`.

#### **Verify the Metric**
- To confirm the metric is pushed, check the Pushgateway metrics:
    ```bash
    curl http://localhost:9091/metrics
    ```

- You can also verify the pushgateway metrics from the Pushgateway UI sevice running using load balancer:

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-3.png)


- We can use promQL in prometheus UI to verify the pushgateway metrics:
    ```promql
    example_metric{job = "db_backup"}
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-6.png)


### **2. Grouping Metrics**

Grouping organizes metrics based on the URL path, which includes the job name and labels. Metrics sharing the same path belong to a group, enabling bulk updates or deletions. For instance, metrics sent to `/job/archive/db=mysql` are grouped separately from those sent to `/job/archive/app=web`. This structure simplifies managing and isolating related metrics effectively.



Grouping metrics allow you to update & delete all metrics in a specific group without impacting the metrics in other groups.

- #### **Task**

    Push the following metrics to the PushGateway and group the metrics as `/job/video_processing/instance/mp4_node1`

    ```
    processing_time_seconds{quality="hd"} 120
    processed_videos_total{quality="hd"} 10
    processed_bytes_total{quality="hd"} 4400
    ```

    Next, push the following metrics to the PushGateway and group the metrics as `/job/video_processing/instance/mov_node1`

    ```
    processing_time_seconds{quality="hd"} 400
    processed_videos_total{quality="hd"} 250
    processed_bytes_total{quality="hd"} 96000
    ```


    Finally, be sure that these metrics are listed as gauge metrics.

- #### **Solution**

    #### Push Metrics with Labels
    Push two metrics with labels forming a group:
    ```bash
    cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/video_processing/instance/mp4_node1
    # TYPE processing_time_seconds gauge
    processing_time_seconds{quality="hd"} 120
    # TYPE processed_videos_total gauge
    processed_videos_total{quality="hd"} 10
    # TYPE processed_bytes_total gauge
    processed_bytes_total{quality="hd"} 4400
    EOF
    ```

    #### Push Metrics to Another Group
    Push similar metrics to a different group:
    ```bash
    cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/video_processing/instance/mov_node1
    # TYPE processing_time_seconds gauge
    processing_time_seconds{quality="hd"} 400
    # TYPE processed_videos_total gauge
    processed_videos_total{quality="hd"} 250
    # TYPE processed_bytes_total gauge
    processed_bytes_total{quality="hd"} 96000
    EOF
    ```

    #### Verify Groups
    Verify that all six metrics are visible on the Prometheus server by performing the following query in the expression browser:

    ```
    {job="video_processing"}
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-7.png)


### **3. HTTP Methods and Their Effects**

#### **POST Request**

- #### **Task**

    Currently the metrics from the first group i.e., `/job/video_processing/instance/mp4_node1` look like as below:

    ```
    processing_time_seconds{quality="hd"} 120
    processed_videos_total{quality="hd"} 10
    processed_bytes_total{quality="hd"} 4400
    ```



    Now, send a `POST` request to the same group with the following metric:
    ```
    processing_time_seconds{quality="hd"} 999
    ```

- #### **Solution**


    Updates metrics with the same name in the group while retaining others.
    ```bash
    cat <<EOF | curl --data-binary @- http://localhost:9091/metrics/job/video_processing/instance/mp4_node1
    # TYPE processing_time_seconds gauge
    processing_time_seconds{quality="hd"} 999
    EOF
    ```

    Verify the changes using the following query in the prometheus UI:

    ```
    processing_time_seconds{instance="mp4_node1", quality="hd"}
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-8.png)

#### **PUT Request**

- #### **Task**

    Currently, the metrics from the first group i.e., `/job/video_processing/instance/mp4_node1` look like as below:

    ```
    processing_time_seconds{quality="hd"} 999
    processed_videos_total{quality="hd"} 10
    processed_bytes_total{quality="hd"} 4400
    ```

    Now, send a `PUT` request with the following metric to this group:

    ```
    processing_time_seconds{quality="hd"} 666
    ```

- #### **Solution**
    Run the following to send a PUT request:

    ```bash
    cat <<EOF | curl -X PUT --data-binary @- http://localhost:9091/metrics/job/video_processing/instance/mp4_node1
    # TYPE processing_time_seconds gauge
    processing_time_seconds{quality="hd"} 666
    EOF
    ```

    Verify the changes using the following query in the prometheus UI:
    ```
    processing_time_seconds{instance="mp4_node1"}
    ```

    All the metrics are replaced with the new one.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-9.png)






#### **DELETE Request**

- #### **Task**

    Let's send a DELETE request to remove all metrics from the `/job/video_processing/instance/mp4_node1` group.


    Once done, verify that all metrics in this group have been removed, but all metrics under the `/job/video_processing/instance/mov_node1 group` still persist.

- #### **Solution**

    Run below command:

    ```
    curl -X DELETE http://localhost:9091/metrics/job/video_processing/instance/mp4_node1
    ```

    Verify the changes:

    Use the following promql to see all metrics from the `/job/video_processing/instance/mp4_node1` group are removed:

    ```
    {job="video_processing", instance="mp4_node1"}
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-10.png)

    Use the following promql to see  all metrics under the `/job/video_processing/instance/mov_node1 group` still persist:

    ```
    {job="video_processing", instance="mov_node1"}
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-11.png)

## **Pushing Metrics to Push Gateway with Prometheus Client Library**

Pushing metrics to Pushgateway using the Prometheus Client Library involves defining metrics in your code, associating them with a `CollectorRegistry`, and updating their values. Once ready, you use methods like `pushadd_to_gateway` to send metrics to Pushgateway by specifying its address, port, job name, and the registry. This approach allows you to programmatically track and push metrics, making it ideal for dynamically generated data in applications.

### **1. Pushing Metrics with Prometheus Client Library**

#### **Install the Library**
```bash
pip install prometheus-client
```

#### **Python Code Example**
Create a python script `app.py`:
```python
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Create a registry
registry = CollectorRegistry()

# Define a Gauge metric
metric = Gauge('example_metric', 'An example metric', registry=registry)

# Set the metric value
metric.set(100)

# Push the metric to Pushgateway
push_to_gateway('localhost:9091', job='example_job', registry=registry)
```

#### **Run the Script**
Save the script as `app.py` and run it:
```bash
python3 app.py
```

#### **Verify the Metric**
Check the metric in Pushgateway:
```bash
curl http://localhost:9091/metrics
```


Verify the metric from the prometheus UI using the following query:

```
example_metric
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2022/images/image-12.png)



### **2. Using Different Functions in Prometheus Client**


Mapping of Prometheus Client Library functions to HTTP methods:

1. **`push` (Client Library)**  
   - **HTTP Equivalent**: `PUT`  
   - **Behavior**: Replaces all metrics within a specific group with the new metrics being pushed.

2. **`pushadd` (Client Library)**  
   - **HTTP Equivalent**: `POST`  
   - **Behavior**: Updates metrics with the same name in the group and retains all other metrics unchanged.

3. **`delete` (Client Library)**  
   - **HTTP Equivalent**: `DELETE`  
   - **Behavior**: Removes all metrics within the specified group.


#### **Example Usage**

- **Push**: Replaces all metrics for a job.
  ```python
  from prometheus_client import push_to_gateway
  push_to_gateway('localhost:9091', job='example_job', registry=registry)
  ```
- **Pushadd**: Updates or adds metrics with the same name, keeps others unchanged.
  ```python
  from prometheus_client import pushadd_to_gateway
  pushadd_to_gateway('localhost:9091', job='example_job', registry=registry)
  ```
- **Delete**: Deletes all metrics for a job.
  ```python
  from prometheus_client import delete_from_gateway
  delete_from_gateway('localhost:9091', job='example_job')
  ```



## **Conclusion**
This lab covered multiple methods to push metrics to Pushgateway, including HTTP requests (POST, PUT, DELETE) and Prometheus client libraries. You also explored grouping and how various HTTP methods affect metrics. Use these techniques to manage metrics efficiently for batch jobs in Prometheus!