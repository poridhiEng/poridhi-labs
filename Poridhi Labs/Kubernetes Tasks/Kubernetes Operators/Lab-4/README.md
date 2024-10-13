# Implementing the Controller for the VPC Resource

## Overview

In this lab, you will define and create a Custom Resource Definition (CRD) for a Virtual Private Cloud (VPC) resource in a Kubernetes cluster, and then implement the controller logic to automate the creation, deletion, and management of the VPC resources.


### Initialize a New Kubebuilder Project

1. **Create a new project directory for the VPC Operator**:
   ```bash
   mkdir vpc-operator
   cd vpc-operator
   ```
   *Creates a new directory and navigates into it.*

2. **Initialize the Kubebuilder project**:
   ```bash
   kubebuilder init --domain network.example.com --repo github.com/your-username/vpc-operator
   ```
   *Sets up the project structure and configuration for a new Kubebuilder project.*

### Create a New API and Resource for VPC

1. **Create a new API for the VPC resource**:
   ```bash
   kubebuilder create api --group networking --version v1alpha1 --kind VPC
   ```
   *Generates the API and controller scaffolding for the VPC resource.*

2. **Generate the initial code and manifests**:
   ```bash
   make generate
   make manifests
   ```
   *Generates code and Kubernetes manifests based on the API definitions.*

### Define the VPC Custom Resource Schema

1. **Open the `api/v1alpha1/vpc_types.go` file** and define the `VPCSpec` and `VPCStatus` structs:

   ```go
   package v1alpha1

   import (
       metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
   )

   // VPCSpec defines the desired state of VPC
   type VPCSpec struct {
       CIDR    string   `json:"cidr,omitempty"`
       Region  string   `json:"region,omitempty"`
       Subnets []string `json:"subnets,omitempty"`
   }

   // VPCStatus defines the observed state of VPC
   type VPCStatus struct {
       State string `json:"state,omitempty"`
   }

   //+kubebuilder:object:root=true
   //+kubebuilder:subresource:status

   // VPC is the Schema for the VPC API
   type VPC struct {
       metav1.TypeMeta   `json:",inline"`
       metav1.ObjectMeta `json:"metadata,omitempty"`

       Spec   VPCSpec   `json:"spec,omitempty"`
       Status VPCStatus `json:"status,omitempty"`
   }

   //+kubebuilder:object:root=true

   // VPCList contains a list of VPC
   type VPCList struct {
       metav1.TypeMeta `json:",inline"`
       metav1.ListMeta `json:"metadata,omitempty"`
       Items           []VPC `json:"items"`
   }

   func init() {
       SchemeBuilder.Register(&VPC{}, &VPCList{})
   }
   ```
   *Defines the schema for the VPC custom resource, including its desired state (`VPCSpec`) and observed state (`VPCStatus`).*

2. **Save the file** and regenerate the code and manifests:
   ```bash
   make generate
   make manifests
   ```
   *Updates the generated code and manifests to reflect changes in the resource schema.*

### Deploy the VPC Custom Resource Definition (CRD)

1. **Build and install the CRD in the cluster**:
   ```bash
   make install
   ```
   *Installs the CRD into the Kubernetes cluster, making the new resource type available.*

2. **Verify that the CRD has been installed**:
   ```bash
   kubectl get crds
   ```
   *Lists all CRDs in the cluster to confirm the VPC CRD is installed.*

### Create a Sample VPC Resource

1. **Create a YAML file named `vpc-sample.yaml`** with the following content:

   ```yaml
   apiVersion: networking.network.example.com/v1alpha1
   kind: VPC
   metadata:
     name: dev-vpc
     namespace: default
   spec:
     cidr: 10.0.0.0/16
     region: us-west-2
     subnets:
       - 10.0.1.0/24
       - 10.0.2.0/24
   ```
   *Defines a sample VPC resource with specific CIDR, region, and subnets.*

2. **Apply the VPC custom resource** to the cluster:
   ```bash
   kubectl apply -f vpc-sample.yaml
   ```
   *Creates the VPC resource in the cluster based on the YAML definition.*

3. **Check the status of the created VPC resource**:
   ```bash
   kubectl get vpc dev-vpc -o yaml
   ```
   *Displays the details of the created VPC resource.*

### Implement the Controller Logic

1. **Open the `controllers/vpc_controller.go` file** and replace the content with the following code:

   ```go
   package controller

   import (
       "context"
       "fmt"
       "github.com/go-logr/logr"
       "sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
       "sigs.k8s.io/controller-runtime/pkg/reconcile"
       
       networkingv1alpha1 "github.com/your-username/vpc-operator/api/v1alpha1"
       "k8s.io/apimachinery/pkg/runtime"
       ctrl "sigs.k8s.io/controller-runtime"
       "sigs.k8s.io/controller-runtime/pkg/client"
   )

   // VPCReconciler reconciles a VPC object
   type VPCReconciler struct {
       client.Client
       Log    logr.Logger
       Scheme *runtime.Scheme
   }

   // Reconcile is the main logic for the controller
   func (r *VPCReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
       log := r.Log.WithValues("vpc", req.NamespacedName)

       // Fetch the VPC instance
       var vpc networkingv1alpha1.VPC
       if err := r.Get(ctx, req.NamespacedName, &vpc); err != nil {
           log.Error(err, "unable to fetch VPC")
           return ctrl.Result{}, client.IgnoreNotFound(err)
       }

       // Define the desired state of the VPC
       desiredState := fmt.Sprintf("CIDR: %s, Region: %s, Subnets: %v", vpc.Spec.CIDR, vpc.Spec.Region, vpc.Spec.Subnets)

       // Check if the VPC is marked for deletion
       if !vpc.DeletionTimestamp.IsZero() {
           log.Info("VPC is marked for deletion", "Name", vpc.Name)
           return ctrl.Result{}, nil
       }

       // Implement your VPC creation logic here
       // For demo purposes, we'll just log the desired state
       log.Info("Creating/Updating VPC", "Desired State", desiredState)

       // Update the VPC status to reflect changes
       vpc.Status.State = "Available"
       if err := r.Status().Update(ctx, &vpc); err != nil {
           log.Error(err, "unable to update VPC status")
           return ctrl.Result{}, err
       }

       // Ensure the VPC has a finalizer for cleanup during deletion
       if !controllerutil.ContainsFinalizer(&vpc, "vpc.finalizers.networking.example.com") {
           controllerutil.AddFinalizer(&vpc, "vpc.finalizers.networking.example.com")
           if err := r.Update(ctx, &vpc); err != nil {
               log.Error(err, "unable to add finalizer to VPC")
               return ctrl.Result{}, err
           }
       }

       return ctrl.Result{}, nil
   }

   // SetupWithManager sets up the controller with the Manager
   func (r *VPCReconciler) SetupWithManager(mgr ctrl.Manager) error {
       return ctrl.NewControllerManagedBy(mgr).
           For(&networkingv1alpha1.VPC{}).
           Complete(r)
   }
   ```
   *Implements the reconciliation logic for the VPC resource, including fetching the resource, logging its desired state, updating its status, and managing finalizers.*

2. **Save the file**.

### Build and Deploy the VPC Operator

1. **Build the Docker image** for your operator:
   ```bash
   make docker-build IMG=your-username/vpc-operator:latest
   ```
   *Compiles the operator code into a Docker image.*

2. **Push the Docker image** to DockerHub:
   ```bash
   docker push your-username/vpc-operator:latest
   ```
   *Uploads the Docker image to a container registry.*

3. **Deploy the operator** in your cluster:
   ```bash
   make deploy IMG=your-username/vpc-operator:latest
   ```
   *Deploys the operator to the Kubernetes cluster.*

4. **Verify the operator deployment**:
   ```bash
   kubectl get pods -n vpc-operator-system
   ```
   *Checks that the operator pod is running in the cluster.*

### Test the VPC Controller

1. **Update the `vpc-sample.yaml`** file with new subnets or CIDR, and reapply:
   ```bash
   kubectl apply -f vpc-sample.yaml
   ```
   *Applies changes to the VPC resource to test the controller's response.*

2. **Check the status of the `VPC` resource**:
   ```bash
   kubectl get vpc dev-vpc -o yaml
   ```
   *Verifies that the VPC resource's status has been updated by the controller.*

### Clean Up

1. **Delete the VPC resource**:
   ```bash
   kubectl delete -f vpc-sample.yaml
   ```
   *Removes the VPC resource from the cluster.*

2. **Uninstall the operator**:
   ```bash
   make undeploy
   ```
   *Removes the operator and its associated resources from the cluster.*

**You have successfully implemented and deployed your VPC Operator!** This lab demonstrated how to build, deploy, and test a Kubernetes-native operator to manage custom VPC resources in a Kubernetes cluster.