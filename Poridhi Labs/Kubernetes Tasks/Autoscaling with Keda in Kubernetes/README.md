# Autoscaling with Keda and Prometheus Using Custom Metrics

This documentation explains how to autoscale Kubernetes pods based on custom Prometheus metrics using Keda (Kubernetes Event-Driven Autoscaler). The process includes creating a custom metric in Go, deploying the app on Kubernetes, configuring Prometheus for metrics scraping, and setting up Keda to enable autoscaling based on these metrics.

![](./images/auto.drawio.svg)

## Key Components Overview

**Prometheus**

Prometheus is an open-source monitoring and alerting toolkit. It collects and stores metrics as time series data, characterized by a metric name, timestamp, and optional key-value pairs called labels. It’s widely used for Kubernetes monitoring because of its efficient scraping and querying mechanisms.

**Keda**

Keda is an event-driven autoscaler for Kubernetes that scales workloads based on custom metrics or events like queue length, message rates, or Prometheus queries.

## Requirements

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

---

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

## Go application

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

## Dockerfile

```Dockerfile
FROM golang:1.22-alpine

WORKDIR /basics

COPY . .

RUN go build -o main .

CMD ["./main"]
```


##  kubernetes/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: goprometheus-deployment
  labels:
    app: goprometheus
spec:
  replicas: 1  # Starting with 1 replica
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

## kubernetes/service.yaml
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

## kubernetes/keda-scaledobject.yaml
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

## prometheus-values.yaml
```yaml
extraScrapeConfigs: |
  - job_name: 'goprometheus'
    scrape_interval: 15s
    static_configs:
      - targets: ['goprometheus-service.default.svc.cluster.local:8181']
```

## helm installations

```sh
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash

# Install Prometheus using Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus -n prometheus --create-namespace

# Install KEDA
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace
```


## Build and deploy

```sh
# Build and push the Docker image
docker build -t your-registry/goprometheuskeda:v1 .
docker push your-registry/goprometheuskeda:v1

# Update Prometheus configuration
helm upgrade --install prometheus prometheus-community/prometheus -f prometheus-values.yaml -n prometheus

# Deploy the application
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/keda-scaledobject.yaml
```


## test

```sh
# Port forward the service
kubectl port-forward svc/goprometheus-service 8181:8181

kubectl port-forward svc/prometheus-server -n prometheus 9090:80

# Generate load
for i in {1..30}; do curl http://localhost:8181/product; done

# Monitor scaling
watch -n 1 'kubectl get pods,hpa,scaledobject'
```


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


I'll help you set up Grafana and create dashboards to visualize the metrics. Let's do this step by step.

1. First, let's install Grafana using Helm:

```bash
# Add Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Grafana
helm install grafana grafana/grafana -n monitoring --create-namespace
```

2. Get the admin password:
```bash
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

3. Access Grafana:
```bash
kubectl port-forward svc/grafana -n monitoring 3000:80
```
Then visit: http://localhost:3000 (login with admin and the password from step 2)

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

1. First, configure the Prometheus data source:
   - In Grafana, go to Configuration → Data Sources
   - Click "Add data source"
   - Select "Prometheus"
   - Set URL to: `http://prometheus-server.prometheus.svc.cluster.local`
   - Click "Save & Test"

2. Import the dashboard:
   - Go to Create → Import
   - Paste the JSON configuration above
   - Click "Load"
   - Select your Prometheus data source
   - Click "Import"

3. The dashboard includes:
   - Request rate graph (shows requests per 5 minutes)
   - Number of active pods
   - Average response time

To test the visualization:

1. Run the load test script from earlier:
```bash
python load_test.py
```

2. Watch the Grafana dashboard (http://localhost:3000) to see:
   - Request rate increasing during high load
   - Number of pods scaling up and down
   - Response time variations

You can modify the dashboard by:
- Adjusting time ranges
- Adding more metrics
- Creating alerts based on thresholds
- Customizing visualization styles



## nodeport

```sh
helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --set service.type=NodePort \
  --set service.nodePort=30080
```









