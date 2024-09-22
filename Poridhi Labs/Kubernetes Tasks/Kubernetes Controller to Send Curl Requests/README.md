# Creating a Controller to Send Curl Requests to an API with Kubebuilder

This tutorial will guide you through creating a custom Kubernetes controller using **Kubebuilder**. The goal is to build a controller that periodically sends HTTP `curl` requests to a specified API endpoint. The controller will then log the response status and body, and schedule the next request based on a defined interval. This tutorial is a step-by-step guide, covering project setup, API creation, controller implementation, and deployment.

![](./images//controller.svg)

### Prerequisites

To follow along with this tutorial, you should have the following tools installed:
- **Go 1.16+**
- **Kubebuilder 3.0+**
- **Docker**
- **kubectl**
- **A Kubernetes cluster** (This can be local, such as Minikube, Kind, or K3s)


### Install Go

```bash
# 1. Download Go and extract it in one step
wget -qO- https://dl.google.com/go/go1.23.1.linux-amd64.tar.gz | sudo tar -C /usr/local -xzf -
```
```bash
# 2. Add Go to PATH
echo 'export PATH=$PATH:/usr/local/go/bin' >> $HOME/.profile
```
```bash
# 3. Apply changes
source $HOME/.profile
```
```bash
# 4. Verify Go installation
go version
```

### Install Kubebuilder
```bash
# install kubebuilder binaries
curl -L -o kubebuilder https://go.kubebuilder.io/dl/latest/$(go env GOOS)/$(go env GOARCH)
```
```bash
chmod +x kubebuilder && mv kubebuilder /usr/local/bin/
```
```bash
kubebuilder version
```

### Verify Docker installation

```bash
docker version
```

### Verify Kubernetes Cluster

```bash
kubectl get nodes -o wide
```

## Task Description

![](./images//Controller%20Workflow%20Diagram.svg)

The main task is to build a Kubernetes controller that manages a custom resource called `CurlJob`. This controller will:
1. **Send HTTP GET requests** to a target URL (API).
2. **Log the response** status and body from the URL.
3. **Repeat the process** at regular intervals, based on the configuration provided in the custom resource.

The end result will be a Kubernetes-native way of sending periodic requests to an API and logging the responses, with the controller automatically managing the lifecycle of these operations.



## Step 1: Set Up the Project

### 1.1 Create a New Project Directory

Start by creating a new directory for the project where all the necessary files will reside. Then, change into this directory:

```bash
mkdir curl-api-controller
cd curl-api-controller
```

### 1.2 Initialize the Project with Kubebuilder

Use the Kubebuilder tool to initialize a new project. This will set up the basic structure required for a Kubernetes controller, including the necessary scaffolding for APIs and controllers.

```bash
kubebuilder init --domain example.com --repo github.com/example/curl-api-controller
```

The `--domain` and `--repo` flags define the base domain for the Custom Resource Definition (CRD) and the repository name, respectively.



## Step 2: Create an API and Controller

### 2.1 Generate a New API and Controller

Now, we will create the API and controller for the custom resource `CurlJob`. This step will prompt you to create both the resource (CRD) and the controller. Be sure to choose `y` (yes) for both when prompted.

```bash
kubebuilder create api --group batch --version v1 --kind CurlJob
```

![alt text](image.png)

The command above will:
- Create a new **Custom Resource Definition** (CRD) called `CurlJob` in the `batch.example.com` API group.
- Set up the **controller** that will manage the behavior of this resource.

### 2.2 Modify the `CurlJobSpec`

The next step is to define what the `CurlJob` custom resource should look like. In this case, the resource needs two key fields:
1. **URL**: The endpoint where the HTTP requests will be sent.
2. **Interval**: The time (in seconds) between each request.

Modify the `CurlJobSpec` struct inside the `api/v1/curljob_types.go` file:

```go
type CurlJobSpec struct {
    // URL is the target API endpoint
    URL string `json:"url"`

    // Interval is the time between curl requests in seconds
    Interval int32 `json:"interval"`
}
```

This defines the structure of the `CurlJob` resource, specifying that each job will include a URL to target and an interval for how often to send the requests.

### 2.3 Update the CRD Manifests

After defining the `CurlJob` custom resource, run the following command to update the CRD manifests:

```bash
make manifests
```

![alt text](image-1.png)

This will generate the necessary Kubernetes YAML files to register the `CurlJob` CRD within the cluster.



## Step 3: Implement the Controller

Now that we have defined the API, we can implement the actual behavior of the controller. The controller will handle sending the HTTP requests and scheduling them based on the interval.

### 3.1 Implement the `Reconcile` Method

The controller's core logic is implemented in the `Reconcile` method. This method is triggered by Kubernetes whenever a `CurlJob` resource is created or updated.

Replace the contents of `internal/controller/curljob_controller.go` with the following:

```go
package controller

import (
    "context"
    "fmt"
    "io/ioutil"
    "net/http"
    "time"

    "k8s.io/apimachinery/pkg/runtime"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/log"

    batchv1 "github.com/example/curl-api-controller/api/v1"
)

type CurlJobReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

func (r *CurlJobReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    logger := log.FromContext(ctx)

    var curlJob batchv1.CurlJob
    if err := r.Get(ctx, req.NamespacedName, &curlJob); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Send the curl request
    resp, err := http.Get(curlJob.Spec.URL)
    if err != nil {
        logger.Error(err, "Failed to send curl request")
        return ctrl.Result{}, err
    }
    defer resp.Body.Close()

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        logger.Error(err, "Failed to read response body")
        return ctrl.Result{}, err
    }

    logger.Info(fmt.Sprintf("Curl request successful. Status: %s, Body: %s", resp.Status, string(body)))

    // Schedule the next request after the specified interval
    return ctrl.Result{RequeueAfter: time.Duration(curlJob.Spec.Interval) * time.Second}, nil
}

func (r *CurlJobReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&batchv1.CurlJob{}).
        Complete(r)
}
```

### Explanation:

- The `Reconcile` method:
  - Retrieves the `CurlJob` resource.
  - Sends an HTTP GET request to the specified URL.
  - Logs the response status and body.
  - Schedules the next request using the `Interval` specified in the custom resource.
  


## Step 4: Update RBAC Permissions

The controller requires the appropriate permissions to manage `CurlJob` resources within the cluster. To provide these permissions, update the **RBAC** configuration in the `config/rbac/role.yaml` file:

```yaml
- apiGroups:
  - batch.example.com
  resources:
  - curljobs
  verbs:
  - create
  - delete
  - get
  - list
  - patch
  - update
  - watch
- apiGroups:
  - batch.example.com
  resources:
  - curljobs/status
  verbs:
  - get
  - patch
  - update
```

This ensures the controller has the necessary permissions to manage and update the status of `CurlJob` resources.



## Step 5: Build and Deploy the Controller

Now that the controller is implemented, we need to build and deploy it to the Kubernetes cluster. At first, login to your docker account using the following command:
```bash
docker login
```

Give your credentials to login. 

![alt text](image-2.png)

Modify your `install` command in the Makefile to include the `--validate=false` flag:

```makefile
$(KUSTOMIZE) build config/crd | $(KUBECTL) apply --validate=false -f -
```

![alt text](image-3.png)

Modify your `deploy` command in the Makefile to include the `--validate=false` flag:

```makefile
$(KUSTOMIZE) build config/default | $(KUBECTL) apply --validate=false -f -
```

![alt text](image-4.png)

### 5.1 Build and Push the Docker Image

First, build the Docker image for the controller and push it to a container registry:

```bash
make docker-build docker-push IMG=<your-registry>/curl-api-controller:v1
```

Replace `<your-registry>` with your actual Docker registry (e.g., Docker Hub or a private registry).

### 5.2 Deploy the Controller

Once the image is built and pushed, deploy the controller to your Kubernetes cluster:

```bash
make deploy IMG=<your-registry>/curl-api-controller:v1
```

This command will apply the necessary Kubernetes manifests to deploy the controller, including the CRDs and other required components.



## Step 6: Create a CurlJob Custom Resource

Now that the controller is running in the cluster, we can create an instance of the `CurlJob` custom resource. This will instruct the controller to start sending curl requests to a specific API.

Create a file named `config/samples/batch_v1_curljob.yaml` with the following content:

```yaml
apiVersion: batch.example.com/v1
kind: CurlJob
metadata:
  name: curljob-sample
spec:
  url: "http://poridhi.io"
  interval: 60
```

This YAML file defines a `CurlJob` that will send a curl request to `https://api.example.com` every 60 seconds.

### Apply the Custom Resource:

```bash
kubectl apply -f config/samples/batch_v1_curljob.yaml
```



## Conclusion

You have now successfully created a Kubernetes controller that periodically sends HTTP requests to a specified API endpoint. The controller reads the response, logs it, and continues sending requests at regular intervals based on the configuration provided by the custom resource. You can monitor the logs to see the controller's actions in real-time:

```bash
kubectl logs -n curl-api-controller-system deployment/curl-api-controller-controller-manager -c manager
```

Or save it in a separate file:
```bash
```bash
kubectl logs -n curl-api-controller-system deployment/curl-api-controller-controller-manager -c manager > output_logs.txt
```

This setup can be extended to perform more complex tasks, such as integrating with external services or automating other workflows in Kubernetes.