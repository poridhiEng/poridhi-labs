# Editing a Kubernetes Pod

In this lab, we will learn how to edit a Kubernetes pod. It's important to note that certain specifications of an existing pod cannot be edited directly. 

The editable fields include:
- spec.containers[*].image
- spec.initContainers[*].image
- spec.activeDeadlineSeconds
- spec.tolerations

We cannot edit environment variables, service accounts, resource limits, and some other fields of a running pod. If we need to make such changes, there are two methods we can use to update the pod configuration.

## Task
Delete and recreate the pod with the modified configuration. At first we need to create a new pod. Use the following command to create a pod:

```bash
kubectl run my-nginx --image=nginx:1.26 --port=80
```

## Export the Pod Definition and Edit

1. Extract the pod definition in YAML format:

    ```bash
    kubectl get pod my-nginx -o yaml > my-new-pod.yaml
    ```


2. Edit the exported file:

    Open the file in an editor (e.g. vim editor).
    
    ```bash
    vim my-new-pod.yaml
    ```

3. Make the necessary changes. For example, change the image:

    ```yaml
    spec:
      containers:
      - name: nginx
        image: nginx:latest
    ```

    Save the changes and exit the editor.

4. We can view the changes using: (optional)

    ```bash
    cat my-new-pod.yaml
    ```
    In the `spec` section we can see the following changes:

    <img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Editing%20a%20kubernetes%20pod/images/image.png?raw=true" alt="" />

4. Delete the existing pod:

    ```bash
    kubectl delete pod my-nginx
    ```

5. Create a new pod with the edited file:

    ```bash
    kubectl create -f my-new-pod.yaml
    ```


## Verification

- Check the status of the new pod:
    ```bash
    kubectl get pods
    ```
    Ensure the new pod is running.

    Expected output:

    <img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Editing%20a%20kubernetes%20pod/images/image-1.png?raw=true" alt="" />

- Describe the new pod to verify the changes:
    ```bash
    kubectl describe pod my-nginx
    ```
    Confirm that the changes have been applied successfully.

    Expected output:

    <img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Editing%20a%20kubernetes%20pod/images/image-2.png?raw=true" alt="" />

