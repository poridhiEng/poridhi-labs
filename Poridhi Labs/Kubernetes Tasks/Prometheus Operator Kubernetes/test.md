Here is a detailed documentation for implementing the project up to setting up the Grafana dashboard, excluding the Terraform AWS part:

---

# **Setting up Prometheus Operator and Grafana Dashboard**

## **Prerequisites**
1. **Kubernetes Cluster**: Ensure you have an operational Kubernetes cluster. You can use EKS, GKE, AKS, or Minikube.
2. **Kubectl Installed**: Your system should have `kubectl` installed and configured to connect to your cluster.
3. **Helm Installed**: Install Helm to manage and deploy Kubernetes applications.
4. **Repository Access**: Clone the [GitHub repository](https://github.com/antonputra/tutorials/tree/main/lessons/154).

---

## **Steps to Implement the Project**

### **1. Create a Monitoring Namespace**
- Use the following YAML file to create a dedicated namespace for monitoring components:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    monitoring: prometheus
```

Apply the namespace:
```bash
kubectl apply -f namespace.yaml
```

---

### **2. Install Prometheus Operator**
1. **Custom Resource Definitions (CRDs):**
   - Download and apply the necessary CRDs from the Prometheus Operator repository:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/prometheus-operator-crd.yml
   ```

2. **RBAC Configuration:**
   - Define role-based access control for the Prometheus Operator:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/example/rbac/prometheus-operator-role-binding.yml
   ```

3. **Deploy the Prometheus Operator:**
   - Use the following YAML for deployment:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: prometheus-operator
     namespace: monitoring
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: prometheus-operator
     template:
       metadata:
         labels:
           app: prometheus-operator
       spec:
         containers:
         - name: prometheus-operator
           image: quay.io/prometheus-operator/prometheus-operator:v0.63.0
   ```
   Apply the deployment:
   ```bash
   kubectl apply -f prometheus-operator-deployment.yaml
   ```

4. Verify the Deployment:
   ```bash
   kubectl get pods -n monitoring
   ```

---

### **3. Deploy Prometheus**
1. **Service Account and RBAC for Prometheus:**
   - Create a service account and cluster role binding for Prometheus.

2. **Deploy Prometheus:**
   - Use a YAML file for the Prometheus custom resource:
   ```yaml
   apiVersion: monitoring.coreos.com/v1
   kind: Prometheus
   metadata:
     name: prometheus
     namespace: monitoring
   spec:
     replicas: 1
     serviceAccountName: prometheus
     retention: 7d
   ```
   Apply the configuration:
   ```bash
   kubectl apply -f prometheus.yaml
   ```

3. Verify the Deployment:
   ```bash
   kubectl get pods -n monitoring
   ```

---

### **4. Deploy a Sample Application**
- Deploy a sample Go application exposing Prometheus metrics.
```bash
kubectl apply -f https://raw.githubusercontent.com/antonputra/tutorials/main/lessons/154/sample-app.yaml
```

---

### **5. Configure Monitoring for the Application**
1. **Create a PodMonitor:**
   - Define a `PodMonitor` resource to monitor the sample app:
   ```yaml
   apiVersion: monitoring.coreos.com/v1
   kind: PodMonitor
   metadata:
     name: sample-app-monitor
     namespace: monitoring
   spec:
     selector:
       matchLabels:
         app: sample-app
     namespaceSelector:
       matchNames:
       - default
     podMetricsEndpoints:
     - port: metrics
   ```
   Apply the configuration:
   ```bash
   kubectl apply -f pod-monitor.yaml
   ```

2. Verify the Configuration:
   ```bash
   kubectl get podmonitors -n monitoring
   ```

---

### **6. Install Grafana**
1. **Add the Helm Repository:**
   ```bash
   helm repo add grafana https://grafana.github.io/helm-charts
   helm repo update
   ```

2. **Deploy Grafana:**
   - Use the following command to deploy Grafana with Helm:
   ```bash
   helm install grafana grafana/grafana --namespace monitoring --set adminPassword=admin123
   ```

3. Verify the Deployment:
   ```bash
   kubectl get pods -n monitoring
   ```

4. **Access Grafana:**
   - Forward the Grafana service to your local machine:
   ```bash
   kubectl port-forward svc/grafana 3000:80 -n monitoring
   ```
   - Open your browser and go to `http://localhost:3000`. Use the default username `admin` and password `admin123` to log in.

---

### **7. Configure Grafana Dashboard**
1. **Add a Prometheus Data Source:**
   - Navigate to **Configuration > Data Sources** in Grafana.
   - Add a new Prometheus data source with the following URL:
     ```
     http://prometheus-operated.monitoring.svc:9090
     ```

2. **Create a Dashboard:**
   - Use the metrics from the sample application to create visualizations.

3. **Save the Dashboard:**
   - Customize and save the dashboard as needed.

---

### **Next Steps**
- The Grafana dashboard is now set up and displaying metrics. For advanced configurations, you can explore:
  - Adding external scrape configurations.
  - Setting up Alertmanager for alerts.
  - Deploying additional exporters for extended monitoring.

--- 

This concludes the documentation for setting up the Prometheus Operator and Grafana dashboard.