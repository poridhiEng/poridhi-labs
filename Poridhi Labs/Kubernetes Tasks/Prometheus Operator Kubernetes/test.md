# **Prometheus Operator Kubernetes**

The **Prometheus Operator** is the de-facto standard for deploying and managing Prometheus instances in Kubernetes. It simplifies configurations, automates target discovery, and manages the lifecycle of Prometheus and Alertmanager. This tutorial covers:

- Deploying Prometheus Operator in Kubernetes
- Configuring **ServiceMonitor** and **PodMonitor**
- Using **Blackbox Exporter** for monitoring websites
- Sending alerts via **Slack**

---

## **1. Pre-requisites**
Before starting, ensure you have:
- A Kubernetes cluster (EKS, GKE, or local Minikube).
- kubectl and helm installed on your system.
- Terraform (optional) for automating infrastructure setup.

---

## **2. Kubernetes Cluster Setup (Optional: Using Terraform)**

### Create EKS Cluster with Terraform
1. Initialise Terraform:
   ```bash
   terraform init
   ```

2. Create an EKS cluster:
   ```bash
   terraform apply
   ```

3. Update kubeconfig:
   ```bash
   aws eks update-kubeconfig --name <cluster-name> --region <region>
   ```

4. Verify access to the cluster:
   ```bash
   kubectl get services
   ```

---

## **3. Deploy Prometheus Operator**

### **Step 1: Create a Namespace**
The Prometheus Operator requires a dedicated namespace:
```bash
kubectl create namespace monitoring
kubectl label namespace monitoring monitoring=prometheus
```

---

### **Step 2: Deploy Prometheus Operator**
1. Clone the Prometheus Operator repository:
   ```bash
   git clone https://github.com/prometheus-operator/prometheus-operator.git
   cd prometheus-operator
   ```

2. Apply Custom Resource Definitions (CRDs):
   ```bash
   kubectl apply -f bundle.yaml
   ```

3. Deploy the Prometheus Operator:
   ```bash
   kubectl apply -f example/prometheus-operator-crd/
   ```

---

### **Step 3: Deploy Prometheus Instance**

#### Create a Prometheus Custom Resource (CR):
Save the following YAML as `prometheus.yaml`:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
  namespace: monitoring
spec:
  serviceAccountName: prometheus
  retention: 7d
  serviceMonitorSelector:
    matchLabels:
      monitoring: prometheus
```

Apply the configuration:
```bash
kubectl apply -f prometheus.yaml
```

---

## **4. Monitor Kubernetes Applications**

### **PodMonitor Example**
#### Deploy a Sample Application:
1. Create a sample deployment with Prometheus metrics exposed:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: sample-app
     namespace: monitoring
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: sample-app
     template:
       metadata:
         labels:
           app: sample-app
       spec:
         containers:
           - name: sample-app
             image: prom/prometheus-example-app
             ports:
               - containerPort: 8080
   ```

2. Apply the deployment:
   ```bash
   kubectl apply -f sample-deployment.yaml
   ```

#### Create a PodMonitor:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: sample-app-pod-monitor
  namespace: monitoring
  labels:
    monitoring: prometheus
spec:
  selector:
    matchLabels:
      app: sample-app
  namespaceSelector:
    matchNames:
      - monitoring
  podMetricsEndpoints:
    - port: metrics
```

Apply the configuration:
```bash
kubectl apply -f pod-monitor.yaml
```

---

### **ServiceMonitor Example**
1. Expose the application with a Kubernetes service:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: sample-app-service
     namespace: monitoring
   spec:
     selector:
       app: sample-app
     ports:
       - name: metrics
         port: 8080
   ```

   Apply the configuration:
   ```bash
   kubectl apply -f service.yaml
   ```

2. Create a ServiceMonitor:
   ```yaml
   apiVersion: monitoring.coreos.com/v1
   kind: ServiceMonitor
   metadata:
     name: sample-app-service-monitor
     namespace: monitoring
     labels:
       monitoring: prometheus
   spec:
     selector:
       matchLabels:
         app: sample-app
     namespaceSelector:
       matchNames:
         - monitoring
     endpoints:
       - port: metrics
   ```

   Apply the configuration:
   ```bash
   kubectl apply -f service-monitor.yaml
   ```

---

## **5. Add External Targets**

### Monitor External Nodes with Node Exporter
1. Install Node Exporter on a VM:
   ```bash
   wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-*.linux-amd64.tar.gz
   tar xvfz node_exporter-*.linux-amd64.tar.gz
   ./node_exporter
   ```

2. Add a scrape job to Prometheus:
   Update `prometheus.yaml`:
   ```yaml
   scrape_configs:
     - job_name: 'external-node'
       static_configs:
         - targets: ['<node-ip>:9100']
   ```

   Apply the configuration:
   ```bash
   kubectl delete pod -l app=prometheus
   ```

---

## **6. Deploy Blackbox Exporter**

### **Deploy Blackbox Exporter**
1. Create a deployment for Blackbox Exporter:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: blackbox-exporter
     namespace: monitoring
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: blackbox-exporter
     template:
       metadata:
         labels:
           app: blackbox-exporter
       spec:
         containers:
           - name: blackbox-exporter
             image: prom/blackbox-exporter
             ports:
               - containerPort: 9115
   ```

2. Expose the exporter with a service:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: blackbox-exporter
     namespace: monitoring
   spec:
     selector:
       app: blackbox-exporter
     ports:
       - port: 9115
   ```

3. Create a Probe resource:
   ```yaml
   apiVersion: monitoring.coreos.com/v1
   kind: Probe
   metadata:
     name: website-probe
     namespace: monitoring
   spec:
     jobName: website
     prober:
       url: blackbox-exporter.monitoring:9115
     targets:
       staticConfig:
         static:
           - https://example.com
   ```

   Apply all configurations:
   ```bash
   kubectl apply -f blackbox-exporter-deployment.yaml
   kubectl apply -f blackbox-exporter-service.yaml
   kubectl apply -f probe.yaml
   ```

---

## **7. Alerting with Alertmanager**

### Deploy Alertmanager:
1. Create an Alertmanager resource:
   ```yaml
   apiVersion: monitoring.coreos.com/v1
   kind: Alertmanager
   metadata:
     name: alertmanager
     namespace: monitoring
   spec:
     replicas: 1
   ```

2. Configure Slack alerts:
   Create a secret with Alertmanager configuration:
   ```yaml
   global:
     slack_api_url: 'https://hooks.slack.com/services/<your-slack-webhook>'
   route:
     group_by: ['alertname']
     receiver: 'slack'
   receivers:
     - name: 'slack'
       slack_configs:
         - channel: '#alerts'
   ```

   Apply the secret:
   ```bash
   kubectl create secret generic alertmanager-config --from-file=alertmanager.yaml
   ```

3. Link Alertmanager to Prometheus:
   Update the Prometheus resource to include Alertmanager:
   ```yaml
   alerting:
     alertmanagers:
       - namespace: monitoring
         name: alertmanager
         port: web
   ```

   Apply the changes:
   ```bash
   kubectl apply -f prometheus.yaml
   ```

---

## **8. Deploy Grafana**

### Install Grafana using Helm:
1. Add the Grafana Helm repository:
   ```bash
   helm repo add grafana https://grafana.github.io/helm-charts
   helm repo update
   ```

2. Deploy Grafana:
   ```bash
   helm install grafana grafana/grafana --namespace monitoring
   ```

3. Retrieve the Grafana admin password:
   ```bash
   kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
   ```

4. Access Grafana:
   Forward the Grafana port:
   ```bash
   kubectl port-forward svc/grafana 3000:80 --namespace monitoring
   ```
   Login at `http://localhost:3000` with:
   - Username: `admin`
   - Password: Retrieved from the previous command.

---

## **9. Clean-Up**

To delete all resources:
```bash
kubectl delete namespace monitoring
```
