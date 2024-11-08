# Understading Persistent Volumes

A `Persistent Volume (PV)` in Kubernetes is a piece of storage in the cluster that has been provisioned by an administrator or dynamically provisioned using `StorageClasses`. PVs are resources in the cluster that provide storage to users and have a lifecycle independent of any individual pod that uses the PV. For instance, database data often needs to be retained beyond the application's lifecycle. This is the role of a persistent volume.

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab - PersistentVolumes/image/pvc_claim.png?raw=true" alt="" />

## key concepts about PersistentVolume

1. **PersistentVolumeClaim (PVC)**
     - A PVC is a request for storage by a user.
     - Users can request specific sizes and access modes (e.g., can be mounted once read-write or many times read-only).
     - PVCs are bound to PVs in a one to one relationship, and Kubernetes ensures that the requested storage is available and appropriately matched.

2. **Access Modes**: 
  Each PersistentVolume can express how it can be accessed using the attribute spec.accessModes.
     - `ReadWriteOnce (RWO)`: The volume can be mounted as read-write by a single node.
     - `ReadOnlyMany (ROX)`: The volume can be mounted as read-only by many nodes.
     - `ReadWriteMany (RWX)`: The volume can be mounted as read-write by many nodes.

  3. **Reclaim Policy**: 
  The reclaim policy specifies what should happen to a PersistentVolume object when the PersistentVolumeClaim is deleted
     - `Retain`: Manual reclamation of the resource.
     - `Recycle`: Basic scrub (rm -rf /thevolume/*).
     - `Delete`: Associated storage asset, such as AWS EBS, GCE PD, or Azure Disk, is deleted.

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab - PersistentVolumes/image/pv_claim2.png?raw=true" alt="" />


## Example task

Create a `Persistent Volume` name `db-pv` with capacity `1Gi` and path `/data/db`. Then create a `Persistent Volume Claim (PVC)` named `db-pvc` with a size of `256Mi` and access mode `ReadWriteOnce`.

### 1. Create PersistentVolumes

We can create a PersistenVolume object using yaml definition file `pv.yaml` of kind `PersistentVolume`.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: db-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data/db
```

```bash
kubectl create -f pv.yaml
```

To get information about PV, we can run

```bash
kubectl get pv
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab - PersistentVolumes/image/pv_status.png?raw=true" alt="" />

The status `Available` indicates that the object is ready to be claimed.

### 2. Create PersistentVolumeClaims (PVC)

Now we will create a yaml definition file `pvc.yaml` of kind `PersistentVolumeClaim` for PVC.

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: db-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ""
  resources:
    requests:
      storage: 256Mi
```

```bash
kubectl create -f pvc.yaml
```

After creating PVC we can get more information by these commands.

```bash
kubectl get pvc
```

```bash
kubectl describe pvc db-pvc
```

<img src="https://github.com/Minhaz00/K8s-lab/blob/yasin/Lab - PersistentVolumes/image/pvc_status.png?raw=true" alt="" />

Once a PersistentVolumeClaim (PVC) is created, if its status is `Bound`, it indicates a successful binding to a PersistentVolume (PV). But as of now it is not mounted to any pod. Thats why `Used by` attribute is showing `<none>`
We will do the pod mounting in the next lab.
