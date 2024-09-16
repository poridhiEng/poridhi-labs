# Understanding Network Policy in Kubernetes

Network policies in Kubernetes control the communication between pods, namespaces, and external IPs. 

By default, all pods in a Kubernetes cluster can communicate with each other. 

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image.png?raw=true" alt="" />

However, with network policies, we can restrict or allow specific types of traffic. A network policy is a set of rules that define how pods communicate with each other and with other network endpoints. We can think of it like a firewall for our Kubernetes pods. When we create a network policy for a pod, it defines what traffic is allowed to come into (ingress) or go out from (egress) the pod. 

Here is an example where we have added a policy for a pod in `ns-2`. Ingress traffic is allowed from the same namespace but not from pods in other namespaces.

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-1.png?raw=true" alt="" />

## Task

We will create two namespaces and a pod in each namespace. We also need a pod in the default namespace.

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-2.png?raw=true" alt="" />

Here is the configuration:

- Namespace: `default`
  
  Pod: `demo-app-0`

- Namespace: `ns-1`
  
  Pod : `demo-app-1`

- Namespace: `ns-2`
  
  Pod : `demo-app-2`

Then we will:
- Verify Initial Communication
- Create Network Policy to deny all communication in `ns-2`
- Verify Communication After Policy
- Create Network Policy to allow communication in `ns-2` only from `ns-1`
- Verify Communication After Policy


## Create namespaces and pods

Create the required namespaces and pods with specified image and namespace using the following commands:

```bash
kubectl create namespace ns-1
kubectl create namespace ns-2

kubectl run demo-app-0 --image=nginx
kubectl run demo-app-1 --image=nginx --namespace=ns-1
kubectl run demo-app-2 --image=nginx --namespace=ns-2
```

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-3.png?raw=true" alt="" />

Let's see the pod details in `ns-1` and `ns-2`:

```bash
kubectl get pods -owide -n ns-1
kubectl get pods -owide -n ns-2
```

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-5.png?raw=true" alt="" />


## Verify Initial Communication

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-18.png?raw=true" alt="" />

Run the following commands to verify the initial communication between `demo-app-1` and `demo-app-2`:

```bash
kubectl exec -it demo-app-1 -n ns-1 -- curl 10.42.1.6:80
```

Here, `10.42.1.6` is the IP address of the `demo-app-2` in my case. 

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-6.png?raw=true" alt="" />

We can also try connecting pod `demo-app-0` to `demo-app-2`: 

```bash
kubectl exec -it demo-app-0 -- curl 10.42.1.6:80
```

We will get the same result here as well. So, the connections works fine from any pod to a pod in `ns-2`.

## Create Network Policy to Deny All Communication

Create the `deny_all_connection.yaml` network policy with below content:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
    name: deny-all-connection
    namespace: ns-2
spec:
    podSelector: {}
    policyTypes:
    - Ingress
 ```

This is a Network Policy that is applied to all pods in the `ns-2` namespace because the `podSelector` is empty braces. The `policyTypes` is the `ingress` policy and since we have not defined any ingress rules so this policy effectively denies all incoming traffic to all pods in the `ns-2` namespace.



Use the following command to apply the policy:

```bash
kubectl create -f deny_all_connection.yaml
 ```

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-7.png?raw=true" alt="" />

## Verify Communication After Policy

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-17.png?raw=true" alt="" />

Run the following commands to verify the communication between `demo-app-1` and `demo-app-2` after we set up the network policy:

```bash
kubectl exec -it demo-app-1 -n ns-1 -- curl 10.42.1.6:80
```



Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-8.png?raw=true" alt="" />

We are not able to connect as before.

We can also try connecting pod `demo-app-0` to `demo-app-2`: 

```bash
kubectl exec -it demo-app-0 -- curl 10.42.1.6:80
```

We will get the same result here as well. So, the connections has been denied for `demo-app-2`.


## Create Network Policy to Allow connections from ns-1

Now let’s create the Network policy that allows ingress traffic from pods in `ns-1` namespace. That means we can connect from `demo-app-1` to `demo-app-2` but we can't connect `demo-app-0` to `demo-app-2`.

Create the `accept_ns1_connection.yaml` network policy with below content:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: accept-from-ns-1
  namespace: ns-2
spec:
  podSelector: {}
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: ns-1
    ports:
    - protocol: TCP
      port: 80
```

Delete the previous network policy applied to `demo-app-2`:

```bash
kubectl delete networkpolicies -n ns-2 --all
```

Now create the new network policy for `demo-app-2`:

```bash
kubectl create -f accept_ns1_connection.yaml
```

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-9.png?raw=true" alt="" />





## Verify Communication After Policy

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-16.png?raw=true" alt="" />

Run the following commands to verify the communication between `demo-app-1` and `demo-app-2` after we set up the network policy:

```bash
kubectl exec -it demo-app-1 -n ns-1 -- curl 10.42.1.6:80
```



Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-11.png?raw=true" alt="" />

We are able to connect the `demo-app-1` and `demo-app-2` due to the new network policy.

Now, let's try to connect pod `demo-app-0` in `default` namespace to `demo-app-2`: 

```bash
kubectl exec -it demo-app-0 -- curl 10.42.1.6:80
```

We will get the same result here as well. So, the connections has been denied for `demo-app-2`.

Here is the output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Network%20policy/images/image-12.png?raw=true" alt="" />

So, We can see that, we can not connect to the pod in `ns-2` from `default` namespace but we can connect to the pod in `ns-2` from `ns-1` namespace. That's how network policy works!