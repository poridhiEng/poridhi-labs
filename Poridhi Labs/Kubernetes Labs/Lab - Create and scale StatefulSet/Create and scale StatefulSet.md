# Create and scale a StatefulSet in kubernetes 

A **StatefulSet** is a Kubernetes resource used for managing stateful applications. It is similar to Deployment. But, unlike Deployments, which manage stateless applications, StatefulSets are designed to manage applications that require states. It is used in case of stateful applications such as Databases.

Pods are created, scaled and deleted in a specific, ordered sequence. This ensures that each Pod is created one at a time, waiting for the previous one to be ready before proceeding to the next. This sequential deployment allows for orderly initialization and orchestration of stateful applications.

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Create%20and%20scale%20StatefulSet/images/image.png?raw=true" alt="" />

Each pod has a unique, stable network identity or name and persistent storage that remains consistent across  restarts. This is achieved through a deterministic naming scheme based on the ordinal index of the Pod (e.g., mysql-0, mysql-1).

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Create%20and%20scale%20StatefulSet/images/image-1.png?raw=true" alt="" />
 
## Task

We have to create a StatefulSet with following configuration: 
- Name:  `nginx-statefulset`
- Set the  serviceName to `nginx`
- Set the replicas to `three`
- Use the `nginx:latest` image

Then, scale the StatefulSet to `five` replicas and verify the StatefulSet and Pods.


## Create a StatefulSet
We will create a StatefulSet definition file `statefulset-definition.yaml`. We can use `vim` editor to open the file.

```bash
vim statefulset-definition.yaml
```

Write the StatefulSet definition given below:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: nginx-statefulset
spec:
  selector:
    matchLabels:
      app: nginx
  serviceName: "nginx"
  replicas: 3
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
```

Run the following command to apply this manifest:

```bash
kubectl create -f statefulset-definition.yaml
```


## Verify the StatefulSet and Pods

Use the following command to see the created StatefulSet and Pods:

```bash
kubectl get statefulset
kubectl get pods
```

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Create%20and%20scale%20StatefulSet/images/image-2.png?raw=true" alt="" />

## Scale the StatefulSet

Scaling a StatefulSet is similar to scaling a Deployment. We have to scale the StatefulSet to five replicas. Use the following command to scale:

```bash
kubectl scale statefulset nginx-statefulset --replicas=5
```

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Create%20and%20scale%20StatefulSet/images/image-3.png?raw=true" alt="" />

This will do the task.


## Verify the StatefulSet and Pods

Use the following commands again to see the created StatefulSet and Pods:

```bash
kubectl get statefulset
kubectl get pods
```

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Create%20and%20scale%20StatefulSet/images/image-4.png?raw=true" alt="" />


## Check the Stable identity of a Pod (Optional)

We can check it by deleting a pod. The StatefulSet will create another pod with the same identity/name.

Here we are deleting the pod `nginx-statefulset-1`:
```bash
kubectl delete pod nginx-statefulset-1
```

Now if check the pods again we will see we still have 5 pods running with the same name. The StatefulSet created the pod `nginx-statefulset-1` again with the same name:

```bash
kubectl get pods
```

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Create%20and%20scale%20StatefulSet/images/image-5.png?raw=true" alt="" />
