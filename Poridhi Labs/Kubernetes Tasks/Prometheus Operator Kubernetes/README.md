# Kubernetes Monitoring Project - Complete Documentation

## Project Overview
This project implements a comprehensive monitoring solution for a K3s Kubernetes cluster using Prometheus, Grafana, Blackbox Exporter, and a sample Go application.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/Prometheus-operator-2.drawio.svg)

## Prerequisites
- kubernetes cluster up and running
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




