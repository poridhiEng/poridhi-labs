# Managing ConfigMaps and Secrets using Kustomize

This documentation provides a step-by-step guide to deploying an NGINX application using Kustomize to generate ConfigMaps and Secrets. We’ll also explore how to automatically roll out changes to the application when the ConfigMap or Secret is updated, and how to handle configuration management without needing to restart the pods manually.

---

## **Introduction to the Problem**

When you update a ConfigMap that is attached to a pod as a volume, the ConfigMap data is propagated automatically to the pod. However, the pod does not pick up the latest ConfigMap data in certain cases:

- If the pod gets environment variables from the ConfigMap.
- If the ConfigMap is mounted as a volume using a `subPath`.

In these situations, the application inside the pod will continue using the old ConfigMap data until the pod is restarted, because the pod is unaware of changes to the ConfigMap. 

This is where Kustomize ConfigMap and Secret generators come in. They automatically manage updates to ConfigMaps and Secrets, triggering pod rollouts when configuration changes.

---

## **How Kustomize ConfigMap/Secret Generator Works**

The Kustomize generator creates a ConfigMap or Secret with a unique name that includes a hash, ensuring updates trigger pod rollouts. Here’s the basic flow:

1. **ConfigMap/Secret Creation**: When a ConfigMap or Secret is generated using Kustomize, a hash is appended to the name (e.g., `app-configmap-7b58b6ct6d`).
2. **Update Handling**: When a ConfigMap or Secret is updated, Kustomize regenerates it with a new hash.
3. **Automatic Rollout**: Kustomize automatically updates the deployment to use the new ConfigMap/Secret, triggering a rollout, ensuring the application uses the latest configuration without manual intervention.

---

## **Base File Structure**

Here’s the structure of the `base` folder, which contains the basic deployment configuration files for the NGINX application:

```bash
nginx-kustomize
└── base
    ├── deployment.yaml
    ├── service.yaml
    └── kustomization.yaml
```

---

### **Step 1: Base Deployment Configuration**

In the base configuration, we define a simple NGINX deployment that uses a ConfigMap to load an HTML file (`index.html`) and an environment variable for the API endpoint.

#### **1.1 Deployment YAML** (`base/deployment.yaml`)

This file defines the NGINX deployment with ConfigMaps mounted as a volume and used as environment variables.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        volumeMounts:
        - name: nginx-config-volume
          mountPath: /usr/share/nginx/html
        env:
        - name: API_ENDPOINT
          valueFrom:
            configMapKeyRef:
              name: nginx-configmap
              key: api-endpoint
      volumes:
      - name: nginx-config-volume
        configMap:
          name: nginx-configmap
```

This deployment mounts a ConfigMap to the `/usr/share/nginx/html` directory (where the NGINX index file is served) and uses the environment variable `API_ENDPOINT` from the `nginx-configmap`.

---

#### **1.2 Service YAML** (`base/service.yaml`)

This file defines a service to expose the NGINX application.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  labels:
    app: nginx
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

---

#### **1.3 Kustomization YAML** (`base/kustomization.yaml`)

The Kustomization YAML file references the deployment and service files. It also generates the necessary ConfigMap.

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml

configMapGenerator:
  - name: nginx-configmap
    literals:
      - api-endpoint=api.example.com
```

This base configuration generates the `nginx-configmap`, which is used to set the API endpoint as an environment variable.

---

### **Step 2: Overlay Configuration for Customizing Environments**

In addition to the base configuration, you can define overlay environments (e.g., `dev`, `prod`, etc.) for further customization using Kustomize generators. For this tutorial, we’ll use a `generators` overlay that generates two ConfigMaps:

1. **`index-html-configmap`**: A ConfigMap that contains the `index.html` file to be mounted to NGINX.
2. **`endpoint-configmap`**: A ConfigMap that stores the API endpoint as a literal.

The overlay folder structure looks like this:

```bash
nginx-kustomize
└── overlays
    └── generators
        ├── deployment.yaml
        ├── kustomization.yaml
        └── files
            └── index.html
```

---

### **Step 3: Overlay Deployment Configuration**

#### **3.1 Deployment YAML** (`overlays/generators/deployment.yaml`)

The overlay deployment specifies how the generated ConfigMaps are used:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  template:
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

---

#### **3.2 Kustomization YAML** (`overlays/generators/kustomization.yaml`)

This Kustomization file generates the ConfigMaps and references the deployment.

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patches:
- path: deployment.yaml

generatorOptions:
  labels:
    app: web-service

configMapGenerator:
- name: index-html-configmap
  files:
  - files/index.html
- name: endpoint-configmap
  literals:
  - endpoint=api.example.com/users
```

---

### **Step 4: HTML Content for NGINX** (`overlays/generators/files/index.html`)

This is the HTML file that will be mounted by NGINX through the ConfigMap:

```html
<html>
  <h1>Welcome</h1>
  </br>
  <h1>Hi! This is the Configmap Index file </h1>
</html>
```

---

### **Step 5: Deploying with Kustomize**

To apply the deployment using Kustomize:

```bash
kustomize build overlays/generators | kubectl apply -f -
```

Once applied, you can check the ConfigMaps:

```bash
kubectl get cm
```

You’ll see ConfigMaps like `index-html-configmap-<hash>` and `endpoint-configmap-<hash>`, automatically generated by Kustomize.

---

### **Step 6: Update and Rollout**

To test the ConfigMap update, modify the `index.html` file:

```html
<html>
  <h1>Welcome</h1>
  </br>
  <h1>Hi! This is the Updated Configmap Index file </h1>
</html>
```

Run the following command to apply the updated ConfigMap and trigger the rollout:

```bash
kustomize build overlays/generators | kubectl apply -f -
```

---

### **Step 7: Garbage Collection**

To remove orphaned ConfigMaps (old ConfigMaps that are no longer referenced), use the `--prune` flag:

```bash
kustomize build overlays/generators | kubectl apply --prune -l app=web-service -f -
```

---

### **Disabling the Hashed ConfigMap**

If you don’t want Kustomize to append the hash to the ConfigMap names, you can disable it by adding the following option to the `kustomization.yaml`:

```yaml
generatorOptions:
  labels:
    app: web-service
  disableNameSuffixHash: true
```

Note that you will need to manually restart the pods for the changes to take effect when disabling the hash.

---

## **Generating Secrets with Kustomize**

You can generate secrets using the `secretGenerator` field in the Kustomization file. Here’s an example:

```yaml
secretGenerator:
- name: nginx-secret
  files:
  - files/secret.txt
```

For generating secrets from literals:

```yaml
secretGenerator:
- name: nginx-api-password
  literals:
  - password=myS3cret
```

Mount the secret as a volume or pass it as an environment variable

 in the deployment YAML file.

---

## **Conclusion**

Kustomize’s ConfigMap and Secret generators make configuration management simple and efficient by automatically handling updates and ensuring smooth rollouts. By leveraging this tool, you can make sure your NGINX application uses the latest configuration seamlessly, reducing the need for manual restarts and manual updates.

