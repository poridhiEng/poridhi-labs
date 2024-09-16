# Assign a pod (name demo, image=nginx) to a particular node using ``nodeName``.

## Task

The goal of this lab is to assign a Kubernetes pod with the name ``demo`` and using the ``nginx`` image to a specific node within the cluster.

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Scenario%206/images/node-05.PNG)

## Solution

Sometimes we need to assign a pod to a particular node in order to achieve optimal resource utilization. Certain nodes might have specific hardware or resources, like GPUs or high memory, which are required for specific workloads. Assigning pods to these nodes ensures optimal resource utilization.
We can use ``nodeName`` to assign a pod in a particular node. 

## Prerequisites

Install vim for creating/editing YAML files in the system.

```bash
sudo apt update
sudo apt install vim
``` 

## Create a Pod Manifest File 

Create a pod manifest using ``--dry-run`` and then add ``nodeName`` to the spec section.

```bash
kubectl run demo --image=nginx --dry-run=client -oyaml > pod.yaml
```

Now, we can see the ``pod.yaml`` file using ``cat pod.yaml``.

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Scenario%206/images/node-01.PNG)

We can observe that there is no ``nodeName`` field in the ``spec`` field. Now, we have to add ``nodename`` field in the ``pod.yaml`` file to assign this pod in a particular node.

## Find the Nodes in the Cluster

```bash
kubectl get nodes
```

The ``kubectl get nodes`` command is used to list all nodes in a Kubernetes cluster. This command displays the details of each node, such as its status, roles, age, and version of Kubernetes running on it. Here's how we typically use it and what the output looks like:

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Scenario%206/images/node-02.PNG)

There are three nodes in the cluster. Now, we will assign the ``pod.yaml`` pod in the ``worker-1`` node.

## Edit the Pod

In this step, we will edit the ``pod.yaml`` file and add ``nodeName`` in the ``spec`` field using vim.

```bash
vim pod.yaml
```
Now, watch the ``pod.yaml`` file using :

```bash 
cat pod.yaml
```

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Scenario%206/images/node-03.png)

Here, the name of the ``worker-1`` node is set as the value in the ``nodename`` field.

## Create the Pod

Apply the YAML file to create the pod in the specific node.

```bash
kubectl apply -f pod.yaml
```

Display additional information of the pod using:

```bash
kubectl get pods -owide
```

The command ``kubectl get pods -owide`` is used to list all pods in the current namespace, displaying additional information such as node name and IP address.

![alt text](https://raw.githubusercontent.com/Minhaz00/K8s-lab/nabil-branch/Scenario%206/images/node-04.png)

Here, we can see that the pod is running in the node ``cluster-uuynfg-worker-1`` as intended.

## Cleanup

To clean up the resources created in this lab, delete the pod using the following command:

```bash
kubectl delete -f pod.yaml
```

