# Monitoring AWS EKS Using Prometheus and Grafana

In this lab, you will learn how to set up monitoring for an Amazon EKS (Elastic Kubernetes Service) cluster using Prometheus and Grafana. This process will enable you to track metrics, visualize data, and set up alerts, ensuring optimal performance and health of your Kubernetes clusters on AWS.


## Amazon EKS, Grafana and Prometheus

**Amazon EKS** (Elastic Kubernetes Service) is a managed Kubernetes service that simplifies the process of deploying, managing, and scaling containerized applications using Kubernetes on AWS. It automates the complexity of cluster management, allowing developers to focus on building applications.


**Grafana** is an open-source tool for data visualization, providing configurable dashboards that integrate with various data sources like Prometheus, InfluxDB, and more.

**Prometheus** is an open-source monitoring and alerting toolkit designed for reliability and scalability in dynamic environments. It collects and stores time-series data, which can be visualized using Grafana.

Here's how monitoring AWS EKS works:

![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-23.png?raw=true)

## Task 
In this hands-on lab, we will do the following tasks:
   - Configure the AWS CLI
   - Install and Configure `kubectl`
   - Install and Configure `eksctl`
   - Install and Configure Helm
   - Create an Amazon EKS Cluster
   - Create worker group
   - Add Helm Repositories
   - Install Prometheus using Helm
   - Expose Prometheus and Grafana
   - Access Grafana Dashboard

The step-by-step implementation is given below.

## Step 1: Configure AWS CLI

Run the following command to configure aws cli:
```bash
aws configure
```

![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image.png?raw=true)

Provide your secret key, secret access key, region etc.

## Step 2: Install and Set Up `kubectl` 

`kubectl` is the command-line tool for interacting with Kubernetes clusters. Installing and configuring `kubectl` allows you to manage your EKS cluster from the command line.

1. Download `kubectl`:

    ```bash
    sudo curl --silent --location -o /usr/local/bin/kubectl   https://s3.us-west-2.amazonaws.com/amazon-eks/1.22.6/2022-03-09/bin/linux/amd64/kubectl
    ```

2. Make the binary executable:

    ```bash
    sudo chmod +x /usr/local/bin/kubectl 
    ```

3. Verify the installation:

    ```bash
    kubectl version --short --client
    ```

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-1.png?raw=true)

    This command should display the `kubectl` version, confirming that the installation was successful.

## Step 3: Install and Set Up `eksctl`

`eksctl` is a command-line tool that simplifies the process of creating and managing EKS clusters. It abstracts the complexity of Kubernetes setup, making it easier to deploy clusters on AWS.

1. Download `eksctl`:

    ```bash
    curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
    ```

2. Move the binary to `/usr/local/bin`:

    ```bash
    sudo mv /tmp/eksctl /usr/local/bin
    ```

3. Verify the installation:

    ```bash
    eksctl version
    ```

    This command should display the `eksctl` version, confirming that it’s correctly installed.

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-2.png?raw=true)

## Step 4: Install Helm

Helm is a package manager for Kubernetes that simplifies the deployment of applications by using Helm charts. These charts are collections of YAML templates that describe Kubernetes resources.

1. Download and install Helm:

    ```bash
    curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3

    chmod 700 get_helm.sh
    
    ./get_helm.sh
    DESIRED_VERSION=v3.8.2 bash get_helm.sh
    curl -L https://git.io/get_helm.sh | bash -s -- --version v3.8.2
    ```

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-3.png?raw=true)

2. Verify the installation:

    ```bash
    helm version
    ```

    This command should display the Helm version, ensuring it’s ready for use.

## Step 5: Create an Amazon EKS Cluster Using `eksctl`

Creating an EKS cluster using `eksctl` streamlines the process by automating the setup of control planes and networking.

1. Create the EKS cluster:

    ```bash
    eksctl create cluster \
    --name poridhi-cluster \
    --version 1.30 \
    --region ap-southeast-1 \
    --zones ap-southeast-1a,ap-southeast-1b \
    --without-nodegroup
    ```

    - **`--name`**: Specifies the name of the cluster.
    - **`--region`**: Defines the AWS region.

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-5.png?raw=true)

    **Note:** It may take 15–20 minutes for the cluster to be fully operational. You will see the status of the cluster 'Active' once it is fully operational.

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-8.png?raw=true)

2. Verify the cluster creation in the AWS Console:

    ```bash
    eksctl get cluster --name poridhi-cluster --region ap-southeast-1
    ```

    This command confirms that your EKS cluster is up and running.


This steps automatically creates necessary VPC, Subnet etc. Here's the resource-map of our VPC. You can see this in AWS Console:

![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-7.png?raw=true)



## Step 6: Create NodeGroup Using `eksctl`

After creating the EKS cluster, you can add a node group that will consist of EC2 instances acting as worker nodes. We will follow the following step in our lab.

1. Use the command below to create NodeGroup

    ```bash
    eksctl create nodegroup \
    --cluster=poridhi-cluster \
    --name=poridhi-nodes \
    --region=ap-southeast-1 \
    --node-type=t3.medium \
    --managed \
    --nodes=2 \
    --nodes-min=1 \
    --nodes-max=2
    ```

    This command creates a managed node group named `poridhi-nodes` in the `poridhi-cluster` Amazon EKS cluster, located in the `ap-southeast-1` AWS region. The node group uses `t3.medium` EC2 instances, with a desired number of 2 nodes. The node group will automatically scale between a minimum of 1 node and a maximum of 2 nodes based on demand.

2. Wait for Completion

    It might take a few minutes for the Node Group to be fully created. You can monitor the progress in the EKS Console. The status of the Node Group will be updated to 'active' once it is fully created.

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-9.png?raw=true)

3. Update the kubeconfig file to interact with the EKS cluster:

    ```bash
    aws eks update-kubeconfig --name poridhi-cluster --region ap-southeast-1
    ```

4. Confirm the connection to the EKS cluster:

    ```bash
    kubectl get nodes
    kubectl get ns
    ```

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-4.png?raw=true)


    These commands list the worker nodes and namespaces in the cluster.

This process will add the worker nodes to your EKS cluster, making them ready to run workloads.



## Step 7: Add Helm Stable Charts for Your Local Client

Helm charts provide pre-configured templates for deploying applications in Kubernetes. Adding the Helm stable charts repository allows you to access a wide range of applications.

1. Add the Helm stable repository:

    ```bash
    helm repo add stable https://charts.helm.sh/stable
    ```

    This command adds the stable Helm chart repository to your local Helm installation.

## Step 8: Add Prometheus Helm Repository

The Prometheus Helm repository contains charts for deploying Prometheus and related tools in Kubernetes.

1. Add the Prometheus Helm repository:

    ```bash
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    ```

    This command adds the Prometheus community Helm repository to your local Helm setup.

## Step 9: Create a Namespace for Prometheus

Namespaces in Kubernetes provide a way to organize and manage resources within a cluster.

1. Create the Prometheus namespace:

    ```bash
    kubectl create namespace prometheus
    ```

2. Verify the namespace creation:

    ```bash
    kubectl get ns
    ```

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-12.png?raw=true)

    This command lists all namespaces, including the newly created Prometheus namespace.

## Step 8: Install Prometheus Using Helm

Helm simplifies the deployment of Prometheus by using pre-configured charts that package all necessary components.

1. Install Prometheus using Helm:

    ```bash
    helm install stable prometheus-community/kube-prometheus-stack -n prometheus
    ```

    - **`prometheus`**: Name of the Helm release.
    - **`prometheus-community/kube-prometheus-stack`**: Specifies the chart to be used.
    - **`-n prometheus`**: Specifies the namespace.

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-13.png?raw=true)

2. Verify the installation:

    ```bash
    kubectl get pods -n prometheus
    ```

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-14.png?raw=true)

    This command lists all the pods in the Prometheus namespace, confirming that Prometheus is running.

3. Check the Prometheus services:

    ```bash
    kubectl get svc -n prometheus
    ```

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-15.png?raw=true)

    This command lists all the services in the Prometheus namespace, confirming that

 Prometheus services are running.

## Step 10: Expose Prometheus and Grafana to the External World

By exposing Prometheus and Grafana, you can access them externally for monitoring and visualization purposes.

1. Edit the service to use a LoadBalancer for external access:

    ```bash
    kubectl edit svc stable-kube-prometheus-sta-prometheus -n prometheus
    ```

    Change the type to `LoadBalancer`:

    ```yaml
    spec:
      type: LoadBalancer
    ```

    Save and exit the vim.


2. Retrieve the external IP address assigned to Prometheus:

    ```bash
    kubectl get svc -n prometheus
    ```

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-10.png?raw=true)

    The `EXTERNAL-IP` will be assigned, which you can use to access Prometheus in a browser.

    Open `<EXTERNAL-IP>:9090` for prometheus:

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-17.png?raw=true)



3. Expose Grafana similarly:

    ```bash
    kubectl edit svc stable-grafana -n prometheus
    ```

    Again, change the type to `LoadBalancer`:

    ```yaml
    spec:
      type: LoadBalancer
    ```

    Save and exit the vim.

4. Access Grafana via the external IP address obtained:

    ```bash
    kubectl get svc -n prometheus
    ```

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-11.png?raw=true)

    The `EXTERNAL-IP` will be listed for Grafana, which you can use to access Grafana in a browser.

    ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-16.png?raw=true)





## Step 11: Retrieve Grafana Admin Password and Open dashboard 

After deploying Grafana to your EKS cluster, you will need the admin password to access the Grafana dashboard. Follow these steps to retrieve the password and access the dashboard:

1. **Retrieve Grafana Admin Password:**
   - Open your terminal and run the following command to get the admin password for Grafana:

     ```bash
     kubectl get secret --namespace prometheus stable-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
     ```

   - This command retrieves the password from the Kubernetes secret where Grafana stores it and decodes it from Base64 format.
   - Log in to Grafana:
        - Use `admin` as the username.
        - Paste the retrieved password into the password field.
        - Click **Login** to access the Grafana dashboard.

4. **Explore the Grafana Dashboard:**
   - Once logged in, you can start exploring the Grafana dashboards. By default, you may see some predefined dashboards for monitoring Kubernetes, which were set up as part of the Prometheus and Grafana installation. You can also create new dashboards tailored to your needs.

   ![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-18.png?raw=true)

This step allows you to securely access and manage your Grafana instance, viewing metrics and data visualizations for your Kubernetes environment. If you click any of the names in the dashboards you will see the detailed information. Below are some examples:

![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-19.png?raw=true)

![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-20.png?raw=true)

![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-21.png?raw=true)

![alt text](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2006/images/image-22.png?raw=true)


## Conclusion

By following this lab, you have successfully set up monitoring for your Amazon EKS cluster using Prometheus and Grafana. You've learned how to install and configure `kubectl`, `eksctl`, and Helm, deploy an EKS cluster, install Prometheus using Helm, and expose it along with Grafana to the external world. Monitoring is crucial for maintaining the health and performance of your applications, and tools like Prometheus and Grafana make it easier to gain insights into your infrastructure.