# Setting up Kubernetes Custom Resources (CRDs)

## Project Overview

The goal of this project is to create a Kubernetes Operator for managing a custom "Book" resource. Operators automate application-specific operations within a Kubernetes cluster by using Custom Resource Definitions (CRDs) to extend the Kubernetes API with custom resources. This allows for the automation of lifecycle management of these resources, making Kubernetes a platform for more than just deploying containerized applications.

### Key Concepts Explained:
1. **Custom Resource Definitions (CRDs)**: CRDs allow you to define new types of objects in Kubernetes. For this project, we will define a `Book` custom resource to manage our book inventory.
   
2. **Kubernetes Controller**: A controller watches the state of the cluster and makes changes to ensure that the actual state matches the desired state. In this case, the controller will update the `Book` status based on its specifications.
   
3. **Reconciliation Loop**: The core mechanism in a Kubernetes controller that continuously monitors the cluster and takes action whenever there is a change in the custom resource. For example, if the number of available copies of a book changes, the reconciliation loop updates the `Book` status.

4. **Operator Pattern**: An operator is a method of packaging, deploying, and managing a Kubernetes application. It enables you to encode domain-specific logic to handle common operations like scaling, backup, and failure recovery. For the `Book` resource, the operator will automate the management of book inventory.

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

### Update the Custom Resource Definition (CRD)

If you need to update the CRD, such as adding new fields or modifying existing ones, follow these steps:

1. **Modify the `Book` custom resource schema** in the `api/v1alpha1/book_types.go` file:
   - Add a new field, such as `Publisher`, to the `BookSpec` struct.

   ```go
   // BookSpec defines the desired state of Book
   type BookSpec struct {
       Title           string `json:"title,omitempty"`
       Author          string `json:"author,omitempty"`
       AvailableCopies int    `json:"availableCopies,omitempty"`
       Publisher       string `json:"publisher,omitempty"` // New field added
   }
   ```

2. **Regenerate the code and manifests**:
   ```bash
   make generate
   make manifests
   ```
   *Updates the generated code and manifests to reflect changes in the resource schema.*

3. **Apply the updated CRD to the cluster**:
   ```bash
   make install
   ```
   *Reinstalls the updated CRD into the Kubernetes cluster.*

4. **Verify the updated CRD**:
   ```bash
   kubectl get crds
   ```
   *Ensures the updated CRD is correctly installed in the cluster.*

5. **Update the sample custom resource** to include the new field:
   - Modify `book-sample.yaml` to include the `publisher` field.

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
     publisher: MIT Press  # New field added
   ```

6. **Reapply the updated custom resource**:
   ```bash
   kubectl apply -f book-sample.yaml
   ```
   *Updates the Book resource in the cluster with the new field.*

**Congratulations!** You have successfully set up and updated a Kubernetes Custom Resource (CRD) for managing book inventory. In the next lab, we will implement the controller logic to handle the reconciliation of the `Book` resources and deploy the operator to automate book management.