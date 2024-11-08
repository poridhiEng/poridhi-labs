# Kuberenetes StorageClass

In Kubernetes, a `StorageClass` provides a way to describe the "classes" of storage available for use in a cluster. Typical characteristics of a storage can be the type (e.g., fast SSD storage versus a remote cloud storage or the backup policy for a storage). The storage class is used to provision a PersistentVolume dynamically based on its criteria.

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/lab-StorageClass/image/sc.png?raw=true" />

Most Kubernetes cloud providers come with a list of existing provisioners. Minikube already creates a default storage class named `standard` which we can see by the following command

```bash
kubectl get storageclass
```
<details>
  <summary>Key Concepts about StorageClass</summary>
  
  1. **Dynamic Provisioning**:
     - `StorageClass` is used to enable dynamic provisioning of PersistentVolumes (PVs). When a PersistentVolumeClaim (PVC) requests storage, the associated `StorageClass` provisions the PV automatically.

  2. **Attributes**:
     - `provisioner`: This field specifies the type of the provisioner to use (e.g., `kubernetes.io/aws-ebs` for AWS Elastic Block Store, `kubernetes.io/gce-pd` for Google Compute Engine Persistent Disks).
     - `parameters`: These are key-value pairs that are passed to the provisioner and can include details such as disk type, replication factor, or other provider-specific attributes.
     - `reclaimPolicy`: This determines what happens to the PV when a PVC is deleted. Common values are `Retain`, `Recycle`, and `Delete`.
     - `volumeBindingMode`: This specifies when volume binding and dynamic provisioning should occur. Possible values are `Immediate` and `WaitForFirstConsumer`.

</details>

## 1. Create a StorageClass:

Storage classes can be created declaratively only with the help of a YAML manifest file `sc.yaml`. At a minimum, we need to declare the provisioner. All other attributes are optional.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  replication-type: regional-pd
```

Here,

- **`provisioner`**: Specifies the storage provider, in this case, GCE Persistent Disks.
- **`parameters`**: Defines the type of storage (e.g., SSD).

For example we can save the YAML contents in the `sc.yaml` file. Then run the following command to create the storageClass object.

```bash
kubectl apply -f sc.yaml
```

We can list the storageClass by the following command:

```bash
kubectl get storageclass
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/lab-StorageClass/image/create-sc.png?raw=true" />

## 2. Using the Storage Classes

Provisioning a PersistentVolume dynamically requires the assignment of the `storageClass` during the creation of `PeristentVolumeClaim`.

### Creating a PersistentVolumeClaim to use a storage class

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 512Mi
  storageClassName: standard
```

```bash
kubectl apply -f pvc.yaml
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/lab-StorageClass/image/create-pvc.png?raw=true" />

- **`storageClassName`**: Specifies that this PVC should use the `standard` StorageClass.

A corresponding `PersistentVolume` object will be created only if the storage class can provision an appropriate PersistentVolume through its `provisioner`. It's crucial to note that Kubernetes does not generate an `error or warning message` if this does not happen. In the next lab, we will mount a pvc to a pod.