# Nginx Web Server Deployment in Development and Production Environments using Kustomize

## Scenario Overview

In this lab, we are going to deploy an Nginx web server in both development (dev) and production (prod) environments using Kubernetes. Each environment has distinct requirements tailored to its specific needs. For the development environment, we need to configure a deployment with 2 replicas, allocating fewer CPU and memory resources to conserve resources. The service should be exposed using a `NodePort` to facilitate easy access during development. In the production environment, the deployment should be configured with 4 replicas, higher CPU and memory limits to handle increased traffic and a service with `ClusterIP`.

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/refs/heads/nabil-branch/Lab-Kustomize/images/kustomize.png)

## Directory Structure

The project follows a specific directory structure for organizing base and overlay configurations.

```
kustomize
├── base
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── kustomization.yaml
└── overlays
    ├── dev
    │   ├── deployment-dev.yaml
    │   ├── service-dev.yaml
    │   └── kustomization.yaml
    └── prod
        ├── deployment-prod.yaml
        ├── service-prod.yaml
        └── kustomization.yaml
```

Create the required directory structure and files using the following commands:

```sh
mkdir -p kustomize/base &&
    touch kustomize/base/deployment.yaml \
         kustomize/base/service.yaml \
         kustomize/base/kustomization.yaml &&
    mkdir -p kustomize/overlays/dev &&
    touch kustomize/overlays/dev/deployment-dev.yaml \
         kustomize/overlays/dev/service-dev.yaml \
         kustomize/overlays/dev/kustomization.yaml &&
    mkdir -p kustomize/overlays/prod &&
    touch kustomize/overlays/prod/deployment-prod.yaml \
         kustomize/overlays/prod/service-prod.yaml \
         kustomize/overlays/prod/kustomization.yaml
```


## Create Namespace for `dev` and `prod`

We can see the initial namespaces using the following command:

```bash
kubectl get namespace
```

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Kustomize/images/kustomize-01.png)

We can create new namespace called `dev` and `prod` by using the ``kubectl`` command.

```bash
kubectl create namespace dev
kubectl create namespace prod
```

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Kustomize/images/kustomize-02.png)

## `base` directory

The base folder contains the deployment, service, and kustomization files. In this base folder, we add the deployment and service YAML with all the configs which could be common for all the environments.

`base/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx-container
        image: nginx:latest
        ports:
        - containerPort: 80
```

`base/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
  namespace: default
spec:
  selector:
    app: web
  ports:
  - name: http
    port: 80
```

`base/kustomization.yaml`:

In this file, we’re referring `deployment.yaml` and `service.yaml` as resources.

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: default

resources:
- deployment.yaml
- service.yaml
```

## Dev Overlay Folder

The following steps describe how to use Kustomize to configure and deploy an Nginx web server in a development environment with specific requirements. For the development environment, we want to configure a deployment with 2 replicas, allocating fewer CPU and memory resources to conserve resources. The service should be exposed using a `NodePort` to facilitate easy access during development.

`overlays/dev/deployment-dev.yaml`:

This file increases the number of replicas from 1 to 2 and adjusts CPU and memory resources. Note that only the changes are defined here. Kustomize will apply these changes to the base deployment configuration.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 2 
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx-container
        resources:
          limits:
            cpu: "200m"
            memory: "256Mi"
          requests:
            cpu: "100m"
            memory: "128Mi"
``` 

`overlays/dev/service-dev.yaml`:

The service in the development environment is configured to use NodePort as a service type.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: NodePort
```

`overlays/dev/kustomization.yaml`:

The `kustomization.yaml` file in the development overlay references the base resources and specifies the patch files for deployment and service.

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: dev

patches:
- path: deployment-dev.yaml
- path: service-dev.yaml
```

### Applying the Changes

To review the customized manifests for the development environment, use the following command:

```sh
kubectl kustomize kustomize/overlays/dev
```
Use this command if you are in the root directory. If you are in the directory where the `kustomization.yaml` file is located, then you can simply use:

```sh
kubectl kustomize .
```

This command will render the final Kubernetes manifest, showing the development-specific changes.

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Kustomize/images/kustomize-03.png)

To apply the customized manifest to the Kubernetes cluster, use one of the following commands:

From root directory:

```sh
kubectl apply -k kustomize/overlays/dev
```

From `kustomize/overlays/dev` directory:

```sh
kubectl apply -k .
```

### Verification

After applying the changes, verify the deployment and services:

```sh
kubectl get deployments -n dev
kubectl get services -n dev
kubectl get pods -n dev
```

To view all objects at once:

```sh
kubectl get all -n dev
```

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Kustomize/images/kustomize-04.png)

Here, we can see that there are 2 replicas running in the dev environment.

## Prod Overlay Folder

In the production environment, the deployment should be configured with 4 replicas, higher CPU and memory limits to handle increased traffic and a service with `ClusterIP`.

`overlays/prod/deployment-prod.yaml`:

This file increases the number of replicas from 1 to 2 and adjusts CPU and memory resources in the prod environment.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 4 
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx-container
        resources:
          limits:
            cpu: "500m" 
            memory: "512Mi" 
          requests:
            cpu: "200m" 
            memory: "256Mi"
```

`overlays/prod/service-prod.yaml`: 

We are changing the service type to ClusterIP.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: ClusterIP
```

`overlays/prod/kustomization.yaml`:

The `kustomization.yaml` file in the development overlay references the base resources and specifies the patch files for deployment and service.

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

namespace: prod

patches:
- path: deployment-prod.yaml
- path: service-prod.yaml
```

### Applying the Changes

To review the customized manifests for the production environment, use the following command:

```sh
kubectl kustomize kustomize/overlays/prod
```
Use this command if you are in the root directory. If you are in the directory where the `kustomization.yaml` file is located, then you can simply use:

```sh
kubectl kustomize .
```

This command will render the final Kubernetes manifest, showing the development-specific changes.

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Kustomize/images/kustomize-05.png)

To apply the customized manifest to the Kubernetes cluster, use one of the following commands:

From root directory:

```sh
kubectl apply -k kustomize/overlays/prod
```

From `kustomize/overlays/prod` directory:

```sh
kubectl apply -k .
```

### Verification

After applying the changes, verify the deployment and services:

```sh
kubectl get deployments -n prod
kubectl get services -n prod
kubectl get pods -n prod
```

To view all objects at once:

```sh
kubectl get all -n prod
```

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Kustomize/images/kustomize-06.png)

## Conclusion

This documentation provides a comprehensive guide to deploying an Nginx web server using Kustomize, covering both development and production environments. By following the steps outlined, you can easily manage different configurations for each environment, ensuring that each has the appropriate settings and resources.
