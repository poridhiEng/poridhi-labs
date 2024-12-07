# Autoscaling with Keda and Prometheus Using Custom Metrics


Autoscaling with KEDA and Prometheus Using Custom Metrics
This documentation provides a step-by-step guide to implement autoscaling for Kubernetes pods using KEDA (Kubernetes Event-Driven Autoscaler), Prometheus, and custom metrics. The process includes creating a custom metric in Go, deploying the app on Kubernetes, configuring Prometheus for metrics scraping, and setting up Keda to enable autoscaling based on these metrics. By combining these tools, Kubernetes can scale workloads dynamically based on real-time metrics derived from the application.

<!-- ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/keda1.drawio.svg) -->

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/arch_final1.drawio.svg)

## Key Components Overview

**Prometheus**

Prometheus is an open-source monitoring and alerting toolkit designed for reliability and scalability. It uses a pull-based approach to scrape metrics from endpoints, storing them as time-series data. Prometheus is commonly integrated with Kubernetes for monitoring workloads and cluster health.

**KEDA**

KEDA is an open-source event-driven autoscaler that extends Kubernetes Horizontal Pod Autoscalers (HPA) by enabling scaling based on various custom metrics or external triggers. Examples include message queue length, database records, or Prometheus queries.

## Prerequirements

### **1. Install Go**

To install Go (Golang) on a Linux system, follow these steps:

**Update System Packages**

```bash
sudo apt update && sudo apt upgrade -y
```

**Download the Latest Go Package**

Visit the [Go Downloads page](https://go.dev/dl/) to check for the latest version. For example, to download version `1.21.0`:

```bash
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
```

**Extract the Go Package**

```bash
sudo tar -xvf go1.21.0.linux-amd64.tar.gz -C /usr/local
```

**Set Up Go Environment Variables**

```bash
echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.profile
source ~/.profile
```

**Verify the Installation**

Check the installed Go version to ensure it's working:

```bash
go version
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-1.png)

**2. Install helm**

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

```go
// main.go
package main

import (
    "log"
    "net/http"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

// Prometheus metrics
var (
    HttpRequestCountWithPath = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total_with_path",
            Help: "Number of HTTP requests by path.",
        },
        []string{"url"},
    )

    HttpRequestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "Response time of HTTP request.",
        },
        []string{"path"},
    )

    orderBooksCounter = prometheus.NewCounter(
        prometheus.CounterOpts{
            Name: "product_order_total",
            Help: "Total number of product orders",
        },
    )
)

func init() {
    // Register metrics with Prometheus
    prometheus.MustRegister(orderBooksCounter)
    prometheus.MustRegister(HttpRequestCountWithPath)
    prometheus.MustRegister(HttpRequestDuration)
}

func main() {
    // Setup routes
    http.HandleFunc("/product", orderHandler)
    http.Handle("/metrics", promhttp.Handler())

    log.Println("Starting server on :8181")
    log.Fatal(http.ListenAndServe(":8181", nil))
}

func orderHandler(w http.ResponseWriter, r *http.Request) {
    start := time.Now()
    
    // Increment metrics
    orderBooksCounter.Inc()
    HttpRequestCountWithPath.WithLabelValues(r.URL.Path).Inc()

    // Simulate some processing
    time.Sleep(100 * time.Millisecond)
    
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("Order placed!"))

    // Record request duration
    duration := time.Since(start).Seconds()
    HttpRequestDuration.WithLabelValues(r.URL.Path).Observe(duration)
}
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
FROM golang:1.22-alpine

WORKDIR /basics

COPY . .

RUN go build -o main .

CMD ["./main"]
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
  replicas: 2  # Starting with 2 replica
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
      containers:
      - name: goprometheus
        image: konami98/go_app_metrics:v1  # Replace with your image
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
  selector:
    app: goprometheus
  ports:
    - protocol: TCP
      port: 8181
      targetPort: 8181
  type: ClusterIP
```

**3. keda-scaledobject.yaml**

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: goprometheus-scaledobject
  namespace: default
spec:
  scaleTargetRef:
    name: goprometheus-deployment
  minReplicaCount: 1
  maxReplicaCount: 5
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

## Deploy the application in kubernetes

```sh
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f keda-scaledobject.yaml
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-8.png)


## Testing and Monitoring the setup

This section demonstrates how to test the service scaling and monitor its behavior using Kubernetes tools

**1. Port-forward service**

Check the services. Go application is deployed in the `default` namespace while Prometheus service is deployed in the `prometheus` namespace using helm.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-10.png)

Use the `kubectl port-forward` command to expose services locally for testing.

```sh
kubectl port-forward svc/goprometheus-service 8181:8181
kubectl port-forward svc/prometheus-server -n prometheus 9090:80
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-9.png)

**2. Monitor resource scaling:**

Use the watch command to observe the pods, horizontal pod autoscaler (HPA), and scaled object in real time. Open a new terminal and run this command:

```sh
# Monitor scaling
watch -n 1 'kubectl get pods,hpa,scaledobject'
```

**Initial situation:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-11.png)

**3. Generate load manually:**

Execute the following command to send multiple requests to the service, simulating a basic load:

```sh
for i in {1..30}; do curl http://localhost:8181/product; done
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-12.png)

After generating the load, wait for some time and monitor the watch terminal for the scaling. You will see hpa scale our deployment according to the load.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-13.png)

**Rescaling:**

When there is no load, it will automatically scale down to minimum replicas:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-14.png)

## Setting up Grafana for Visualization

Now we will set up Grafana and create dashboards to visualize the metrics. Grafana will use prometheus as data source and show the mertrices in the dashboard. Let's do this step by step.

**1. Install Grafana using Helm:**

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install grafana grafana/grafana -n monitoring --create-namespace
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-15.png)

**2. Expose the Grafana service using Nodeport:**

The Grafana service type will by default ClusterIP. We will convert it into NodePort service to access through `Poridhi's Loadbalancer`. 

```sh
helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --set service.type=NodePort \
  --set service.nodePort=30080
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-16.png)

<!-- **3. Port-forward the Grafana service:**

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80
``` -->

**3. Create a load-balancer to access Grafana.**

First get the MasterNode IP:

```sh
kubectl get nodes -o wide
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-17.png)


Create a load-balancer with the MasterNode IP and the NodePort of the Grafana service(`30080`):

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-18.png)


**5. Get the admin password to login into Grafana:**

```bash
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-19.png)

Use the password and login into Grafana.


## Configure Grafana Dashboard

Now, let's create a dashboard to monitor the metrics.

### **Configure the Prometheus data source:**

- In Grafana, go to Configuration → **`Data Sources`**
- Click "Add data source"
- Select "Prometheus"

  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-20.png)

- Set URL to: `http://prometheus-server.prometheus.svc.cluster.local`

  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-21.png)

- Click "Save & Test"

  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-22.png)

### **Build the dashboard:**

Now we will create a Grafana dashboard to monitor specific metrics. Each panel represents a specific metric visualization. Here's how to add them:

#### **(a) Request Rate Panel**

**1. Add Visualization:**

- Click on **"Add new panel"** to create a new visualization.
- Choose your **Prometheus data source** (configured earlier).

**2. **Query**: Use the PromQL query:**

```
rate(product_order_total[5m]) * 300
```
- This calculates the request rate over the past 5 minutes, scaled by a factor of 300.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-27.png)

**3. Customize Panel**:

- Title: **Request Rate**.
- Visualization Type: Select **Time series** to show a line chart over time.

**4. Save this panel.**

#### **(b) Active Pods Panel**

**1. Add another panel for tracking the number of active pods in your Kubernetes cluster.**

**2. Query**: Use this PromQL query:

```
count(kube_pod_status_ready{namespace="default", condition="true"})
```

- This counts all pods in the `default` namespace where the `condition` is `true` (ready state).

**3. Customize Panel**:

- Title: **Number of Pods**.
- Visualization Type: **Stat** (a single large number showing the current pod count).

**4. Save this panel.**

#### **(c) Response Time Panel**

**1. Add a third panel for monitoring average response time.**

**2. Query**: Use this PromQL query:

```
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```
- This divides the total request duration by the number of requests over the last 5 minutes, giving the average response time.

**3. Customize Panel**:

- Title: **Average Response Time**.
- Visualization Type: **Time series** (to track changes in response time over time).

**4. Save this panel.**

### **Configure Dashboard Settings**
Once all panels are added, configure the overall dashboard settings for optimal viewing.

**1. Access Settings**: Click the **gear icon** at the top right corner of the dashboard.

**2. Set Refresh Rate**: Configure the refresh rate to **5 seconds** for near real-time updates.

**3. Set Time Range**:

- Default to show data for the **last 30 minutes**.
- This can be changed in the time picker in the top-right corner.

**4. Save the Dashboard**: Click the **Save Dashboard** icon and name it **"Application Metrics"**.

Here is the Final Dashboard:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-23.png)

## Automated Load Testing with Python

Now we will test scaling of the application automatically. The `load_test.py` script creates a simulated workload for the service. It generates high, no-load, and medium load phases to test the system's responsiveness and scalability.


## load_test.py

```py
import requests
import time
import threading
from datetime import datetime

def send_requests(duration_seconds, requests_per_second):
    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        try:
            response = requests.get('http://localhost:8181/product')
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        
        # Sleep for 1/requests_per_second seconds
        time.sleep(1.0 / requests_per_second)

def main():
    print("Starting load test...")
    print("Phase 1: High load (30 seconds)")
    send_requests(30, 5)  # 5 requests per second for 30 seconds
    
    print("\nPhase 2: No load (60 seconds)")
    time.sleep(60)  # Wait for 60 seconds with no load
    
    print("\nPhase 3: Medium load (30 seconds)")
    send_requests(30, 2)  # 2 requests per second for 30 seconds
    
    print("\nLoad test completed")

if __name__ == "__main__":
    main()
```


### Test the visualization:

**1. Run the load test script from earlier:**

```bash
python load_test.py
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-24.png)

> Make Sure you have Port-forwarded the Go application Service.

**2. Watch the Grafana dashboard to see:**

- Request rate increasing during high load
- Number of pods scaling up and down
- Response time variations

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-25.png)

During the normal load condition, the deployment will be scale down to minimum replicas:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Autoscaling%20with%20Keda%20in%20Kubernetes/images/image-26.png)


### **Conclusion**

This guide demonstrated how to set up autoscaling using **KEDA** and **Prometheus** to manage Kubernetes workloads dynamically. By leveraging custom metrics, we configured real-time scaling, monitored performance with Grafana, and validated the setup with load tests. This event-driven approach ensures efficient resource usage, scalability, and responsiveness, providing a foundation for optimizing Kubernetes applications.









