# Creating a VPC Custom Resource with CRDs

## Overview

In this lab, you will define and create a Custom Resource Definition (CRD) for a Virtual Private Cloud (VPC) resource in a Kubernetes cluster. This CRD will act as a custom object type in the Kubernetes API, allowing you to create and manage VPCs just like native Kubernetes resources such as Pods or Services.

### Key Concepts:
- **Custom Resource Definition (CRD)**: Extends the Kubernetes API to include new types of resources.
- **Custom Resource (CR)**: A specific instance of a custom resource defined by a CRD.

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

**Congratulations!** You have successfully set up a Kubernetes Custom Resource (CRD) for a VPC. In the next lab, we will implement the controller logic to handle the reconciliation of VPC resources and deploy the operator to automate VPC management.