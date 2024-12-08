# Autoscaling with Keda and Prometheus Using Custom Metrics

Autoscaling with KEDA and Prometheus Using Custom Metrics
This documentation provides a step-by-step guide to implement autoscaling for Kubernetes pods using KEDA (Kubernetes Event-Driven Autoscaler), Prometheus, and custom metrics. The process includes creating a custom metric in Go, deploying the app on Kubernetes, configuring Prometheus for metrics scraping, and setting up Keda to enable autoscaling based on these metrics. By combining these tools, Kubernetes can scale workloads dynamically based on real-time metrics derived from the application.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/arch_final2.drawio.svg)

## Key Components Overview

**Prometheus**

Prometheus is an open-source monitoring and alerting toolkit designed for reliability and scalability. It uses a pull-based approach to scrape metrics from endpoints, storing them as time-series data. Prometheus is commonly integrated with Kubernetes for monitoring workloads and cluster health.

**KEDA**

KEDA is an open-source event-driven autoscaler that extends Kubernetes Horizontal Pod Autoscalers (HPA) by enabling scaling based on various custom metrics or external triggers. Examples include message queue length, database records, or Prometheus queries.

## Prerequirements


**Install helm**

Make sure you have helm installed on you machine or you can install this using the following command:

```sh
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

Check the helm version

```sh
helm version
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-2.png)

**Configure helm:**

If you are facing this issue:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-3.png)

This is due to the fact that, Helm is unable to connect to the Kubernetes cluster. As helm could not find the the correct kubeconfig file in this directory: `~/.kube/config` To solve this issue, we have to set up the correct path of kubeconfig file. This will solve the issue.

```sh
kubectl config view --raw > /root/.kube/config
chmod 600 /root/.kube/config
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-4.png)


## Go Application: Exposing Custom Metrics

The following Go application exposes custom Prometheus metrics:

```python
from flask import Flask, request, Response
from prometheus_client import Counter, Histogram, generate_latest
import time

# Create a Flask application
app = Flask(__name__)

# Prometheus metrics
http_request_count_with_path = Counter(
    'http_requests_total_with_path',
    'Number of HTTP requests by path.',
    ['url']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'Response time of HTTP request.',
    ['path']
)

order_books_counter = Counter(
    'product_order_total',
    'Total number of product orders'
)

@app.route('/')
def home_route():
    return "Welcome", 200

@app.route('/product')
def order_handler():
    start_time = time.time()

    # Increment counters
    order_books_counter.inc()
    http_request_count_with_path.labels(url=request.path).inc()

    # Simulate processing delay
    time.sleep(0.1)

    # Calculate request duration
    duration = time.time() - start_time
    http_request_duration.labels(path=request.path).observe(duration)

    return "Order placed!", 200

@app.route('/metrics')
def metrics():
    # Return Prometheus metrics
    return Response(generate_latest(), mimetype="text/plain")

if __name__ == '__main__':
    # Start the Flask server
    app.run(host='0.0.0.0', port=8181)
```

### Code Explanation

**Custom Metrics Defined:**

- `http_requests_total_with_path`: Tracks HTTP requests by URL path.
- `http_request_duration_seconds`: Measures request duration.
- `product_order_total`: Counts the total number of product orders.

**Key Functionality:**

- `orderHandler`: Simulates order placement, increments counters, and tracks response times.
- `/metrics`: Exposes metrics in Prometheus-compatible format.

### Dockerize the Application

Here is the Dockerfile to Dockerize the Go application.

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY app.py /app/

RUN pip install flask prometheus-client

CMD ["python", "app.py"]
```

### Build and Push the Docker Image

Now build the docker image and push it to your dockerhub repository.

```sh
docker build -t <DOCKERHUB_USERNAME>/<IMAGE_NAME>:<VERSION> .
docker push <DOCKERHUB_USERNAME>/<IMAGE_NAME>:<VERSION>
```

> NOTE: Make sure to update the <> values

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image.png)


##  Deploying on Kubernetes

Now to deploy this application into kubernetes, we have to write Kubernetes manifests file.

### Kubernetes Manifests Files

**1. deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: goprometheus-deployment
  labels:
    app: goprometheus
spec:
  replicas: 2  # Running one pod on each worker node
  selector:
    matchLabels:
      app: goprometheus
  template:
    metadata:
      labels:
        app: goprometheus
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8181"
        prometheus.io/path: "/metrics"
    spec:
      nodeSelector:
        role: worker-node
      containers:
      - name: goprometheus
        image: your-registry/goprometheuskeda:v1
        ports:
        - containerPort: 8181
        resources:
          limits:
            memory: "128Mi"
            cpu: "500m"
          requests:
            memory: "64Mi"
            cpu: "250m"
```


**2. service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: goprometheus-service
spec:
  type: NodePort
  selector:
    app: goprometheus
  ports:
    - port: 8181
      targetPort: 8181
      nodePort: 30081
      protocol: TCP
```

**3. keda-scaledobject.yaml**

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: goprometheus-scaledobject
spec:
  scaleTargetRef:
    name: goprometheus-deployment
  minReplicaCount: 2  # Minimum 2 pods (one per worker node)
  maxReplicaCount: 6  # Maximum 3 pods per worker node
  cooldownPeriod: 30
  pollingInterval: 15
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus-server.prometheus.svc.cluster.local:80
      metricName: request_rate
      threshold: '20'
      query: sum(rate(product_order_total[5m])) * 300
```

## Helm installations and Upgrade

**1. Install Prometheus**

```sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus -n prometheus --create-namespace
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-5.png)

**2. Install KEDA**

```sh
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-6.png)


### Update the Prometheus Configuration

**Create a `prometheus-values.yaml` which will contain the scrap configs of Prometheus**

```yaml
extraScrapeConfigs: |
  - job_name: 'goprometheus'
    scrape_interval: 15s
    static_configs:
      - targets: ['goprometheus-service.default.svc.cluster.local:8181']
```

Now update the prometheus:

```sh
helm upgrade --install prometheus prometheus-community/prometheus -f prometheus-values.yaml -n prometheus
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-7.png)


## Labeling the Worker Nodes

First get the worker node name:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-32.png)

```sh
kubectl label nodes <worker-1> role=worker-node
kubectl label nodes <worker-2> role=worker-node
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-33.png)


## Deploy the application in kubernetes

```sh
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f keda-scaledobject.yaml
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-8.png)


## Testing and Monitoring the setup

This section demonstrates how to test the service scaling and monitor its behavior using Kubernetes tools

**1. Expose the Go application NodePort Service Using LoadBalancer:**

First get the MasterNode IP:

```sh
kubectl get nodes -o wide
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-28.png)


Create a load-balancer with the MasterNode IP and the NodePort of the Grafana service(`30081`):

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-31.png)

**2. Monitor resource scaling:**

Use the watch command to observe the pods, horizontal pod autoscaler (HPA), and scaled object in real time. Open a new terminal and run this command:

```sh
watch -n 1 'kubectl get pods,hpa,scaledobject'
```

**Initial situation:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-11.png)

**3. Generate load manually:**

Execute the following command to send multiple requests to the service, simulating a basic load:

```sh
for i in {1..30}; do curl <load-balancer-address>; done
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-29.png)

After generating the load, wait for some time and monitor the watch terminal for the scaling. You will see hpa scale our deployment according to the load.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-30.png)

**Rescaling:**

When there is no load, it will automatically scale down to minimum replicas:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-14.png)

### **Conclusion**

This guide demonstrated how to set up autoscaling using **KEDA** and **Prometheus** to manage Kubernetes workloads dynamically. By leveraging custom metrics, we configured real-time scaling, monitored performance with Grafana, and validated the setup with load tests. This event-driven approach ensures efficient resource usage, scalability, and responsiveness, providing a foundation for optimizing Kubernetes applications.





























```sh
# First check raw counter
http_requests_total_with_path_total{url="/product"}

# Then check rate
rate(http_requests_total_with_path_total{url="/product"}[2m])

# Finally check sum
sum(rate(http_requests_total_with_path_total{url="/product"}[2m]))
```