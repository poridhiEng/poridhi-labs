# The Ultimate Guide to Create Helm Charts

This documentation provides a step-by-step guide to creating Helm charts for deploying Kubernetes applications. By following this guide, you will learn how to generate a Helm chart, understand its folder structure, and apply templating to customize deployments for different environments such as development, staging, and production.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart/images/overview.png)

## **Introduction to Helm Charts**
Helm is a package manager for Kubernetes that simplifies the deployment process by bundling Kubernetes resources into reusable templates called charts. A Helm chart allows you to deploy your application with a single command, reducing complexity and ensuring consistency across environments.

## **Prerequisites**

**1. Helm CLI installed**

If you don't have Helm CLI installed, you can install it using the following command:
```bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

After installing Helm CLI, you can verify the installation by running:
```bash
helm version
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image.png)

**2. Kubernetes Cluster**

This lab is intended to be run on `Poridhi's` Kubernetes Cluster. You might need to change the kubeconfig path if you face any issues running helm commands.

```bash
kubectl config view --raw > /root/.kube/config
chmod 600 /root/.kube/config
```
---

## **Steps to Create a Helm Chart**

### **1. Generate a Basic Helm Chart**
Helm provides a command to scaffold the necessary files and directories for a chart.

```bash
helm create <chart-name>
```

For example:

```bash
helm create web-server
```

This command generates a folder structure for the Helm chart:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-1.png)

## Folder and File Structure Overview**

#### **Chart.yaml**
- Contains metadata about the Helm chart.
- Fields:
  - `name`: The name of the chart.
  - `version`: The version of the chart, incremented with changes.

#### **values.yaml**
- Contains default configuration values for the chart.
- Customizable by the user for specific environments.
- Example:
  ```yaml
  appName: my-app
  replicas: 2
  ```

#### **charts/**
- Stores dependencies for the chart.
- Only used for complex applications requiring other charts.

#### **templates/**
- Contains Kubernetes manifest templates (YAML files).
- Examples:
  - `deployment.yaml`
  - `service.yaml`
  - `configmap.yaml`

#### **.helmignore**
- Specifies files to ignore when packaging the Helm chart.

---

## Customize the Chart

#### **Clean Up Unnecessary Files**

We will remove the generated templates (e.g., an Nginx application) to start from scratch:

```bash
rm -rf templates/*
```

#### **Add Custom Templates**

We will deploy a simple nginx application with a deployment, service and configmap.

- `deployment.yaml`
- `service.yaml`
- `configmap.yaml`

Fill the contents of `templates/deployment.yaml` with the following:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: default
  labels:
    app: nginx-app
spec:
  replicas: 5
  selector:
    matchLabels:
      app: nginx-app
      tier: frontend
  template:
    metadata:
      labels:
        app: nginx-app
        tier: frontend
    spec:
      containers:
      - name: nginx-container
        image: konami98/:latest
        ports:
        - containerPort: 80
        envFrom:
        - configMapRef:
            name: nginx-configmap
        resources:
          requests:
            memory: "16Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
```

Fill the contents of `templates/service.yaml` with the following:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: default
  labels:
    app: nginx-app
spec:
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
  selector:
    app: nginx-app
    tier: frontend
  type: NodePort
```

Fill the contents of `templates/configmap.yaml` with the following:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-configmap
  namespace: default
data:
  BG_COLOR: '#12181b'
  FONT_COLOR: '#FFFFFF'
  CUSTOM_HEADER: 'Customized with a configmap!'
```

---

### Deploy the Application**

#### **Install the Chart**

Run the following command to install the Helm chart:

```bash
helm install <release-name> <chart-directory>
```

Example:
```bash
helm install custom-nginx-release web-server/
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-3.png)

Verify deployment:

```bash
kubectl get all
```
You should see resources such as Pods, Services, and Deployments.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-2.png)

#### **Access the Application**

To access the application, we can use Poridhi's loadbalancer.

**1. First, we need to get the NodeIP of the master node.**

```bash
kubectl get nodes -o wide
```

**2. Get the NodePort of the service.**

```bash
kubectl get svc
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-4.png)

**3. Create a loadbalancer using the NodeIP and NodePort.**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-5.png)

**4. Access the application using the loadbalancer URL.**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-6.png)

Here is the nginx application running on the loadbalancer.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-7.png)

---

## Helm Templating for Customization

Helm templating allows dynamic values to be injected into YAML files, enabling configurations for different environments. Using the same chart, we will customize the deployment for different environments. For prod environment and dev environment, we will have different configmap data. This approach helps create scalable, environment-specific Kubernetes deployments.

#### 1. First Create prod and dev namespace

```bash
kubectl create namespace prod
kubectl create namespace dev
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-8.png)

#### 2. Define Base Values in `values.yaml`

The `values.yaml` file acts as the default configuration. Below is the base configuration:

```yaml
appName: nginx-custom
port: 80
namespace: default
configmap:
  name: nginx-configmap
  data:
    CUSTOM_HEADER: 'This app was deployed with helm!'
image:
  name: konami98/nginx-custom
  tag: latest
```

- **appName**: Defines the application name.
- **port**: Specifies the port on which the service will expose the application.
- **namespace**: The default namespace for deploying resources.
- **configmap**: Holds environment-specific configuration for the application.
- **image**: Specifies the Docker image and tag.

> NOTE: Make sure to use this image as it is a customized nginx image which can reads the configmap data. If you want to use your own image, make sure to update the image to read the configmap data.

---

#### 3. **Override Base Values for Environments**

To support multiple environments (e.g., `prod` and `dev`), additional values files (`values-prod.yaml`, `values-dev.yaml`) are created to override the base configuration.

**Production Values:**

```yaml
namespace: prod
configmap:
  data:
    CUSTOM_HEADER: 'Nginx webserver is running on the PROD environment!'
```

**Development Values:**

```yaml
namespace: dev
configmap:
  data:
    CUSTOM_HEADER: 'Nginx webserver is running on the DEV environment!'
```

- Both files override the namespace and `CUSTOM_HEADER` field in the `configmap`.

#### 4. **Template Kubernetes Resources**

**Example ConfigMap Template:**

```yaml
kind: ConfigMap 
apiVersion: v1 
metadata:
  name: {{ .Values.configmap.name }}
  namespace: {{ .Values.namespace }}
data:
  BG_COLOR: '#12181b'
  FONT_COLOR: '#FFFFFF'
  CUSTOM_HEADER: {{ .Values.configmap.data.CUSTOM_HEADER }}
```

- `{{ .Values.configmap.name }}` and `{{ .Values.namespace }}` are dynamically populated based on the environment-specific values.
- The `CUSTOM_HEADER` is injected dynamically for the environment.

**Example Deployment Template:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.appName }}
  namespace: {{ .Values.namespace }}
  labels:
    app: {{ .Values.appName }}
spec:
  replicas: 5
  selector:
    matchLabels:
      app: {{ .Values.appName }}
      tier: frontend
  template:
    metadata:
      labels:
        app: {{ .Values.appName }}
        tier: frontend
    spec: # Pod spec
      containers:
      - name: mycontainer
        image: "{{ .Values.image.name }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 80
        envFrom:
        - configMapRef:
            name: {{ .Values.configmap.name }}
        resources:
          requests:
            memory: "16Mi" 
            cpu: "50m"    # 50 milli cores (1/20 CPU)
          limits:
            memory: "128Mi" # 128 mebibytes 
            cpu: "100m"
```

- The `image` and `namespace` fields dynamically adapt based on the values file.
- `envFrom` ensures the application can access the `ConfigMap` values as environment variables.

**Example Service Template:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.appName }}
  namespace: {{ .Values.namespace }}
  labels:
    app: {{ .Values.appName }}
spec:
  ports:
  - port: 80
    protocol: TCP
    name: http
  selector:
    app: {{ .Values.appName }}
    tier: frontend
  type: NodePort
```

- The `port` and `namespace` are dynamically injected.

---

#### 5. **Install or Upgrade Helm Release**

Deploy the Helm chart with the base `values.yaml` file or override it with the environment-specific values.

**Base Deployment:**

```bash
helm upgrade nginx-custom-release web-server/ --values web-server/values.yaml
```

**Production Deployment:**

```bash
helm install nginx-custom-dev web-server/ --values web-server/values.yaml -f web-server/values-dev.yaml -n dev
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-9.png)

**Development Deployment:**

```bash
helm install nginx-custom-prod web-server/ --values web-server/values.yaml -f web-server/values-prod.yaml -n prod
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-10.png)

### Verify the Deployment

After deploying the helm chart, we can verify the deployment by running the following command:

**1. Get all the helm releases**

```bash
helm ls --all-namespaces
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-11.png)

**2. Default Deployment**

```bash
kubectl get all
```

**2. Production Deployment**

```bash
kubectl get all -n prod
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-12.png)

**3. Development Deployment**

```bash
kubectl get all -n dev
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-13.png)

### Access the Application

To access the application, we can use Poridhi's loadbalancer. Create loadbalancers for the production and development deployment in the same way as we did in the previous section and access the application using the loadbalancer URL.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-16.png)

**Here is the nginx application running on the production environment.**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-15.png)

**Here is the nginx application running on the dev environment.**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Labs/Lab-HelmChart//images/image-14.png)

---

## **Conclusion**

By following this guide, you now have the foundational skills to create, customize, and deploy Helm charts. This will allow you to streamline the Kubernetes application deployment process and maintain consistency across multiple environments. Explore further Helm features, such as hooks and dependencies, to enhance your deployments!