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


## Python Application: Exposing Custom Metrics

The following Go application exposes custom Prometheus metrics:

```python
from flask import Flask, request, Response
from prometheus_client import Counter, Histogram, generate_latest
import time

app = Flask(__name__)

# Counter for all HTTP requests
total_http_requests = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint']
)

@app.route('/')
def roor_route():
    total_http_requests.labels(method=request.method, endpoint='/').inc()
    return "Welcome", 200

@app.route('/product')
def order_handler():
    total_http_requests.labels(method=request.method, endpoint='/product').inc()
    return "Order placed!", 200

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

if __name__ == '__main__':
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
  name: pyprometheus-deployment
  labels:
    app: pyprometheus
spec:
  replicas: 2  # Running one pod on each worker node
  selector:
    matchLabels:
      app: pyprometheus
  template:
    metadata:
      labels:
        app: pyprometheus
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8181"
        prometheus.io/path: "/metrics"
    spec:
      nodeSelector:
        role: worker-node
      containers:
      - name: pyprometheus
        image: <DOCKERHUB_USERNAME>/<IMAGE_NAME>:<VERSION>
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
  name: pyprometheus-service
spec:
  type: NodePort
  selector:
    app: pyprometheus
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
  name: pyprometheus-scaledobject
spec:
  scaleTargetRef:
    name: pyprometheus-deployment
  minReplicaCount: 2
  maxReplicaCount: 6
  cooldownPeriod: 10
  pollingInterval: 5
  advanced:
    horizontalPodAutoscalerConfig:
      behavior:
        scaleDown:
          stabilizationWindowSeconds: 10
          policies:
          - type: Pods
            value: 1
            periodSeconds: 10
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus-server.prometheus.svc.cluster.local:80
      metricName: request_count
      threshold: '50'  # Scale when total requests exceed 50 in last 30s
      query: |
        sum(increase(http_requests_total{endpoint=~".*"}[30s])) or vector(0)
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
  - job_name: 'pyprometheus'
    scrape_interval: 15s
    static_configs:
      - targets: ['pyprometheus-service.default.svc.cluster.local:8181']
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

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/KEDA%20with%20python/images/image-8.png)


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

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/KEDA%20with%20python/images/image-1.png)

**3. Generate load manually:**

Execute the following command to send multiple requests to the service, simulating a basic load:

```sh
for i in {1..50}; do curl <load-balancer-address>; done
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/KEDA%20with%20python/images/image-3.png)

After generating the load, wait for some time and monitor the watch terminal for the scaling. You will see hpa scale our deployment according to the load.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/KEDA%20with%20python/images/image-2.png)

**Rescaling:**

When there is no load, it will automatically scale down to minimum replicas:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/KEDA%20with%20python/images/image.png)


**Prometheuse Dashboard**

First access the Prometheus UI by creating a loadbalancer stated previously. Then you can test the queries in the Prometheus UI:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/KEDA%20with%20python/images/image-5.png)

Total httl request count:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/KEDA%20with%20python/images/image-7.png)

### **Conclusion**

This guide demonstrated how to set up autoscaling using **KEDA** and **Prometheus** to manage Kubernetes workloads dynamically. By leveraging custom metrics, we configured real-time scaling, monitored performance with Grafana, and validated the setup with load tests. This event-driven approach ensures efficient resource usage, scalability, and responsiveness, providing a foundation for optimizing Kubernetes applications.