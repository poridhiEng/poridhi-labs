# Prometheus Operators

This lab provides a simplified step-by-step guide for setting up Prometheus Operator in Kubernetes. It includes the setup of `ServiceMonitor` and `PodMonitor` objects for monitoring, deploying Grafana for visualisation.

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

## Step-by-Step Instructions

First clone this repository to get all the files required for this project

```sh
git clone https://github.com/Galadon123/Prometheus-Operator-.git
```
## **1. Deploy Prometheus Operator**

- Create a dedicated **monitoring namespace** to house all monitoring components.
- Label the namespace with `monitoring=prometheus`, as this is crucial for Prometheus Operator to discover related objects such as `ServiceMonitor` and `PodMonitor`.


```bash
kubectl apply -f prometheus-operator/namespace.yaml
```

**2. Apply Custom Resource Definitions (CRDs)**

- Apply the necessary CRDs for Prometheus Operator. These include definitions for objects like `ServiceMonitor`, `PodMonitor`, and other custom configurations.
- Use Kubernetes secrets for sensitive configurations, such as additional scrape configurations.

```sh
kubectl apply --server-side -f prometheus-operator/crds
```

**3. Apply RBAC Policy**

```sh
kubectl apply -f prometheus-operator/rbac
```

**4. Deploy Prometheus**

- Create a custom resource (CR) for Prometheus using the Prometheus Operator.
- Configure key parameters such as:
    - Namespace and label selectors for `ServiceMonitor` and `PodMonitor`.
    - Retention settings (default is 3 days, but you can adjust as needed).
    - Resource requests and limits for Prometheus pods.

- Ensure the Prometheus pods are running and that the service is exposed using port forwarding or Ingress.

```sh
kubectl apply -f prometheus-operator/deployment
```

Check if pods are running or not:

```sh
kubectl get pods -n monitoring
```

You might check the logs of the pod for any misconfiguration.

**5. Set Up a PodMonitor**

- Deploy an application that exposes metrics, such as a sample app with Prometheus metrics endpoints.
- Create a `PodMonitor` object:
    - Use label selectors to target the pods you want to monitor (e.g., `app=my-app`).
    - Specify the metrics endpoint exposed by the application.
    - Ensure the `PodMonitor` object has the same label as the Prometheus instance (e.g., `prometheus=main`).

- Verify in the Prometheus UI that the new target is discovered and metrics are being scraped.

- To access the Prometheus UI you can port-forward the prometheus service and access using the the loadbalancer URL:

```sh
kubectl port-forward svc/prometheus-operated 9090 -n monitoring
```


![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-2.png)

```sh
kubectl apply -f prometheus
```

**6. Set Up a ServiceMonitor**

- Create a Kubernetes Service for the application that exposes the Prometheus metrics endpoint.
- Create a `ServiceMonitor` object:

    - Use label selectors to target the service you created.
    - Specify the endpoint and port name of the metrics endpoint.

- Ensure that the `ServiceMonitor` object matches the labels defined in the Prometheus custom resource for service discovery.

- Check the Prometheus UI for the new target with the `ServiceMonitor` configuration.

**7. Deploy the Go application**

```sh
kubectl apply -f myapp/deploy
```

**8. Deploy Grafana**

Create a Kubernetes deployment for Grafana using the Prometheus Operator. Make sure you have helm installed on you machine or you can install this using the following command:

```sh
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

Update the Kubeconfig file permission:

```sh
kubectl config view --raw > /root/.kube/config
chmod 600 /root/.kube/config
```


```sh
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install grafana grafana/grafana -n monitoring --create-namespace
```

The Grafana service type will by default ClusterIP. We will convert it into NodePort service to access through Poridhi's Loadbalancer.

```sh
helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --set service.type=NodePort \
  --set service.nodePort=30080
```

Create a load balancer with the MasterNode IP and the Nodeport (30080). Then access the Grafana UI using the loadbalancer URL.

**9. Configure Prometheus as a Data Source**

- Log into Grafana using the default admin credentials or a custom one you configured.
- Add Prometheus as a data source:
    - Use the URL of the Prometheus service exposed in your cluster (default port is `9090`).
    - Test the data source to ensure it is connected correctly.


**9. Create Dashboards in Grafana**

   - Create a new dashboard in Grafana to visualise the metrics collected by Prometheus.
   - Use example metrics such as:
     - `container_cpu_usage_seconds_total` for CPU usage.
     - `container_memory_usage_bytes` for memory usage.
     - Apply rate or aggregation functions to make the graphs more meaningful.
   - Customise the dashboard by adjusting legends, colours, and time intervals.


   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image.png)


## Conclusion
Following these steps will set up a fully functional monitoring stack in your Kubernetes cluster. If you encounter any issues, check the logs for the respective pods to troubleshoot.






