# Detail setup of storage in kubernetes using PersistentVolume

## Task

1. Create a PersistentVolume named `logs-pv` that maps to the hostPath /tmp/logs. The access mode should be `ReadWriteOnce` and `ReadOnlyMany`. Provision a storage capacity of `2Gi`. Assign the reclaim policy `Delete` and an `empty string` as the storage class. Ensure that the status of the PersistentVolume shows `Available`.

2. Create a PersistentVolumeClaim named `logs-pvc`. The access it uses is `ReadWriteOnce`. Request a capacity of `1Gi`. Ensure that the status of the PersistentVolume shows `Bound`.

3. Mount the PersistentVolumeClaim in a Pod running the image `nginx` at the mount path `/var/log/nginx`.

4. Open an interactive shell to the container and create a new file named `mynginx`. log in `/var/log/nginx`. Exit out of the Pod.

## Steps

Here is the overview of what we are intended to do in this lab.

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab - PersistentVolumeTask/image/overall-steps.png?raw=true" alt="" />

## 1. Create the PersistentVolume

We wil start by creating the PV named `logs-pv`. To do that we will define a yaml definition file of name `logs-pv.yaml`.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: logs-pv
spec:
  capacity:
    storage: 2Gi
  accessModes:
    - ReadWriteOnce
    - ReadOnlyMany
  persistentVolumeReclaimPolicy: Delete
  storageClassName: ""
  hostPath:
    path: /tmp/logs
```

Now create the PersistentVolume object and check on its status:

```bash
kubectl create -f logs-pv.yaml
```
```bash
kubectl get pv
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab - PersistentVolumeTask/image/task-createpv.png?raw=true" alt="" />

Here the status `Available` indicates that the object is ready to be claimed.

## 2. Create the PersistentVolumeClaim

Now we will create the file `logs-pvc.yaml` to define the PersistentVolumeClaim. The following YAML manifest shows its contents:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: logs-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ""
  resources:
    requests:
      storage: 1Gi
```

Create the PersistentVolumeClaim object and check on its status:

```bash
kubectl create -f logs-pvc.yaml
```
```bash
kubectl get pvc
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab - PersistentVolumeTask/image/task-create-pvc.png?raw=true" alt="" />

Once a PersistentVolumeClaim (PVC) is created, if its status is `Bound`, it indicates a successful binding to a PersistentVolume (PV).

## 3. Create the Pod

Next we have to create the file `nginx-pod.yaml` to define the pod and bind the PersistentVolumeClaim `logs-pvc` to it.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    run: nginx
spec:
  volumes:
    - name: logs-volume
      persistentVolumeClaim:
        claimName: logs-pvc
  containers:
    - name: nginx
      image: nginx
      volumeMounts:
        - mountPath: "/var/log/nginx"
          name: logs-volume
  dnsPolicy: ClusterFirst
  restartPolicy: Never
```

Create the Pod using the following command and check its status:
```bash
kubectl create -f nginx-pod.yaml
```
```bash
kubectl get pods
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab - PersistentVolumeTask/image/task-create-pod.png?raw=true" alt="" />

## 4. Exec the pod and create a file

Now we can go ahead and open an interactive shell to the Pod. Navigating to the mount path at `/var/log/nginx` gives the access to the underlying PersistentVolume:

```bash
kubectl exec nginx -it -- /bin/sh
cd /var/log/nginx
touch my-nginx.log
ls
```
Exit the pod:
```bash
exit
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab - PersistentVolumeTask/image/task-exec.png?raw=true" alt="" />