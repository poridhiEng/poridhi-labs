# Kubernetes Monitoring Project - Complete Documentation

## Project Overview
This project implements a comprehensive monitoring solution for a K3s Kubernetes cluster using Prometheus, Grafana, Blackbox Exporter, and a sample Go application.

## Prerequisites
- K3s cluster up and running
- kubectl configured
- Helm v3
- Docker for building the sample application

## Directory Structure
```
projects/
├── blackbox-exporter/
│   ├── 0-deployment.yaml
│   └── 1-service.yaml
├── grafana-values.yaml
├── myapp/
│   ├── deploy/
│   │   ├── 0-namespace.yaml
│   │   ├── 1-deployment.yaml
│   │   ├── 2-service.yaml
│   │   ├── 3-pod-monitor.yaml
│   │   ├── 4-prom-service.yaml
│   │   └── 5-service-monitor.yaml
│   ├── Dockerfile
│   ├── main.go
│   ├── go.mod
│   └── go.sum
├── probe.yaml
├── prometheus/
│   ├── 0-service-account.yaml
│   ├── 1-cluster-role.yaml
│   ├── 2-cluster-role-binding.yaml
│   └── 3-prometheus.yaml
└── prometheus-operator/
    └── deployment/
        ├── 0-service-account.yaml
        └── 1-cluster-role.yaml
```

## Installation Steps

### 1. Create Monitoring Namespace
```bash
kubectl create namespace monitoring
```

### 2. Deploy Prometheus Operator
```bash
kubectl apply -f projects/prometheus-operator/deployment/0-service-account.yaml
kubectl apply -f projects/prometheus-operator/deployment/1-cluster-role.yaml
```

### 3. Deploy Prometheus
```bash
kubectl apply -f projects/prometheus/0-service-account.yaml
kubectl apply -f projects/prometheus/1-cluster-role.yaml
kubectl apply -f projects/prometheus/2-cluster-role-binding.yaml
kubectl apply -f projects/prometheus/3-prometheus.yaml
```

### 4. Deploy Blackbox Exporter
```bash
kubectl apply -f projects/blackbox-exporter/0-deployment.yaml
kubectl apply -f projects/blackbox-exporter/1-service.yaml
```

### 5. Deploy Sample Application
```bash
# Build the application
docker build -t myapp:latest projects/myapp/
# If using a local registry or k3d registry
docker tag myapp:latest localhost:5000/myapp:latest
docker push localhost:5000/myapp:latest

# Deploy to Kubernetes
kubectl apply -f projects/myapp/deploy/
```

### 6. Install Grafana
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install grafana grafana/grafana \
  --namespace monitoring \
  --values projects/grafana-values.yaml
```

## Accessing Services

### Prometheus
```bash
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
```
Access at: http://localhost:9090

### Grafana
```bash
# Get admin password
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

# Port forward
kubectl port-forward -n monitoring svc/grafana 3000:80
```
Access at: http://localhost:3000

### Sample Application
```bash
kubectl port-forward -n staging svc/myapp 8080:8080
kubectl port-forward -n staging svc/myapp-prom 8081:8081
```
- Application: http://localhost:8080/api/devices
- Metrics: http://localhost:8081/metrics

## Verification Steps

1. Check all pods are running:
```bash
kubectl get pods -n monitoring
kubectl get pods -n staging
```

2. Verify Prometheus targets:
```bash
# Access Prometheus UI and check Status -> Targets
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
```

3. Test sample application:
```bash
curl http://localhost:8080/api/devices
```

4. Check metrics:
```bash
curl http://localhost:8081/metrics
```

## Monitoring Configuration

### Key Metrics to Watch
- HTTP request duration
- Error rates
- Resource usage (CPU/Memory)
- Endpoint availability

### Grafana Dashboards
After logging into Grafana:
1. Add Prometheus data source
   - URL: http://prometheus-operated:9090
2. Import basic dashboards:
   - Node Exporter Dashboard (ID: 1860)
   - Kubernetes cluster monitoring (ID: 315)

## Troubleshooting

### Common Issues and Solutions

1. Pods not starting:
```bash
kubectl describe pod -n monitoring <pod-name>
kubectl logs -n monitoring <pod-name>
```

2. Prometheus not finding targets:
```bash
# Check ServiceMonitor/PodMonitor
kubectl get servicemonitor -n monitoring
kubectl get podmonitor -n monitoring

# Check labels match
kubectl get pods -n staging --show-labels
```

3. Metrics not showing up:
```bash
# Check metrics endpoint directly
kubectl port-forward -n staging <pod-name> 8081:8081
curl localhost:8081/metrics
```

## Cleanup

```bash
# Remove sample application
kubectl delete -f projects/myapp/deploy/

# Remove monitoring components
kubectl delete -f projects/prometheus/
kubectl delete -f projects/blackbox-exporter/

# Remove Grafana
helm uninstall grafana -n monitoring

# Remove namespaces
kubectl delete namespace monitoring
kubectl delete namespace staging
```

## Best Practices

1. Resource Management
   - Always set resource requests and limits
   - Monitor resource usage and adjust as needed

2. Security
   - Use RBAC appropriately
   - Keep monitoring components in dedicated namespace
   - Regularly update components

3. Monitoring
   - Set up relevant alerts
   - Keep retention period appropriate to cluster size
   - Regular backup of Grafana dashboards

4. Performance
   - Adjust scrape intervals based on needs
   - Use appropriate retention periods
   - Consider using recording rules for complex queries

This documentation provides a complete reference for setting up and managing the monitoring infrastructure on a K3s cluster. For additional customization or configuration options, refer to the official documentation of each component.
