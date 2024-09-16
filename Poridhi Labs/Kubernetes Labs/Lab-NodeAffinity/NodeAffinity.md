# NodeAffinity in Kubernetes

`NodeAffinity` is a scheduling feature in Kubernetes that allows us to constrain which nodes our pods are eligible to be scheduled on based on node labels. It allows us to specify rules that determine which nodes are suitable for your pods, helping ensure they are placed on nodes with certain desired characteristics.

![NodeAffinity](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-NodeAffinity/images/1.png?raw=true)

## Types of NodeAffinity

There are two types of NodeAffinity:

- RequiredDuringSchedulingIgnoredDuringExecution

- PreferredDuringSchedulingIgnoredDuringExecution

![NodeAffinity](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-NodeAffinity/images/2.png?raw=true)

## Task

We have a Kubernetes cluster with nodes labeled to indicate their geographic zones, such as zoneA and zoneB. We want to ensure that a particular pod is only scheduled on nodes within zoneA.

## Label Nodes

#### Get the `nodes` name:
```
Kubectl get nodes
```
![NodeAffinity](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-NodeAffinity/images/output-1.png?raw=true)

Label Node-1 with `zone=zoneA`:

```
kubectl label nodes <node-1> zone=zoneA
```

Label Node-2 with `zone=zoneB`:

```
kubectl label nodes <node-2> zone=zoneB
```

Replace `<node-1>` and `<node-2>`with the actual names of desired nodes.


## Create a Pod Specification with NodeAffinity

#### Pod Specification with NodeAffinity for zoneA (`zoneA-pod.yaml`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: zone-a-pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: zone
            operator: In
            values:
            - zoneA
  containers:
  - name: container-1
    image: nginx
```

#### Pod Specification with NodeAffinity for zoneB (`zoneB-pod.yaml`)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: zone-b-pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: zone
            operator: In
            values:
            - zoneB
  containers:
  - name: container-2
    image: nginx
```

![NodeAffinity](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-NodeAffinity/images/3.png?raw=true)

## Apply the Pod Specification

```
kubectl apply -f zoneA-pod.yaml
kubectl apply -f zoneB-pod.yaml
```
![NodeAffinity](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-NodeAffinity/images/output-2.png?raw=true)

## Verify the Pod Placement

After applying the pod specification, verify that the pod has been scheduled on a node labeled with `zone=zoneA` & `zone=zoneB`.

```
kubectl get pods -o wide
```

Check the NODE column to ensure that `zoneA-pod` is running on a node labeled `zone=zoneA` and `zoneB-pod` is running on a node labeled `zone=zoneB`

![NodeAffinity](https://github.com/Minhaz00/K8s-lab/blob/fazlul/Lab-NodeAffinity/images/output-3.png?raw=true)

