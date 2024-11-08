# Scenario 5 - Labels and Selectors

## Task
Assign a label to a node `CKA=true` and then create a pod `name=demo` `image=nginx`
and assign it to the node with the label you created. Then again assign a label to another node `CKA=false` and then create a pod `name=demo-1` with `image=nginx`

## Solution

To solve this task we need to perform two step:
1. Create a label for each node.
2. Create pods that has a node selector matching the label.

### Step 01

First, we will label the node. To get the avaible nodes we can run the command

```bash
kubectl get nodes
```

Here, we can see we have two worker node available. Now we can label the two nodes. For the first node

```bash
kubectl label nodes your-node-name CKA=true
```
<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab%20-%20Scenario%205%20-%20Labels%20and%20Selectors/image/get%20nodes.png?raw=true" />

For the second node

```bash
kubectl label nodes your-node-name CKA=false
```

Now we can check if we have successfully labeled the nodes.

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab%20-%20Scenario%205%20-%20Labels%20and%20Selectors/image/get%20nodes%202.png?raw=true" />

### Step 02: Create pod with a nodeSelector?

We can create a pod manifest using `--dry-run` then use the NodeSelector.
This YAML file will specify that the pod should only be scheduled on nodes with the label CKA=true.

```bash
kubectl run demo --image=nginx --dry-run=client -oyaml > pod.yaml
```


<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab%20-%20Scenario%205%20-%20Labels%20and%20Selectors/image/pod%20yaml.png?raw=true" />

Now we can edit the file using and add the NodeSelector. The file should look like this

```yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: demo
  name: demo
spec:
  nodeSelector:
    CKA: "true"
  containers:
  - image: nginx
    name: demo
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```

Apply the manifest

```bash
kubectl apply -f pod.yaml
```

Then create the second pod as well in the same way. 

```bash
kubectl run demo-2 --image=nginx --dry-run=client -o yaml > pod.yaml
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab%20-%20Scenario%205%20-%20Labels%20and%20Selectors/image/pod%20yaml%202.png?raw=true" />

The yaml file will look like this. Edit the file and add the nodeSelector
```bash
vim pod.yaml
```
```yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    run: demo-2
  name: demo-2
spec:
  nodeSelector:
    CKA: "false"
  containers:
  - image: nginx
    name: demo-2
    resources: {}
  dnsPolicy: ClusterFirst
  restartPolicy: Always
status: {}
```

### Check the pod status

Now to see check the status of pod creation, we can run

```bash
kubectl get pods -o wide
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab%20-%20Scenario%205%20-%20Labels%20and%20Selectors/image/get%20pods%202.png?raw=true" />

here, we can see that each pod is running on the its respective node that we labeled.