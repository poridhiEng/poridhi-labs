# Generating ConfigMaps Using Kustomize

In this tutorial, we'll explore how to generate ConfigMaps using Kustomize in a Kubernetes environment. We'll walk through an Nginx example where we use a ConfigMap to provide content for `index.html`. This guide assumes you have a basic understanding of Kubernetes, Kustomize, and have `kubectl` installed and configured.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/309c930d26d0e32057a5aa09f9e2fdddfd79f3c0/Kustomize/Lab%2004/images/configmap.svg)

## Prerequisites

- **Kustomize**: Ensure you have Kustomize installed. If you have `kubectl` version 1.14 or later, Kustomize is included.
- **Kubernetes Cluster**: Access to a Kubernetes cluster where you can deploy resources.

## Repository Structure

Here's the file structure we'll be working with, specifically focusing on the `generators` overlay folder:

```
├── base
│   ├── deployment.yaml
│   ├── kustomization.yaml
│   └── service.yaml
└── overlays
    ├── generators
        ├── deployment.yaml
        ├── files
        │   └── index.html
        ├── kustomization.yaml
        └── service.yaml
```

## Base Configuration Files

Before diving into the overlays, let's look at the base configuration files. These files provide the foundational Kubernetes resources that the overlays will modify or extend.

### 1. `base/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-service
  template:
    metadata:
      labels:
        app: web-service
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```

**Explanation:**

- Defines a Deployment named `web-deployment`.
- Specifies 2 replicas.
- Labels pods with `app: web-service`.
- Runs the `nginx` container exposing port 80.

### 2. `base/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web-service
  ports:
  - protocol: TCP
    port: 80
```

**Explanation:**

- Defines a Service named `web-service`.
- Selects pods with `app: web-service`.
- Exposes port 80.

### 3. `base/kustomization.yaml`

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
```

**Explanation:**

- Lists the resources (`deployment.yaml` and `service.yaml`) to include.

## Generating ConfigMaps with Kustomize

Now, let's focus on the `generators` overlay, which customizes the base resources and adds ConfigMap generators.

### Overlay Directory Structure

```
overlays/generators
├── deployment.yaml
├── files
│   └── index.html
├── kustomization.yaml
└── service.yaml
```

### 1. Overlay `deployment.yaml` File

In the `overlays/generators` directory, the `deployment.yaml` file modifies the base deployment to:

- Use ConfigMaps for environment variables and mounted volumes.
- Set resource requests and limits.
- Increase replicas to 3.

Here's the `deployment.yaml` file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  selector:                     
    matchLabels:
      app: web-service         
  template:
    metadata:
      labels:                    
        app: web-service         
    spec:
      containers:
      - name: nginx
        resources:
          limits:
            cpu: "200m"
            memory: "256Mi"
          requests:
            cpu: "100m"
            memory: "128Mi"
        env:
        - name: ENDPOINT
          valueFrom:
            configMapKeyRef:
              name: endpoint-configmap
              key: endpoint
        volumeMounts:
        - name: nginx-index-file
          mountPath: /usr/share/nginx/html/
      volumes:
      - name: nginx-index-file
        configMap:
          name: index-html-configmap
```

**Explanation:**

- **`replicas: 3`**: Increases the number of replicas to 3.
- **Environment Variable**: Sets `ENDPOINT` from `endpoint-configmap`.
- **Volume Mount**: Mounts `index-html-configmap` to `/usr/share/nginx/html/`.

### 2. `files/index.html` File

The content for the ConfigMap is stored in the `files/index.html` file:

```html
<html>
    <h1>Welcome</h1>
    <br/>
    <h1>Hi! This is the ConfigMap Index file</h1>
</html>
```

### 3. Overlay `service.yaml` File

The `service.yaml` in the overlay modifies the base service to be of type `NodePort`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: NodePort
  selector:
    app: web-service
  ports:
  - protocol: TCP
    port: 80
    nodePort: 30007
```

**Explanation:**

- **`type: NodePort`**: Exposes the service on a NodePort.
- **`nodePort: 30007`**: Specifies the NodePort number.

### 4. Overlay `kustomization.yaml` File

The `kustomization.yaml` file in the `overlays/generators` directory specifies how to generate the ConfigMaps and apply the patches:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patches:
- path: deployment.yaml
- path: service.yaml

generatorOptions:
  labels:
    app: web-service

configMapGenerator:
- name: index-html-configmap
  behavior: create
  files:
  - files/index.html
- name: endpoint-configmap
  literals:
  - endpoint=api.example.com/users
```

**Explanation:**

- **`resources`**: Includes resources from the base directory.
- **`patches`**: Applies the overlay `deployment.yaml` and `service.yaml` as patches to the base resources.
- **`generatorOptions`**: Adds the label `app: web-service` to generated resources.
- **`configMapGenerator`**: Specifies ConfigMaps to generate.

## Deploying the Application

### 1. Build and Apply with Kustomize

Run the following command to build and apply the resources:

```bash
kubectl kustomize overlays/generators | kubectl apply -f -
```

Use this command if you are in the root directory. If you are in the directory where the `kustomization.yaml` file is located, then you can simply use:

```bash
kubectl kustomize . | kubectl apply -f -
```

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/refs/heads/main/Kustomize/Lab%2004/images/image.png)

### 2. Verify the ConfigMaps

List the ConfigMaps to verify they have been created:

```bash
kubectl get configmaps
```

**Expected Output:**

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/refs/heads/main/Kustomize/Lab%2004/images/image-1.png)

*Note: The ConfigMap names have hashes appended to ensure uniqueness when the data changes.*

### 3. Access the Nginx Webpage

Since the deployment uses a NodePort service, you can access the Nginx webpage by finding the node IP.

To get the IP address of the node in a Kubernetes cluster, we can use the kubectl command-line tool to fetch this information. Here's how:

```bash
kubectl get nodes -o wide
```

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/refs/heads/main/Kustomize/Lab%2004/images/image-2.png)

#### Curl using NodePort

```bash
kubectl get svc
```

**Example Output:**

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/refs/heads/main/Kustomize/Lab%2004/images/image-3.png)

We can access the service through any of our Kubernetes cluster nodes' IP addresses, on port 30007.

```bash
curl http://<Node-IP>:30007
```

You should see the output displaying:

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/refs/heads/main/Kustomize/Lab%2004/images/image-4.png)

### 4. Check the Environment Variable

To verify that the environment variable `ENDPOINT` is set from the ConfigMap, execute the following command:

```bash
kubectl get pods
```

Get the name of one of the pods, then run:

```bash
kubectl exec -it <pod-name> -- env | grep ENDPOINT
```

Replace `<pod-name>` with the name of one of the Nginx pods.

**Expected Output:**

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/refs/heads/main/Kustomize/Lab%2004/images/image-5.png)

## Updating the ConfigMap

To test updating the ConfigMap through the generator, modify the `index.html` file.

### 1. Update `index.html`

Edit the `files/index.html` file to update its content:

```html
<html>
    <h1>Welcome</h1>
    <br/>
    <h1>Hi! This is the Updated ConfigMap Index file</h1>
</html>
```

### 2. Apply Changes with Kustomize

Apply the updated configuration:

```bash
kubectl kustomize overlays/generators | kubectl apply -f -
```

Use this command if you are in the root directory. If you are in the directory where the `kustomization.yaml` file is located, then you can simply use:

```bash
kubectl kustomize . | kubectl apply -f -
```

List the ConfigMaps to verify they have been created:

```bash
kubectl get configmaps
```

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/refs/heads/main/Kustomize/Lab%2004/images/image-6.png)

### 3. Prune Orphaned ConfigMaps

By default, Kustomize doesn't remove old ConfigMaps. We can see that the previous ConfigMap is not deleted. To prune orphaned ConfigMaps, use the `--prune` flag with the appropriate label selector:

```bash
kubectl kustomize overlays/generators | kubectl apply --prune -l app=web-service -f -
```

**Explanation:**

- **`--prune`**: Removes resources from the cluster that are not defined in the current configuration.
- **`-l app=web-service`**: Specifies the label selector to identify resources for pruning.

Now, List the ConfigMaps to verify previous ConfigMap has been deleted:

```bash
kubectl get configmaps
```

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/refs/heads/main/Kustomize/Lab%2004/images/image-7.png)

### 4. Verify the Update

After applying the changes, We can access the service through any of our Kubernetes cluster nodes' IP addresses, on port 30007.

```bash
curl http://<Node-IP>:30007
```

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/refs/heads/main/Kustomize/Lab%2004/images/image-8.png)

## Conclusion

In this tutorial, we've demonstrated how to generate ConfigMaps using Kustomize, deploy them in a Kubernetes cluster, and update them effectively.

**Key Takeaways:**

- **Base and Overlay Structure**: Understand how base configurations and overlays work together in Kustomize.
- **ConfigMap Generators**: Simplify the creation and management of ConfigMaps.
- **Hashed Names**: Ensure that updates to ConfigMaps trigger rollouts automatically.
- **Pruning**: Use the `--prune` flag to remove obsolete resources.

By leveraging Kustomize's powerful features, you can manage complex configurations more efficiently and keep your Kubernetes deployments organized.