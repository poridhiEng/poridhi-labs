# Prometheus Operator

This lab provides a simplified step-by-step guide for setting up Prometheus Operator in Kubernetes. It includes the setup of `ServiceMonitor` and `PodMonitor` objects for monitoring, deploying Grafana for visualisation.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/Prometheus-operator-2.drawio.svg)

### Prerequisites

**1. Kubernetes Cluster: Ensure you have an operational Kubernetes cluster. You can use EKS, GKE, AKS, or Minikube.**

**2. Helm Installed: Install Helm to manage and deploy Kubernetes applications.**

## Overall Folder Structure

```
.
├── alertmanager/
├── blackbox-exporter/
├── myapp/
├── prometheus-operator/
├── prometheus/
├── terraform/
├── README.md
├── alert.yaml
├── build.sh
├── grafana-values.yaml
├── probe.yaml
└── scrape-config.yaml
```


## Steps to Implement the Project

## **Install Prometheus Operator**

To install Prometheus Operator, Clone this repository to get the necessary files:

```bash
git clone https://github.com/Konami33/Prometheus-Operator.git
```

**Create a Monitoring Namespace**

Use the following YAML file to create a dedicated namespace for monitoring components:

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

**Custom Resource Definitions (CRDs):**

Apply the necessary CRDs for Prometheus Operator. These include definitions for objects like ServiceMonitor, PodMonitor, and other custom configurations.

```sh
kubectl apply --server-side -f prometheus-operator/crds
```

**Server-Side Apply:**

The `--server-side` flag instructs Kubernetes to apply changes using server-side apply rather than the default client-side apply. With server-side apply:
- The server manages the changes and ensures conflicts are detected and resolved.
- It's particularly useful for managing resources collaboratively or when multiple controllers might update the same resource.
- The server will calculate the desired state by merging fields from the manifest and existing configurations.

You can check the created crds:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-3.png)

**2. RBAC Configuration:**
Apply the Role and RoleBinding configurations to ensure proper access control for the Prometheus Operator.

```sh
kubectl apply -f prometheus-operator/rbac
```

**3. Deploy the Prometheus Operator:**

```sh
kubectl apply -f prometheus-operator/deployment
```

Check the status of the deployment:

```sh
kubectl get pods -n monitoring
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-4.png)

You may check the logs of the pod for any misconfiguration.

## **Deploy Prometheus**

For deploying Prometheus, create the necessary files step by step:

### **1. ServiceAccount**

#### **File Contents: (service-account.yaml)**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring
```

The `ServiceAccount` allows Prometheus to interact with Kubernetes resources securely.

**Key Attributes**:
- **`name`**: Specifies the `prometheus` ServiceAccount to be used by the Prometheus pods.
- **`namespace`**: Limits the scope of this ServiceAccount to the `monitoring` namespace.

**Function**: This ensures Prometheus operates under the permissions defined in the RBAC rules, without relying on the default ServiceAccount.

---

### **2. ClusterRole**
#### **File Contents: (cluster-role.yaml)**
```yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
  - apiGroups: [""]
    resources:
      - nodes
      - nodes/metrics
      - services
      - endpoints
      - pods
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources:
      - configmaps
    verbs: ["get"]
  - apiGroups:
      - networking.k8s.io
    resources:
      - ingresses
    verbs: ["get", "list", "watch"]
  - nonResourceURLs: ["/metrics"]
    verbs: ["get"]
```

Grants Prometheus the necessary permissions to monitor Kubernetes resources and collect metrics.

**Key Permissions**:
- **Cluster Resources**:
- Access `nodes`, `services`, `endpoints`, and `pods` to discover metrics endpoints.
- Access `configmaps` to read configuration data.
- **Networking Resources**:
- Access `ingresses` to gather network-related metrics.
- **NonResourceURLs**:
- Fetch data from `/metrics`, a common endpoint for exposing application and system metrics.

**Function**: This ensures Prometheus has visibility into the Kubernetes cluster, enabling it to scrape metrics from various sources.

---

### **3. ClusterRoleBinding**

#### **File Contents: (cluster-role-binding.yaml)**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
  - kind: ServiceAccount
    name: prometheus
    namespace: monitoring
```


ClusterRoleBinding binds the `prometheus` ClusterRole to the `prometheus` ServiceAccount.

**Key Attributes**:
- **`roleRef`**: Links to the `prometheus` ClusterRole, granting Prometheus the permissions defined there.
- **`subjects`**: Specifies that the `prometheus` ServiceAccount in the `monitoring` namespace is the entity receiving the permissions.

**Function**: Ensures Prometheus pods, running under the `prometheus` ServiceAccount, have the required permissions to monitor cluster resources.

---

### **4. Prometheus Custom Resource**
#### **File Contents: (prometheus.yaml)**

```yaml
---
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: main
  namespace: monitoring
spec:
  alerting:
    alertmanagers:
      - namespace: monitoring
        name: alertmanager-operated
        port: web
  ruleSelector:
    matchLabels:
      prometheus: main
  ruleNamespaceSelector:
    matchLabels:
      monitoring: prometheus
  version: v2.42.0
  serviceAccountName: prometheus
  podMonitorSelector:
    matchLabels:
      prometheus: main
  podMonitorNamespaceSelector:
    matchLabels:
      monitoring: prometheus
  serviceMonitorSelector:
    matchLabels:
      prometheus: main
  serviceMonitorNamespaceSelector:
    matchLabels:
      monitoring: prometheus
  probeSelector:
    matchLabels:
      prometheus: main
  probeNamespaceSelector:
    matchLabels:
      monitoring: prometheus
  resources:
    requests:
      memory: 500Mi
      cpu: 200m
    limits:
      memory: 1Gi
      cpu: 500m
  replicas: 1
  logLevel: info
  logFormat: logfmt
  retention: 3d
  scrapeInterval: 15s
  securityContext:
    fsGroup: 0
    runAsNonRoot: false
    runAsUser: 0
  storage:
    volumeClaimTemplate:
      spec:
        resources:
          requests:
            storage: 20Gi
```

It deploys and configures a Prometheus instance to scrape metrics from Kubernetes resources and applications.

**Key Attributes**:
- **`alerting`**: Configures integration with Alertmanager for sending alerts.
- `ruleSelector`: Finds PrometheusRules based on labels for alerts.
- `podMonitorSelector` & `serviceMonitorSelector`: Finds targets for scraping based on labels.
- `probeSelector`: Configures probes for black-box monitoring.
- **`replicas`**: Configures a single replica of Prometheus.
- **`storage`**: Requests 500Mi of persistent storage for metric data retention.
- **`retention`**: Retains metrics data for 3 days.
- **`scrapeInterval`**: Configures a 15-second interval for scraping targets.
- **`securityContext`**: Configures Prometheus to run as root (`runAsUser: 0`), which may be needed depending on the setup.

**Function**: Deploys Prometheus with specific configurations for storage, alerting, monitoring, and scraping metrics.


Apply the manifests:

```sh
kubectl apply -f prometheus
```

**Make sure pods are running:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-5.png)


**Access the prometheus UI:**

To access the prometheus UI, first get service, and port-forward the service to test it locally:

```sh
kubectl get svc -n monitoring
kubectl port-forward svc/prometheus-operated 9090 -n monitoring
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-6.png)

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-7.png)

## **Go application**

**First write a simple Go application exposing metrics:**

```go
package main

import (
	"log"
	"math/rand"
	"net/http"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

type metrics struct {
	duration *prometheus.SummaryVec
}

func NewMetrics(reg prometheus.Registerer) *metrics {
	m := &metrics{
		duration: prometheus.NewSummaryVec(prometheus.SummaryOpts{
			Namespace:  "tester",
			Name:       "duration_seconds",
			Help:       "Duration of the request.",
			Objectives: map[float64]float64{0.9: 0.01, 0.99: 0.001},
		}, []string{"path", "status"}),
	}
	reg.MustRegister(m.duration)
	return m
}

type Device struct {
	ID       int    `json:"id"`
	Mac      string `json:"mac"`
	Firmware string `json:"firmware"`
}

func main() {
	reg := prometheus.NewRegistry()
	m := NewMetrics(reg)

	pMux := http.NewServeMux()
	promHandler := promhttp.HandlerFor(reg, promhttp.HandlerOpts{})
	pMux.Handle("/metrics", promHandler)

	go func() {
		log.Fatal(http.ListenAndServe(":8081", pMux))
	}()

	go simulateTraffic(m)

	app := fiber.New()

	app.Get("/api/devices", getDevices)

	log.Fatal(app.Listen(":8080"))
}

func getDevices(c *fiber.Ctx) error {
	sleep(1000)
	dvs := []Device{
		{1, "5F-33-CC-1F-43-82", "2.1.6"},
		{2, "EF-2B-C4-F5-D6-34", "2.1.6"},
	}

	return c.JSON(dvs)
}

func simulateTraffic(m *metrics) {
	for {
		now := time.Now()
		sleep(1000)
		m.duration.WithLabelValues("/fake", "200").Observe(time.Since(now).Seconds())
	}
}

func sleep(ms int) {
	rand.Seed(time.Now().UnixNano())
	now := time.Now()
	n := rand.Intn(ms + now.Second())
	time.Sleep(time.Duration(n) * time.Millisecond)
}
```

**Dockerize the Application:**

**dockerfile**

```dockerfile
FROM golang:1.19.6-buster AS build

WORKDIR /app

COPY go.mod ./
COPY go.sum ./

RUN go mod download && go mod verify

COPY main.go main.go

RUN go build -o /myapp main.go

FROM gcr.io/distroless/base-debian11

COPY --from=build /myapp /myapp

ENTRYPOINT ["/myapp"]
```

Build and Push the Docker Image:

```sh
docker build -t <DOCKERHUB_USERNAME>/<IMAGE_NAME>:<VERSION> .
docker push <DOCKERHUB_USERNAME>/<IMAGE_NAME>:<VERSION>
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image.png)

> NOTE: Make sure to login to the docker hub.

## **Deploy the Go Application**

To deploy the application in the kubernetes cluster, follow the stes:

#### **1. Namespace**
##### **File Contents: (namespace.yaml)**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: staging
  labels:
    monitoring: prometheus
```

This manifest file creates a dedicated `staging` namespace to deploy the Go application.

**Labels**: `monitoring: prometheus` Used to associate this namespace with Prometheus monitoring.

---

#### **2. Deployment**
##### **File Contents: (deployment.yaml)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: staging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: <YOUR_IMAGE_NAME>
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 8080
            - name: http-metrics
              containerPort: 8081
          resources:
            requests:
              memory: 256Mi
              cpu: 200m
            limits:
              memory: 256Mi
              cpu: 200m
```


**Purpose**: Deploys the Go application in the `staging` namespace.

**Key Attributes**:

- **`replicas: 1`**: Ensures a single instance of the application is running.
- **`selector`**: `matchLabels: app: myapp` Matches pods with the label `app: myapp`, ensuring only these pods are part of this deployment.
- **Template Labels**:

    **`app: myapp`**: Adds this label to all pods created by the deployment. The selector ensures that the Deployment manages these pods.

- **Ports**:
    - `8080`: The main application port.
    - `8081`: Exposes metrics for Prometheus scraping.
- **Resources**:
    - **Requests**: Ensures the pod gets a minimum of `200m CPU` and `256Mi memory`.
    - **Limits**: Prevents the pod from exceeding `200m CPU` and `256Mi memory`.

---

#### **3. Service**
##### **File Contents: (service.yaml)**
```yaml
apiVersion: v1
kind: Service
metadata:
  namespace: staging
  name: myapp
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 8080
      targetPort: http
  selector:
    app: myapp
```

**Purpose**: Exposes the application within the cluster as a ClusterIP service.

**Key Attributes**:

- **`type: ClusterIP`**: Ensures the service is accessible only within the cluster.
- **`port: 8080`**: Service listens on port 8080.

- **`targetPort: http`**: Forwards traffic to the container’s `http` port (mapped to 8080 in the Deployment).

- **`app: myapp`**: Directs traffic to pods with the `app: myapp` label.

**Function**: Provides stable internal networking for the application, enabling other services or components to communicate with it.

---

#### **4. PodMonitor**
##### **File Contents: (pod-monitor.yaml)**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: myapp
  namespace: staging
  labels:
    prometheus: main
spec:
  namespaceSelector:
    matchNames:
      - staging
  selector:
    matchLabels:
      app: myapp
  podMetricsEndpoints:
    - port: http-metrics
      path: /metrics
```

**Purpose**: Configures Prometheus to scrape metrics from the Go application pods.

**Key Attributes**:
- **`labels: prometheus: main`**: Associates this PodMonitor with the Prometheus instance labeled `main`.

- **Namespace Selector**:
    - **`matchNames: staging`**: Limits the scope of this PodMonitor to the `staging` namespace.
- **Pod Selector**:
    - **`matchLabels: app: myapp`**: Targets pods with the `app: myapp` label.
- **Endpoints**:
  - **`port: http-metrics`**: Specifies the container port (8081) that exposes metrics.
  - **`path: /metrics`**: The endpoint path to scrape metrics from the application.

**Function**: Enables Prometheus to dynamically discover and scrape metrics from all pods matching the specified labels and namespace.


#### **5. Service: `myapp-prom`**

##### **File Contents: (prom-service.yaml)**
```yaml
---
apiVersion: v1
kind: Service
metadata:
  namespace: staging
  name: myapp-prom
  labels:
    app: myapp-monitoring
spec:
  type: ClusterIP
  ports:
    - name: http-metrics
      port: 8081
      targetPort: http-metrics
  selector:
    app: myapp
```

**Purpose**: Creates a dedicated service to expose metrics from the Go application (on port `8081`) within the cluster.
**Key Attributes**:

- Specifies the `staging` namespace, ensuring the service operates within the same scope as the application.

- **`app: myapp-monitoring`**: Label used for identification by the `ServiceMonitor` to scrape metrics.
- **`type: ClusterIP`**: Ensures the service is only accessible within the Kubernetes cluster.
- **`port: 8081`**: Exposes the service on port `8081` for internal communication.
- **`targetPort: http-metrics`**: Forwards traffic to the container's `http-metrics` port (defined in the deployment).
- **`selector`**: `app: myapp` Matches pods labeled with `app: myapp` (from the deployment) to forward traffic.

**Functionality**:

This service acts as a dedicated endpoint for Prometheus to scrape application metrics, keeping the metrics interface separate from the application's primary service (if any). The use of `http-metrics` ensures Prometheus accesses the appropriate metrics endpoint.


#### **6. ServiceMonitor: `myapp`**

##### **File Contents: (service-monitor.yaml)**
```yaml
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp
  namespace: staging
  labels:
    prometheus: main
spec:
  namespaceSelector:
    matchNames:
      - staging
  selector:
    matchLabels:
      app: myapp-monitoring
  endpoints:
    - port: http-metrics
      path: /metrics
```

**Purpose**: Configures Prometheus to monitor services (like `myapp-prom`) by defining a `ServiceMonitor` resource
**Key Attributes**:

- The `staging` namespace is specified to limit the scope of monitoring to this namespace.
- **`prometheus: main`**: Associates this `ServiceMonitor` with the Prometheus instance labeled `main`.

- **`matchNames: staging`**: Restricts the `ServiceMonitor` to select services only in the `staging` namespace.

- **`matchLabels: app: myapp-monitoring`**: Targets services with the label `app: myapp-monitoring` (e.g., `myapp-prom` service).
- **`endpoints`**:
    - **`port: http-metrics`**: Specifies the metrics port (8081) of the service to scrape.
    - **`path: /metrics`**: Defines the HTTP path where metrics are exposed by the application.

**Functionality**:
The `ServiceMonitor` enables Prometheus to dynamically discover and scrape metrics from Kubernetes services (e.g., `myapp-prom`) that meet the defined criteria. This simplifies integration and ensures scalability as new services matching the labels are automatically monitored.

**Apply the deployment:**

```sh
kubectl apply -f myapp/deploy
```
**Verify the deployment:**

```sh
kubectl get all -n staging
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-8.png)

## Check prometheus UI for targets and metrics:

First checkout if the targets are expodes correctly:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-9.png)


lets query some metrics:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-10.png)

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-11.png)


## **Deploy Grafana**

Create a Kubernetes deployment for Grafana using the Prometheus Operator. Make sure you have helm installed on you machine or you can install this using the following command:

```sh
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

Update the Kubeconfig file permission:

```sh
kubectl config view --raw > /root/.kube/config
chmod 600 /root/.kube/config
```

**Install Grafana using Helm:**

```sh
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install grafana grafana/grafana -n monitoring --create-namespace
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-12.png)

**Expose the Grafana service using Nodeport:**

The Grafana service type will by default `ClusterIP`. We will convert it into NodePort service to access through Poridhi's Loadbalancer.

```sh
helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --set service.type=NodePort \
  --set service.nodePort=30080
```

**Create a load balancer with the MasterNode IP and the Nodeport (30080).**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-14.png)


**Get the admin password to login into Grafana:**

```sh
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-13.png)

Use the password and login into Grafana UI.


## **Configure Grafana Dashboard**

Let's create a Grafana Dashboard for visualization.

### **Create a New Dashboard**
1. In the Grafana menu (left side), click **Dashboards**.
2. Click **+ Create** and select **Dashboard**.
3. Choose **Add a new panel** to start configuring the panel.

### **Configure the Panel**
**1. Panel Title**:
- In the top-left corner of the editor, click the title field and enter **Traffic** as the panel title.

**2. Data Source**:
- In the **Query** section, select your Prometheus data source from the dropdown menu.
- If not configured:

     - Go to **Configuration** > **Data Sources** in the left-hand menu.
     - Click **Add data source**, select **Prometheus**, enter the Prometheus URL (e.g., `http://prometheus-operated.monitoring.svc:9090`), and save the configuration.

     ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-15.png)

**3. PromQL Query**: In the **Query** editor, enter the following PromQL query:

```
rate(tester_duration_seconds_count[1m])
```
Click **Run query** to ensure the data is being fetched correctly.

**4. Legend**:
In the **Legend** field, enter:

```
{{path}}
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/image-16.png)

### **Customize the Visualization**

**1. Visualization Type**: On the right panel, under the **Visualization** tab, select **Time series** as the panel type.

**2. Field Settings**:

- Go to the **Field** tab.
- Set the unit to **requests per second (reqps)**.
- Adjust thresholds:
    - Green: Default (normal traffic levels).
    - Red: Triggered when traffic exceeds 80 requests per second.

**3. Graph Settings**:

- Set **Line Width** to `2` for a clear line graph.
- Enable **Fill Opacity** to `50%` for better visibility.
- Ensure **Line Interpolation** is set to `smooth` for smoother curves.

**4. Tooltip**: In the **Options** tab, set the **Tooltip mode** to `Single`.

**5. Legend Placement**:

- Enable the legend by toggling **Show Legend**.
- Set **Display Mode** to `List`.
- Set **Placement** to `Bottom`.


### **Save the Dashboard**

1. Click **Apply** in the top-right corner to save the panel configuration.
2. You’ll return to the dashboard view. Click **Save Dashboard** in the top-right corner.
3. Enter a name for your dashboard (e.g., **Traffic Dashboard**) and click **Save**.

---

### **Verify the Panel**
**1. Check the panel to ensure it’s displaying the correct data.**
- The graph should show the rate of HTTP requests per second.
- The legend should display the `path` label from the metrics.

**2. If the graph is empty:**
- Verify the Prometheus data source configuration.
- Ensure the query returns data in Prometheus directly.


Here is how the panel will look like:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/Prometheus%20Operator%20Kubernetes/images/dash.png)


## Conclusion

In this tutorial, we have successfully created a Grafana dashboard to monitor the HTTP request rate in a
Kubernetes cluster using Prometheus as the data source. We have also customized the panel to display the
correct data and set up alerts for high traffic levels. This dashboard will help you monitor and troubleshoot
your application's performance in real-time.






