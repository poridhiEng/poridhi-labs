
### **Test Network Interface Configuration**

1. **Create and deploy the following YAML configuration file** (`deploy.yaml`):

   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: nginx-worker-1
   spec:
     containers:
     - name: nginx
       image: nginx
       ports:
       - containerPort: 80
     nodeSelector:
       kubernetes.io/hostname: worker-1
   ---
   apiVersion: v1
   kind: Pod
   metadata:
     name: bash-worker-1
   spec:
     containers:
     - name: ubuntu
       image: smatyukevich/ubuntu-net-utils
       command:
         - "/bin/bash"
         - "-c"
         - "sleep 10000"
     nodeSelector:
       kubernetes.io/hostname: worker-1
   ---
   apiVersion: v1
   kind: Pod
   metadata:
     name: nginx-worker-2
   spec:
     containers:
     - name: nginx
       image: nginx
       ports:
       - containerPort: 80
     nodeSelector:
       kubernetes.io/hostname: worker-2
   ---
   apiVersion: v1
   kind: Pod
   metadata:
     name: bash-worker-2
   spec:
     containers:
     - name: ubuntu
       image: smatyukevich/ubuntu-net-utils
       command:
         - "/bin/bash"
         - "-c"
         - "sleep 10000"
     nodeSelector:
       kubernetes.io/hostname: worker-2
   ```

2. **Deploy the YAML configuration**:

   Run the following command to deploy the pods using the `deploy.yaml` file:

   ```bash
   kubectl apply -f deploy.yaml
   ```

3. **Check the status of the pods**:

   Once the pods are deployed, check their status and observe that they have not been assigned IP addresses yet:

   ```bash
   kubectl get pods -o wide
   ```

   **Expected output**:  
   The pods will be listed, but you will notice that they **do not have any IP addresses** assigned yet, which confirms that the IP assignment part of the CNI has not been implemented at this stage. The pod's status might show "Pending" or "Running" without an IP.


