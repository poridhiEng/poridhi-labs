# Switching Contexts Between Kubernetes Namespaces

Namespaces in Kubernetes provide a way to divide cluster resources between multiple users. They are intended for use in environments with many users spread across multiple teams or projects. Understanding how to switch between contexts allows us to control and manage our Kubernetes resources effectively.

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Namespace-Switching/images/switching-01.PNG)

## Task: Switching Contexts between ``development`` and ``production`` Namespaces

In this guide, we will create two simple pods in two different namespaces (``development`` and ``production``) in a Kubernetes cluster.  we will create an ``NGINX`` pod in the ``development`` namespace and a ``BusyBox`` pod in the ``production`` namespace within a Kubernetes cluster. We will also demonstrate how to switch between these namespaces using ``kubectl``. This will help us understand how to isolate resources and manage different environments within the same cluster.

## Prerequisites

Install vim for creating/editing YAML files in the system.

```bash
sudo apt update
sudo apt install vim
```

## Required Steps

## 1. Create Namespaces

First, create the development and production namespaces.

```bash
kubectl create namespace development
kubectl create namespace production
```

Verify that the namespaces are created:

```bash
kubectl get namespaces
```

## 2. Create ``Nginx`` Pod in ``development`` Namespace

Create a pod for NGINX in development namespace.

(nginx-pod-development.yaml):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  namespace: development
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
    - containerPort: 80
```

Apply the NGINX pod configuration in the ``development`` namespace:

```bash
kubectl apply -f nginx-pod-development.yaml
```

## 2. Create ``BusyBox`` Pod in ``production`` Namespace

Create a pod for BusyBox in production namespace.

(busybox-pod-production.yaml):

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: busybox-pod
  namespace: production
spec:
  containers:
  - name: busybox
    image: busybox
    command: ['sh', '-c', 'while true; do echo hello; sleep 10; done']
```

Apply the BusyBox pod configuration in the ``production`` namespace:

```bash
kubectl apply -f busybox-pod-production.yaml
```

## 3. Verify the pods are running in their respective namespaces

For ``development`` namespace:

```bash
kubectl get pods --namespace=development
```

For ``production`` namespace:

```bash
kubectl get pods --namespace=production
```

## 4. Switch Between Namespaces 

Check the pods running in the ``default`` namespace:

```bash
kubectl get pods
```
There is no pod running in the ``default`` namespace because we have not created any pod.

Set the default namespace for current context to ``development``:

```bash
kubectl config set-context --current --namespace=development
```

Now, any ``kubectl`` command will default to the ``development`` namespace:

```bash
kubectl get pods
```

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Namespace-Switching/images/development-ns.PNG)

Change the default namespace to ``production``:

```bash
kubectl config set-context --current --namespace=production
```

Now, any ``kubectl`` command will default to the ``production`` namespace:

```bash
kubectl get pods
```

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Namespace-Switching/images/production-ns.PNG)

## 5. Confirming the Current Namespace

After switching contexts, it's important to confirm that we're working in the correct namespace.

```bash
kubectl config view --minify | grep namespace:
```
This command will show the namespace that is currently set in the active context. If no specific namespace is set, the default namespace will be used.

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Lab-Namespace-Switching/images/current-context.PNG)

By following these steps, we can easily switch between namespaces in Kubernetes, ensuring that our resources and operations are correctly isolated. 

