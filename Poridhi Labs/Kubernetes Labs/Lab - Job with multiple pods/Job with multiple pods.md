# Deploy a Kubernetes Job with Multiple Pods


In Kubernetes, a Job can run multiple pods in parallel to complete a task. The `parallelism` setting determines how many pods run at the same time, while the `completions` setting specifies how many successful completions are needed. 

Each pod does the same tasks independently, and the Job is complete once the specified number of successful completions is reached. Pods are not restarted if they fail when the restartPolicy is set to "Never". This approach ensures efficient task completion by utilizing multiple pods simultaneously.


## Task: Create and Verify a Job with Multiple Pods

Create a Kubernetes Job configuration named `multi-pod-job` to execute a specific command concurrently across `three` pods which contains a container named `busybox` with the `busybox` image. 

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Job%20with%20multiple%20pods/images/image-1.png?raw=true" alt="" />


Ensure that each pod prints the message `Hello, Kubernetes Jobs with multiple pods!`.

## 

Create a file named `multi-job.yaml` with the following content:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: multi-pod-job
spec:
  completions: 3
  parallelism: 3
  template:
    spec:
      containers:
      - name: busybox
        image: busybox
        command: ["echo", "Hello, Kubernetes Jobs with multiple pods!"]
      restartPolicy: Never
```

Run the following command to create the Job:

```bash
kubectl create -f multi-job.yaml
```

This YAML configuration describes a Kubernetes Job named `multi-pod-job` that needs to complete `three` times and runs `three` pods at the same time. Each pod executes the command to print `Hello, Kubernetes Jobs with multiple pods!`. The Job ensures that if any pod fails, it won't be restarted, maintaining the desired number of completions.


## Verifying the Job

Check the status of the Job to ensure it was created and the required number of pods completed successfully:

```bash
kubectl get jobs
```

Verify that the pods have completed successfully:

```bash
kubectl get pods
```

View the logs of each completed pod to see the output:

```bash
kubectl logs <pod-name-1>
kubectl logs <pod-name-2>
kubectl logs <pod-name-3>
```

Expected output:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20Job%20with%20multiple%20pods/images/image.png?raw=true" alt="" />

## Clean Up

Run the following commands to delete the Jobs created during this lab:

```bash
kubectl delete job multi-pod-job
```