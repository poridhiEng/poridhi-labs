# Prometheus Operator Kubernetes Tutorial: ServiceMonitor and PodMonitor Step-by-Step Guide

This document provides a simplified step-by-step guide for setting up Prometheus Operator in Kubernetes. It includes the setup of `ServiceMonitor` and `PodMonitor` objects for monitoring, deploying Grafana for visualisation, and using Blackbox Exporter to monitor external targets. It excludes EKS, Terraform, and alert-related configurations.

---

## Overview

Prometheus Operator is a standard tool for deploying and managing Prometheus instances in Kubernetes. This guide helps clarify the setup of monitoring configurations, particularly focusing on the use of `ServiceMonitor` and `PodMonitor`.

---

## Steps to Set Up Prometheus Operator and Monitoring in Kubernetes

### 1. **Deploy Prometheus Operator**
   - Create a dedicated **monitoring namespace** to house all monitoring components.
   - Label the namespace with `monitoring=prometheus`, as this is crucial for Prometheus Operator to discover related objects such as `ServiceMonitor` and `PodMonitor`.

### 2. **Apply Custom Resource Definitions (CRDs)**
   - Apply the necessary CRDs for Prometheus Operator. These include definitions for objects like `ServiceMonitor`, `PodMonitor`, and other custom configurations.
   - Use Kubernetes secrets for sensitive configurations, such as additional scrape configurations.

### 3. **Deploy Prometheus**
   - Create a custom resource (CR) for Prometheus using the Prometheus Operator.
   - Configure key parameters such as:
     - Namespace and label selectors for `ServiceMonitor` and `PodMonitor`.
     - Retention settings (default is 7 days, but you can adjust as needed).
     - Resource requests and limits for Prometheus pods.

   - Ensure the Prometheus pods are running and that the service is exposed using port forwarding or Ingress.

---

## Steps for Monitoring with PodMonitor and ServiceMonitor

### 4. **Set Up a PodMonitor**
   - Deploy an application that exposes metrics, such as a sample app with Prometheus metrics endpoints.
   - Create a `PodMonitor` object:
     - Use label selectors to target the pods you want to monitor (e.g., `app=my-app`).
     - Specify the metrics endpoint exposed by the application.
     - Ensure the `PodMonitor` object has the same label as the Prometheus instance (e.g., `prometheus=main`).

   - Verify in the Prometheus UI that the new target is discovered and metrics are being scraped.

### 5. **Set Up a ServiceMonitor**
   - Create a Kubernetes Service for the application that exposes the Prometheus metrics endpoint.
   - Create a `ServiceMonitor` object:
     - Use label selectors to target the service you created.
     - Specify the endpoint and port name of the metrics endpoint.

   - Ensure that the `ServiceMonitor` object matches the labels defined in the Prometheus custom resource for service discovery.

   - Check the Prometheus UI for the new target with the `ServiceMonitor` configuration.

---

## Deploying Grafana for Visualisation

### 6. **Deploy Grafana**
   - Use a Helm chart to deploy Grafana in Kubernetes. Ensure you have a persistent volume to store Grafana dashboards and configurations.
   - Expose Grafana using a Service or Ingress, depending on your setup.

### 7. **Configure Prometheus as a Data Source**
   - Log into Grafana using the default admin credentials or a custom one you configured.
   - Add Prometheus as a data source:
     - Use the URL of the Prometheus service exposed in your cluster (default port is `9090`).
     - Test the data source to ensure it is connected correctly.

### 8. **Create Dashboards in Grafana**
   - Create a new dashboard in Grafana to visualise the metrics collected by Prometheus.
   - Use example metrics such as:
     - `container_cpu_usage_seconds_total` for CPU usage.
     - `container_memory_usage_bytes` for memory usage.
     - Apply rate or aggregation functions to make the graphs more meaningful.
   - Customise the dashboard by adjusting legends, colours, and time intervals.

---

## Monitoring External Targets Using Blackbox Exporter

### 9. **Deploy Blackbox Exporter**
   - Deploy Blackbox Exporter in Kubernetes to monitor external services like websites or APIs.
   - Expose Blackbox Exporter using a Service.

### 10. **Configure Blackbox Exporter with Prometheus**
   - Create a `Service` for Blackbox Exporter to expose its endpoints.
   - Add a `Probe` custom resource to monitor external targets:
     - Define the target URL (e.g., a website URL).
     - Set the desired parameters such as HTTP status code and response time.
   - Update the Prometheus configuration to include the `Probe` resource.

### 11. **Verify Monitoring of External Targets**
   - Check the Prometheus UI for new targets created by the `Probe` custom resource.
   - Ensure that metrics such as `probe_http_status_code` and `probe_duration_seconds` are being collected.

---

## Summary
By following these steps, you can:
- Deploy Prometheus Operator and configure it for monitoring Kubernetes workloads using `PodMonitor` and `ServiceMonitor`.
- Visualise metrics with Grafana dashboards.
- Monitor external services using Blackbox Exporter and `Probe` resources.
















kubectl apply -f prometheus-operator/namespace.yaml


kubectl apply -f --server-side -f prometheus-operator/crds

kubectl get crd

kubectl apply -f prometheus-operator/deployment


kubectl get pods -n monitoring

kubectl apply -f prometheus

kubectl get pods -n monitoring  [check operator pod is running]

kubectl get service -n monitoring

kubectl port-forward  svc/prometheus-operated 9090 -n monitoring

Now access prometheus ui

kubectl apply -f myapp/deploy/4-prom-service.yaml

kubectl get endpoints -n staging


kubectl apply -f prometheus/3-prometheus.yaml  []

kubectl get pods -n monitoring

kubectl get service -n monitoring

kubectl port-forward  svc/prometheus-operated 9090 -n monitoring

Now access prometheus ui

 

