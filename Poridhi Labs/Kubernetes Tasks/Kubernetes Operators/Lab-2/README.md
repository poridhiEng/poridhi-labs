# Implementing and Deploying the Controller

## Overview

In this lab, you will implement the controller logic to automate the management of the `Book` custom resources in your Kubernetes cluster. The controller will continuously monitor the `Book` resources and update their status based on the specified fields.

### Install Prerequisites

1. **Go (version 1.16 or later)**: Required to build your custom operator.
   ```bash
   sudo apt-get install golang
   ```
   
2. **Kubebuilder**: A tool that helps scaffold a Kubernetes Operator using controller-runtime libraries.
   ```bash
   curl -L -O https://github.com/kubernetes-sigs/kubebuilder/releases/download/v3.2.0/kubebuilder_linux_amd64.tar.gz
   tar -xzvf kubebuilder_linux_amd64.tar.gz
   sudo mv kubebuilder /usr/local/bin/
   ```

3. **Docker**: Needed to build and push the operator container image.
   ```bash
   sudo apt-get install docker.io
   ```
   
4. **Kubernetes Cluster**: A local cluster (e.g., minikube or kind) or a remote cluster where you have permissions to deploy the operator.

5. **Kubectl**: The command-line tool for interacting with your Kubernetes cluster.
   ```bash
   sudo apt-get install kubectl
   ```

### Create a New Kubebuilder Project

1. **Create a new directory** for your project and navigate into it:
   ```bash
   mkdir book-operator
   cd book-operator
   ```
   *Creates a new directory and navigates into it.*

2. **Initialize the Kubebuilder project**:
   ```bash
   kubebuilder init --domain example.com --repo github.com/fazlulkarim105925/book-operator
   ```
   *Sets up the project structure, initializes Go modules, and creates necessary configurations for your operator.*

3. **Create a new API and Resource for the `Book` custom resource**:
   ```bash
   kubebuilder create api --group library --version v1alpha1 --kind Book
   ```
   *Generates scaffolding for your custom resource (CRD) and controller. Choose `yes` for both creating the resource and the controller.*

### Define the `Book` Custom Resource Schema

1. Open the `api/v1alpha1/book_types.go` file:
   ```bash
   nano api/v1alpha1/book_types.go
   ```
   
2. Define the structure of the `Book` custom resource:

   - Modify the `BookSpec` and `BookStatus` structs to define the properties you want for your `Book` custom resource.

   ```go
   package v1alpha1

   import (
       metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
   )

   // BookSpec defines the desired state of Book
   type BookSpec struct {
       Title           string `json:"title,omitempty"`
       Author          string `json:"author,omitempty"`
       AvailableCopies int    `json:"availableCopies,omitempty"`
   }

   // BookStatus defines the observed state of Book
   type BookStatus struct {
       InStock bool `json:"inStock,omitempty"`
   }

   //+kubebuilder:object:root=true
   //+kubebuilder:subresource:status

   // Book is the Schema for the books API
   type Book struct {
       metav1.TypeMeta   `json:",inline"`
       metav1.ObjectMeta `json:"metadata,omitempty"`

       Spec   BookSpec   `json:"spec,omitempty"`
       Status BookStatus `json:"status,omitempty"`
   }

   //+kubebuilder:object:root=true

   // BookList contains a list of Book
   type BookList struct {
       metav1.TypeMeta `json:",inline"`
       metav1.ListMeta `json:"metadata,omitempty"`
       Items           []Book `json:"items"`
   }

   func init() {
       SchemeBuilder.Register(&Book{}, &BookList{})
   }
   ```
   *Defines the schema for the Book custom resource, including its desired state (`BookSpec`) and observed state (`BookStatus`).*

3. Save the file and regenerate code using:
   ```bash
   make generate
   make manifests
   ```
   *Generates Go code for CRDs, client sets, deep copy functions, and helpers, and creates Kubernetes manifest files for CRDs, RBAC permissions, and controller configurations.*

### Deploy the Custom Resource Definition (CRD)

1. **Build and install the CRD in the cluster**:
   ```bash
   make install
   ```
   *Installs the CRD into the Kubernetes cluster, making the new resource type available.*

2. **Verify that the CRD has been installed**:
   ```bash
   kubectl get crds
   ```
   *Lists all CRDs in the cluster to confirm the Book CRD is installed.*

### Create a Sample Custom Resource

1. **Create a YAML file named `book-sample.yaml`** with the following content:

   ```yaml
   apiVersion: library.example.com/v1alpha1
   kind: Book
   metadata:
     name: introduction-to-algorithms
     namespace: default
   spec:
     title: Introduction to Algorithms
     author: Thomas H. Cormen
     availableCopies: 3
   ```
   *Defines a sample Book resource with specific title, author, and available copies.*

2. **Apply the custom resource** to the cluster:
   ```bash
   kubectl apply -f book-sample.yaml
   ```
   *Creates the Book resource in the cluster based on the YAML definition.*

3. **Check the status of the created `Book` resource**:
   ```bash
   kubectl get book introduction-to-algorithms -o yaml
   ```
   *Displays the details of the created Book resource.*

### Implement the Controller Logic

1. Open the `controllers/book_controller.go` file:
   ```bash
   nano controllers/book_controller.go
   ```
   
2. Replace the content with the following code:

   ```go
   package controller

   import (
       "context"
       "github.com/go-logr/logr"
       libraryv1alpha1 "github.com/fazlulkarim105925/book-operator/api/v1alpha1"
       "k8s.io/apimachinery/pkg/runtime"
       ctrl "sigs.k8s.io/controller-runtime"
       "sigs.k8s.io/controller-runtime/pkg/client"
   )

   // BookReconciler reconciles a Book object
   type BookReconciler struct {
       client.Client
       Log    logr.Logger
       Scheme *runtime.Scheme
   }

   // Reconcile is the core logic of the operator, called whenever a Book resource changes
   func (r *BookReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
       log := r.Log.WithValues("book", req.NamespacedName)

       // Fetch the Book resource
       var book libraryv1alpha1.Book
       if err := r.Get(ctx, req.NamespacedName, &book); err != nil {
           log.Error(err, "unable to fetch Book")
           return ctrl.Result{}, client.IgnoreNotFound(err)
       }

       // Update the Book status based on AvailableCopies
       book.Status.InStock = book.Spec.AvailableCopies > 0

       // Update the status in Kubernetes
       if err := r.Status().Update(ctx, &book); err != nil {
           log.Error(err, "unable to update Book status")
           return ctrl.Result{}, err
       }

       return ctrl.Result{}, nil
   }

   // SetupWithManager sets up the controller with the Manager
   func (r *BookReconciler) SetupWithManager(mgr ctrl.Manager) error {
       return ctrl.NewControllerManagedBy(mgr).
           For(&libraryv1alpha1.Book{}).
           Complete(r)
   }
   ```
   *Implements the reconciliation logic for the Book resource, including fetching the resource, updating its status based on available copies, and ensuring the status is updated in Kubernetes.*

3. Save the file.

### Step 7: Build and Deploy the Operator

1. **Build the Docker image** for your operator:
   ```bash
   make docker-build IMG=fazlulkarim105925/book-operator:latest
   ```
   *Compiles the operator code into a Docker image.*

2. **Push the Docker image** to DockerHub:
   ```bash
   docker push fazlulkarim105925/book-operator:latest
   ```
   *Uploads the Docker image to a container registry.*

3. **Deploy the operator** in your cluster:
   ```bash
   make deploy IMG=fazlulkarim105925/book-operator:latest
   ```
   *Deploys the operator to the Kubernetes cluster.*

4. **Verify the operator deployment**:
   ```bash
   kubectl get pods -n book-operator-system
   ```
   *Checks that the operator pod is running in the cluster.*

### Test the Controller

1. **Update the `availableCopies` field in `book-sample.yaml`** to `0` and reapply:
   ```bash
   kubectl apply -f book-sample.yaml
   ```

2. **Check the status of the `Book` resource**:
   ```bash
   kubectl get book introduction-to-algorithms -o yaml
   ```
   *The `status.inStock` field should be updated to `false`.*

### Clean Up

1. **Delete the Book resource**:
   ```bash
   kubectl delete -f book-sample.yaml
   ```
   *Removes the Book resource from the cluster.*

2. **Uninstall the operator**:
   ```bash
   make undeploy
   ```
   *Removes the operator and its associated resources from the cluster.*

**You have successfully built, deployed, and tested your Kubernetes Operator!** This lab demonstrated how to implement the controller logic and deploy a Kubernetes-native application that automates custom resource management.