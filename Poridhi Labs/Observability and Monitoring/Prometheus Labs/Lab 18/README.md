# Understanding Application Instrumentation

Application instrumentation is the process of adding monitoring capabilities to your application's code to measure its performance and behavior. It's like adding sensors to your application that help you understand what's happening inside while it's running. Think of it as similar to how a car's dashboard provides critical information about speed, fuel level, and engine temperature.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/87e2faa5791ef084229170ef8156365973343c89/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2018/images/app%20instrument.svg)


### Why Instrument Applications?

1. `Performance Monitoring`: Track response times, resource usage, and bottlenecks
2. `Error Detection`: Identify and diagnose problems quickly
3. `Business Insights`: Measure user behavior and application usage patterns
4. `Capacity Planning`: Make informed decisions about scaling and resource allocation


### Prometheus client libraries 
Prometheus client libraries make instrumentation straightforward by providing pre-defined metric types and utilities to track, expose, and update metrics dynamically during application execution. These metrics can then be scraped by Prometheus for visualization and alerting.

Prometheus supports official client libraries for several programming languages, including: **Go**, **Java**, **Python**, **Ruby**, **Rust**. For other languages, unofficial libraries are available, or developers can create custom libraries to avoid dependencies.

## Task Description

We'll build a Flask web application that demonstrates the `Counters` types of Prometheus metrics used for tracking total numbers of specific events. We'll also see why we need `labels` for metrics and how to add labels. We'll be using docker for prometheus.

Our application will expose these metrics through an HTTP endpoint that Prometheus can scrape.


## Setup the Environment

1. Create a project directory:
   ```bash
   mkdir prometheus-lab
   cd prometheus-lab
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required libraries:
   ```bash
   pip install flask prometheus-client
   ```

These packages provide:
- `Flask`: Web framework for building our application
- `prometheus-client`: Official Python client library for Prometheus

## Flask Application Code

Let's break down our application code piece by piece in `app.py`:


The code is a Python application built with Flask and uses the `prometheus_client` library to monitor and expose metrics for Prometheus. Let’s break down each part, focusing on how **Counter metrics** are used and their functionality.



### 1. **Setup and Imports**
```python
from flask import Flask, request
from prometheus_client import Counter, generate_latest, start_http_server
```
- **Flask:** The web framework used to handle HTTP requests.
- **prometheus_client:**
  - `Counter`: A Prometheus metric type for counting events.
  - `generate_latest`: A function to format metrics into Prometheus-compatible output.
  - `start_http_server`: Used to expose a metrics endpoint (though not utilized here explicitly).



### 2. **Initialize Flask App**
```python
app = Flask(__name__)
```
- Creates a Flask app instance to define routes and handle HTTP requests.



### 3. **Prometheus Counter Metric**
```python
http_requests_total = Counter(
    'http_requests_total', 
    'Total HTTP requests'
)
```
- **Purpose:** The `Counter` metric counts the number of events, such as HTTP requests.
- **Parameters:**
  - `'http_requests_total'`: The name of the metric as it will appear in Prometheus.
  - `'Total HTTP requests'`: A human-readable description of the metric.
- **Behavior:** Each time the `inc()` method is called on this counter, it increments its value by 1.



### 4. **Define Routes and Increment Counter**
#### Route: `/cars`
```python
@app.route('/cars', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def cars():
    # Increment Counter
    http_requests_total.inc()

    if request.method == 'GET':
        return {"message": "Fetching all cars."}
    elif request.method == 'POST':
        return {"message": "Creating a new car."}
    elif request.method == 'PATCH':
        return {"message": "Updating car details."}
    elif request.method == 'DELETE':
        return {"message": "Deleting a car."}
```
- **What Happens:**
  - The route `/cars` handles multiple HTTP methods: `GET`, `POST`, `PATCH`, and `DELETE`.
  - The line `http_requests_total.inc()` increments the `http_requests_total` counter by 1 each time the `/cars` endpoint is accessed.
  - Each method returns a corresponding message.

#### Route: `/boats`
```python
@app.route('/boats', methods=['GET', 'POST'])
def boats():
    # Increment Counter
    http_requests_total.inc()

    if request.method == 'GET':
        return {"message": "Fetching all boats."}
    elif request.method == 'POST':
        return {"message": "Creating a new boat."}
```
- **What Happens:**
  - Similar to `/cars`, the `/boats` route supports `GET` and `POST` methods.
  - Every time this route is accessed, `http_requests_total.inc()` increments the counter by 1.



### 5. **Metrics Endpoint**
```python
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
```
- **Purpose:** This route exposes all Prometheus metrics collected by the application.
- **How It Works:**
  - `generate_latest()` formats the metrics into a text format compatible with Prometheus.
  - The response is returned with the appropriate content type (`text/plain`).



### 6. **Run the App**
```python
if __name__ == '__main__':
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000)
```
- Starts the Flask application on `0.0.0.0:5000`.

### 7. **Run the Application**

Run the application using the following command:
```bash
python3 app.py
```

### **How Counter Metrics Work**
  
We used Counter metrics to monitor the total number of HTTP requests received by the application, which can be helpful for understanding traffic patterns and diagnosing issues.
  - Each time `http_requests_total.inc()` is called, the counter value increases by 1.
  - In this application, `http_requests_total` is incremented each time an endpoint (`/cars` or `/boats`) is accessed.






## Run prometheus server using docker

### 1. Setup prometheus configuration in `prometheus.yml` :

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'flask-app'
    static_configs:
      - targets: ['<ip-adress>:5000']
```

Get the `ip-address` from `eth0` ip address using `ifconfig` command. 

### 2. `docker-compose.yml` for prometheus server:

```yaml
version: '3'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - monitoring

networks:
  monitoring:
```

### 3. Running the docker container:
```bash
docker-compose up -d 
```

## Create Load Balancer and send HTTP requests

### 1. Create load balancer for flask-app and prometheus UI:
- Get the `eth0` IP using `ifconfig` command.
- Create a load balancers with the `IP` address and port `9090` for prometheus dashboard.
- Create another load balancer with the `IP` address and port `5000` for flask app.


### 2. Generate some test data using `Postman`:

- Send some `GET/POST/DELETE` request to the address:
`<flask-app-lb-url>/cars`.

  ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2018/images/image.png?raw=true)

  ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2018/images/image-1.png?raw=true)

- Send some `GET/POST` request to the address:
`<flask-app-lb-url>/boats`.

  ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2018/images/image-2.png?raw=true)

    


## Access Prometheus UI and Query Metrics

1. Open the load balancer url for prometheus service. 

2. Check if the target is in `up` state from: *status > target health*

    ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2018/images/image-3.png?raw=true)

3. Query using the promQL:

    ```promql
    http_requests_total
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2018/images/image-4.png?raw=true)


## Why We Need Labels
Labels in Prometheus metrics allow us to add key-value pairs that provide additional context, enabling more granular monitoring and filtering. Labels enhance the granularity of metrics, enabling you to:

1. **Monitor Specific Endpoints and Methods:**
   - For example, you can query the total number of `GET` requests to `/cars` or `POST` requests to `/boats`.
2. **Analyze API Traffic Patterns:**
   - Labels make it easy to identify which routes or methods are most frequently used or underutilized.
3. **Troubleshoot Issues:**
   - If a particular endpoint is causing errors or slowdowns, labeled metrics can help isolate the problem.

##  Add Labels in the Code


In this updated version of the code in `app.py`, labels have been added to the Prometheus `Counter` metric to provide more detailed tracking. Let’s explore the changes and their significance:


### **1. Changes in the `Counter` Metric Initialization**
#### Previous Code:
```python
http_requests_total = Counter(
    'http_requests_total', 
    'Total HTTP requests'
)
```
- This defined a basic counter that tracked the **total number of HTTP requests** without distinguishing between methods or endpoints.

#### Updated Code:
```python
http_requests_total = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint']
)
```
- **Added Labels:**
  - `['method', 'endpoint']` specifies two labels:
    - `method`: Tracks the HTTP method used (e.g., `GET`, `POST`).
    - `endpoint`: Tracks the specific endpoint accessed (e.g., `/cars`, `/boats`).
- **Purpose:** Allows grouping and querying of metrics based on specific HTTP methods and endpoints.



### **2. Changes in Incrementing the Counter in `/cars` and `/boats` endpoints**
#### Previous Code:
```python
http_requests_total.inc()
```
- This incremented the counter without adding any additional context, only tracking the total count of all HTTP requests across the entire application.

#### Updated Code in `/cars` endpoint:
```python
http_requests_total.labels(method=request.method, endpoint='/cars').inc()
```

#### Updated Code in `/boats` endpoint:
```python
http_requests_total.labels(method=request.method, endpoint='/boats').inc()
```

- **Labels Context:**
  - `labels(method=request.method, endpoint='/cars')` adds the HTTP method and endpoint as specific labels to this metric increment.
- **Behavior:**
  - Every request to `/cars` or `/boats` will now be counted separately based on the combination of `method` and `endpoint` labels.


### Restart the App 

Use the following command to restart the app:
```bash
python3 app.py
```



## Send HTTP Requests and Query Metrics

1. Send some `GET/POST` requests in the `/cars` or `/boats` endpoints using postman as before. 

2. Go to prometheus dashboard and use the following promql to query the metrics:

    ```bash
    http_requests_total
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2018/images/image-5.png?raw=true)

3. You can now use promql to query specific http requests in specific endpoinds and for specific methods as follows:

    ```
    http_requests_total{method="POST", endpoint="/cars"}
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2018/images/image-6.png?raw=true)



## Conclusion

In this lab, we explored the basics of application instrumentation using Prometheus by integrating the `prometheus_client` library into a Flask application. We demonstrated how to use `Counter` metrics to monitor HTTP requests, exposed these metrics through a `/metrics` endpoint, and configured Prometheus to scrape and visualize the data. By using Docker for Prometheus setup and testing the application through HTTP requests, we gained hands-on experience in monitoring and understanding application performance. This foundation can be extended with other Prometheus metric types and advanced queries for deeper insights into application behavior.