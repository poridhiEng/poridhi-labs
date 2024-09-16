# Kubernetes Jobs: Overview and Usage


A **Kubernetes Job** is a resource designed to manage the execution of short-lived workloads. Unlike deployments or replica sets that are intended to keep applications running indefinitely, a Job ensures that a specified number of pods successfully complete their tasks.

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Jobs%20in%20kubernetes/images/image-5.png?raw=true" alt="" />

Kubernetes Jobs are designed for specific types of tasks that need to be completed and then finished. These tasks include batch processing, data analytics etc. They are also useful for automating tasks that need to be performed periodically or on a schedule.


## How Kubernetes Jobs Work
When you create a Kubernetes Job, it starts by creating one or more pods to do the tasks. Each pod runs its task until it finishes and then stops.

The Job monitors these pods to ensure the tasks are completed successfully. If a pod fails, the Job creates a new one to finish the task.

Once a pod completes its task successfully, it is not restarted. This is different from deployments, where pods keep running. This approach makes sure tasks are done efficiently without unnecessary restarts. The pods are created one after another.

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Jobs%20in%20kubernetes/images/image-1.png?raw=true" alt="" />

## Task: Create and Verify a Job

We'll create a Job that runs a single pod to perform a simple task. We'll ensure it completes successfully and check the output.

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Jobs%20in%20kubernetes/images/image-4.png?raw=true" alt="" />

We will create a job named `single-pod-job`. The job runs `one` pod, which contains a container named `busybox` with the `busybox` image. The container executes the command `"echo Hello, Kubernetes Jobs!"`. The job has a restart policy of `Never`.


## Creating a Job


Create a file named `single-job.yaml` with the following content:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: single-pod-job
spec:
  template:
    spec:
      containers:
      - name: busybox
        image: busybox
        command: ["echo", "Hello, Kubernetes Jobs!"]
      restartPolicy: Never
```


Use the following command to create the Job:

```bash
kubectl create -f single-job.yaml
```

## Verifying the Job

Check the status of the Job to ensure it was created and completed successfully:
```bash
kubectl get jobs
```

Verify that the pod has completed successfully:
```bash
kubectl get pods
```

View the logs of the completed pod to see the output:
```bash
kubectl logs <pod-name>
```

Expected otuput:

<img src="https://github.com/Minhaz00/K8s-lab/blob/Minhaz/Lab%20-%20Jobs%20in%20kubernetes/images/image-2.png?raw=true" alt="" />

The Job named `single-pod-job` was created and has successfully completed its task.
The pod created by this Job has finished its task and is in a `Completed` state.
The output from the pod's task is `Hello, Kubernetes Jobs!`, which can be seen using the logs command. 
After executing the task the pod stoped automatically.


