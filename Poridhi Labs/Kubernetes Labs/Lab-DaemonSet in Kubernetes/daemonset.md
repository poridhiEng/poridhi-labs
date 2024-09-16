# Deploying a DaemonSet to Run a Pod on Every Node in a Kubernetes Cluster

## DaemonSet 

A DaemonSet in Kubernetes is a controller that ensures a specific pod runs on all (or selected) nodes in a cluster.When a new node is added to the cluster, the DaemonSet automatically adds the specified pod to the new node.When a node is removed, the pods managed by the DaemonSet on that node are cleaned up.

![DaemonSet](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-DaemonSet%20in%20Kubernetes/images/4.png?raw=true)

## Task:
Deploy a DaemonSet in a Kubernetes cluster to ensure a specific pod runs on all nodes, including master node, by using a YAML manifest file. The example will use an nginx container, and the deployment will demonstrate using tolerations to allow scheduling on control plane nodes.

## Create the DaemonSet Manifest File( `ds-demo.yaml1`)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: ds-demo
  labels:
    k8s-app: ds-demo
spec:
  selector:
    matchLabels:
      name: ds-demo
  template:
    metadata:
      labels:
        name: ds-demo
    spec:
      tolerations:
        - key: node-role.kubernetes.io/master
          operator: Exists
          effect: NoSchedule
      containers:
        - name: ds-demo
          image: nginx
```

![output-1](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-DaemonSet%20in%20Kubernetes/images/5.png?raw=true)

## Apply the DaemonSet Manifest

```
kubectl apply -f ds-demo.yaml
```

## Verify the DaemonSet Deployment

```
kubectl get pods
```
![output-1](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-DaemonSet%20in%20Kubernetes/images/2.png?raw=true)

```
kubectl get daemonset
```
This will return the list of all daemonsets in the current Kubernetes namespace. 

![](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-DaemonSet%20in%20Kubernetes/images/6.png?raw=true)

```
kubectl get pods -o wide
```
Check the NODE column to ensure that `ds-demo` pod is running on a every node include master-node.

![output-2](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-DaemonSet%20in%20Kubernetes/images/1.png?raw=true)

## CleanUp

```
kubectl delete -f ds-demo.yaml
```
This will delete the DaemonSet and clean up the resources.