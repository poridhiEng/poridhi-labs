# Autoscaling with Keda and Prometheus Using Custom Metrics


Autoscaling with KEDA and Prometheus Using Custom Metrics
This documentation provides a step-by-step guide to implement autoscaling for Kubernetes pods using KEDA (Kubernetes Event-Driven Autoscaler), Prometheus, and custom metrics. The process includes creating a custom metric in Go, deploying the app on Kubernetes, configuring Prometheus for metrics scraping, and setting up Keda to enable autoscaling based on these metrics. By combining these tools, Kubernetes can scale workloads dynamically based on real-time metrics derived from the application.

![](./images/keda1.drawio.svg)

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

1. Visit the [Go Downloads page](https://go.dev/dl/) to check for the latest version.

2. Use `wget` to download the Go tarball. For example, to download version `1.21.0`:

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

**2. Install helm**

Make sure you have helm installed on you machine or you can install this using the following command:

```sh
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

Check the helm version

```sh
helm version
```

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

![alt text](image.png)


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
  replicas: 2 # Starting with 2 replica
  selector:
    matchLabe ls:
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
        image: your-registry/goprometheuskeda:v1  # Replace with your image
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

**4. prometheus-values.yaml**

```yaml
extraScrapeConfigs: |
  - job_name: 'goprometheus'
    scrape_interval: 15s
    static_configs:
      - targets: ['goprometheus-service.default.svc.cluster.local:8181']
```

## Helm installations and Upgrade

**1. Install Prometheus**

```sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus -n prometheus --create-namespace
```

**2. Install KEDA**

```sh
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace
```


### Update the Prometheus Configuration

```sh
helm upgrade --install prometheus prometheus-community/prometheus -f prometheus-values.yaml -n prometheus
```

## Deploy the application in kubernetes

```sh
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f keda-scaledobject.yaml
```


## Testing and Monitoring the setup

This section demonstrates how to test the service scaling and monitor its behavior using Kubernetes tools

**1. Port-forward service**

Use the `kubectl port-forward` command to expose services locally for testing.

```sh
kubectl port-forward svc/goprometheus-service 8181:8181
kubectl port-forward svc/prometheus-server -n prometheus 9090:80
```

2. Generate load manually:

Execute the following command to send multiple requests to the service, simulating a basic load: 
```sh
# Generate load
for i in {1..30}; do curl http://localhost:8181/product; done
```

3. Monitor resource scaling:

Use the watch command to observe the pods, horizontal pod autoscaler (HPA), and scaled object in real time.

```sh
# Monitor scaling
watch -n 1 'kubectl get pods,hpa,scaledobject'
```


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

Run the script using Python:

```sh
python load_test.py
```

## Setting up Grafana for Visualization

Now we will set up Grafana and create dashboards to visualize the metrics. Let's do this step by step.

**1. First, let's install Grafana using Helm:**

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install grafana grafana/grafana -n monitoring --create-namespace
```

2. Expose the Grafana service using Nodeport:

```sh
helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --set service.type=NodePort \
  --set service.nodePort=30080
```

<!-- **3. Port-forward the Grafana service:**

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80
``` -->

**4. Create a load-balancer to access Grafana.**



**5. Get the admin password to login into Grafana:**

```bash
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```


## Create a Grafana Dashboard

Now, let's create a dashboard to monitor our metrics. Here's the dashboard configuration:

```json
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 20,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "smooth",
            "lineWidth": 2,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "editorMode": "code",
          "expr": "rate(product_order_total[5m]) * 300",
          "legendFormat": "Requests per 5m",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Request Rate",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 2,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "pluginVersion": "10.0.0",
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "editorMode": "code",
          "expr": "count(kube_pod_status_ready{namespace=\"default\", condition=\"true\"})",
          "legendFormat": "Active Pods",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Number of Pods",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 20,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "smooth",
            "lineWidth": 2,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "s"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 24,
        "x": 0,
        "y": 8
      },
      "id": 3,
      "options": {
        "legend": {
          "calcs": [
            "mean",
            "max"
          ],
          "displayMode": "table",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "editorMode": "code",
          "expr": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])",
          "legendFormat": "Response Time",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Average Response Time",
      "type": "timeseries"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-30m",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Application Metrics",
  "uid": "application-metrics",
  "version": 1,
  "weekStart": ""
}

```

To set up the dashboard:

**1. First, configure the Prometheus data source:**

- In Grafana, go to Configuration → Data Sources
- Click "Add data source"
- Select "Prometheus"
- Set URL to: `http://prometheus-server.prometheus.svc.cluster.local`
- Click "Save & Test"

**2. Import the dashboard:**

- Go to Create → Import
- Paste the JSON configuration above
- Click "Load"
- Select your Prometheus data source
- Click "Import"

**3. The dashboard includes:**

- Request rate graph (shows requests per 5 minutes)
- Number of active pods
- Average response time


### Test the visualization:

**1. Run the load test script from earlier:**

```bash
python load_test.py
```

**2. Watch the Grafana dashboard to see:**

- Request rate increasing during high load
- Number of pods scaling up and down
- Response time variations

**You can modify the dashboard by:**

- Adjusting time ranges
- Adding more metrics
- Creating alerts based on thresholds
- Customizing visualization styles


### **Conclusion**

This guide demonstrated how to set up autoscaling using **KEDA** and **Prometheus** to manage Kubernetes workloads dynamically. By leveraging custom metrics, we configured real-time scaling, monitored performance with Grafana, and validated the setup with load tests. This event-driven approach ensures efficient resource usage, scalability, and responsiveness, providing a foundation for optimizing Kubernetes applications.









