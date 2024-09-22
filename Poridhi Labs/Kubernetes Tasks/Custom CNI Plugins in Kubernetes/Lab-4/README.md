# **Dynamic IP Assignment for Kubernetes Pods with Bash CNI**

In Kubernetes, each pod must be assigned a unique IP address to communicate with other pods, the host system, and external networks. In this lab, we will implement dynamic IP assignment for Kubernetes pods using a custom **Bash CNI** plugin. By assigning IP addresses dynamically, we ensure efficient pod-to-pod and pod-to-host communication within the Kubernetes cluster.

![](./images/41.svg)

## **Objectives**

By the end of this lab, you will:

- Provision the necessary infrastructure for a Kubernetes cluster on AWS using Terraform.
- Modify the custom Bash CNI plugin to dynamically assign IP addresses to Kubernetes pods.
- Verify that pods can communicate with the host, other pods, and external resources.

## **Prerequisites**

Before starting this lab, ensure you have:

- An AWS account with programmatic access enabled.
- AWS CLI installed and configured.
- Terraform installed on your local machine.

## **Provision Infrastructure for Kubernetes Cluster**

We will use **Terraform** to automate the creation of AWS resources for our Kubernetes cluster. This includes setting up EC2 instances for the master and worker nodes, with the necessary tools for Kubernetes installed via user data scripts.

![](./images/21.svg)

### **AWS CLI Configuration**

To configure AWS CLI, use the following command:

```bash
aws configure
```

This will prompt you to enter:

- **AWS Access Key ID**
- **AWS Secret Access Key**
- **Default region** (e.g., `ap-southeast-1`)
- **Output format** (e.g., `json`)

  ![](./images/1.png)

### **Terraform Configuration (main.tf)**

Create a `main.tf` file with the following configuration to set up your Kubernetes cluster infrastructure.

```hcl
# Provider configuration
provider "aws" {
  region = "ap-southeast-1" # Replace with your desired region
}

# Create a key pair and store it locally
resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "my_key_pair" {
  key_name   = "cni"
  public_key = tls_private_key.example.public_key_openssh
}

resource "local_file" "private_key" {
  filename        = "${path.module}/cni.pem"
  content         = tls_private_key.example.private_key_pem
  file_permission = "0400"
}

# Create a VPC
resource "aws_vpc" "my_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "my-vpc"
  }
}

# Create an Internet Gateway
resource "aws_internet_gateway" "my_igw" {
  vpc_id = aws_vpc.my_vpc.id
  tags = {
    Name = "my-igw"
  }
}

# Create a public subnet
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "ap-southeast-1a"
  tags = {
    Name = "public-subnet"
  }
}

# Create a route table
resource "aws_route_table" "my_rt" {
  vpc_id = aws_vpc.my_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.my_igw.id
  }
  tags = {
    Name = "my-rt"
  }
}

# Associate the route table with the public subnet
resource "aws_route_table_association" "my_rt_association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.my_rt.id
}

# Create a security group allowing all traffic
resource "aws_security_group" "allow_all_traffic" {
  vpc_id = aws_vpc.my_vpc.id
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "allow-all-traffic"
  }
}

# Hostname and Kubernetes setup for each node
variable "user_data_master" {
  default = <<EOF
#!/bin/bash
sudo hostnamectl set-hostname master

# Install Docker
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo apt-get install -y docker.io

# Install Kubernetes components
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl

# Enable IP forwarding
sudo sysctl net.ipv4.ip_forward=1
EOF
}

variable "user_data_worker_1" {
  default = <<EOF
#!/bin/bash
sudo hostnamectl set-hostname worker-1

# Install Docker
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo apt-get install -y docker.io

# Install Kubernetes components
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl

# Enable IP forwarding
sudo sysctl net.ipv4.ip_forward=1
EOF
}

variable "user_data_worker_2" {
  default = <<EOF
#!/bin/bash
sudo hostnamectl set-hostname worker-2

# Install Docker
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo apt-get install -y docker.io

# Install Kubernetes components
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl

# Enable IP forwarding
sudo sysctl net.ipv4.ip_forward=1
EOF
}

# Create EC2 instances for master and workers
resource "aws_instance" "ec2_instances" {
  count                       = 3
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public_subnet.id
  vpc_security_group_ids      = [aws_security_group.allow_all_traffic.id]
  associate_public_ip_address = true
  key_name                    = aws_key_pair.my_key_pair.key_name

  # Assign different user_data to set the hostname and install components for each instance
  user_data = lookup({
    0 = var.user_data_master
    1 = var.user_data_worker_1
    2 = var.user_data_worker_2
  }, count.index)

  tags = {
    Name = "ec2-instance-${count.index + 1}"
  }
}

# Output for private key and public IPs of instances
output "private_key_path" {
  value = local_file.private_key.filename
}

output "ec2_public_ips" {
  value = [for instance in aws_instance.ec2_instances : instance.public_ip]
}

# Variables for AMI and instance type
variable "ami_id" {
  default = "ami-0e86e20dae9224db8"  # Replace with your desired AMI
}

variable "instance_type" {
  default = "t3.small"
}
```

### **Applying the Terraform Configuration**

Once the `main.tf` file is created, follow these steps to apply the configuration and create the infrastructure:

1. **Initialize Terraform**:

   ```bash
   terraform init
   ```

2. **Apply the Terraform configuration**:

   ```bash
   terraform apply
   ```

   ![](./images/2.png)

Terraform will create the necessary infrastructure, and it will output the public IPs of the EC2 instances and the path to the private key (`cni.pem`). You can use this information to SSH into the instances.

## **SSH into EC2 Instances and Set Up the Cluster**

Once the instances are provisioned, SSH into the **master** and **worker** nodes to complete the Kubernetes setup:

1. SSH into the **master node** using the private key:

   ```bash
   ssh -i cni.pem ubuntu@<master-public-ip>
   ```

2. Initialize the Kubernetes cluster on the master node:

   ```bash
   sudo kubeadm init --pod-network-cidr=10.244.0.0/16
   ```

   *After running this command, Kubernetes will provide a `join command` that is needed to connect the worker nodes to the cluster. `Note down this join command` as you will use it later to join the worker nodes.*

3. Set up `kubectl` for the master node:

   ```bash
   mkdir -p $HOME/.kube
   sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
   sudo chown $(id -u):$(id -g) $HOME/.kube/config
   ```

4. SSH into each worker node (`worker-1` & `worker-2`) and run the **join command**:

   ```bash
   ssh -i cni.pem ubuntu@<worker-1-public-ip>
   ```

   ```bash
   sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
   ```
   ![](./images/4.png)

5. **Verify the Cluster Setup**:

   Run the following command to check the status of the nodes:

   ```bash
   kubectl get nodes
   ```

   ![](./images/5.png)

   Both master and worker nodes will show as **NotReady** until the CNI plugin is configured.

## **Setting Up Network Interfaces**

To enable communication between pods, we need to set up network bridges (`cni0`) and virtual Ethernet (veth) pairs that connect containers to the host’s network.

### **Create the `cni0` Bridge and Virtual Interfaces**

1. **Create the network bridge (`cni0`) on each node**:

   ```bash
   sudo brctl addbr cni0
   sudo ip link set cni0 up
   sudo ip addr add <bridge-ip>/24 dev cni0
   ```

   Replace `<bridge-ip>` with:

   - `10.244.0.1` for the **master** node.
   - `10.244.1.1` for **worker-1**.
   - `10.244.2.1` for **worker-2**.

This creates the necessary bridge to allow communication between containers within the same node.

## Modify the Bash CNI Plugin for IP Assignment**

Now we will modify the Bash CNI script to dynamically assign IP addresses to Kubernetes pods.

### **Add IP Assignment to the Bash CNI Script**

1. **Open the Bash CNI script on each node**:

   ```bash
   sudo nano /opt/cni/bin/bash-cni
   ```

2. **Insert the following IP assignment logic** into the script:

   ```bash
   #!/bin/bash -e
   
   # Redirect output to a log file
   exec 3>&1
   exec &>> /var/log/bash-cni-plugin.log
   
   # Define the location to store reserved IPs
   IP_STORE=/tmp/reserved_ips
   
   # Log the CNI command and input
   echo "CNI command: $CNI_COMMAND"
   stdin=$(cat /dev/stdin)
   echo "stdin: $stdin"
   
   # Function to allocate an available IP address
   allocate_ip(){
       for ip in "${all_ips[@]}"
       do
           reserved=false
           for reserved_ip in "${reserved_ips[@]}"
           do
               if [ "$ip" = "$reserved_ip" ]; then
                   reserved=true
                   break
               fi
           done
           if [ "$reserved" = false ] ; then
               echo "$ip" >> $IP_STORE
               echo "$ip"
               return
           fi
       done
   }
   
   case $CNI_COMMAND in
   ADD)
       mkdir -p /var/run/netns/
       ln -sfT $CNI_NETNS /var/run/netns/$CNI_CONTAINERID
   
       rand=$(tr -dc 'A-F0-9' < /dev/urandom | head -c4)
       host_if_name="veth$rand"
       ip link add $CNI_IFNAME type veth peer name $host_if_name
   
       ip link set $host_if_name up
       ip link set $host_if_name master cni0
   
       ip link set $CNI_IFNAME netns $CNI_CONTAINERID
       ip netns exec $CNI_CONTAINERID ip link set $CNI_IFNAME up
   
       # IP Assignment Logic
       subnet=$(echo "$stdin" | jq -r ".subnet")
       subnet_mask_size=$(echo $subnet | awk -F  "/" '{print $2}')
       base_ip=$(echo "$subnet" | awk -F '/' '{print $1}' | awk -F '.' '{print $1"."$2"."$3}')
       all_ips=($(seq -f "$base_ip.%g" 2 254))
   
       gw_ip="$base_ip.1"
       reserved_ips=$(cat $IP_STORE 2> /dev/null || printf "$base_ip.0\n$gw_ip\n")
       reserved_ips=(${reserved_ips[@]})
       printf '%s\n' "${reserved_ips[@]}" > $IP_STORE
       container_ip=$(allocate_ip)
   
       ip netns exec $CNI_CONTAINERID ip addr add $container_ip/$subnet_mask_size dev $CNI_IFNAME
       ip netns exec $CNI_CONTAINERID ip route add default via $gw_ip dev $CNI_IFNAME
   
       # Output JSON response
       mac=$(ip netns exec $CNI_CONTAINERID ip link show $CNI_IFNAME | awk '/ether/ {print $2}')
       echo "{
         \"cniVersion\": \"0.3.1\",
         \"interfaces\": [                                            
             {
                 \"name\": \"$CNI_IFNAME\",
                 \"mac\": \"$mac\",                            
                 \"sandbox\": \"$CNI_NETNS\" 
             }
         ],
         \"ips\": [
             {
                 \"version\": \"4\",
                 \"address\": \"$container_ip/$subnet_mask_size\",
                 \"gateway\": \"$gw_ip\",          
                 \"interface\": 0 
             }
         ]
       }" >&3
   
   ;;
   DEL)
       ip=$(ip netns exec $CNI_CONTAINERID ip addr show $CNI_IFNAME | awk '/inet / {print $2}' | sed s%/.*%% || echo "")
       if [ ! -z "$ip" ]
       then
           sed -i "/$ip/d" $IP_STORE
       fi
   ;;
   VERSION)
       echo '{
         "cniVersion": "0.3.1", 
         "supportedVersions": [ "0.3.0", "0.3.1", "0.4.0" ] 
       }' >&3
   ;;
   *)
     echo "Unknown CNI command: $CNI_COMMAND"
     exit 1
   ;;
   esac
   ```

3. **Make the script executable**:

   ```bash
   sudo chmod +x /opt/cni/bin/bash-cni
   ```

### **Explanation of Script**

1. **IP Assignment Logic**:
   - The script now dynamically assigns IP addresses to containers. It calculates a subnet from the provided input (`stdin`), reserves necessary IP addresses (such as gateway), and assigns available IPs to new containers.

2. **JSON Response**:
   - After assigning an IP, the script outputs the network configuration in JSON format, compatible with the CNI specification. This response includes the container’s interface, MAC address, IP, and gateway.

3. **VERSION Command**:
   - The script now handles the `VERSION` command, which returns the supported CNI version and specifications (`0.3.1` in this case).

4. **IP Deallocation**:
   - When a container is deleted (`DEL` command), the script removes the assigned IP from the IP store, making it available for future containers.

## **Test IP Assignment and Pod Communication**

Now that we have implemented dynamic IP assignment, we will verify that pods are assigned IPs and can communicate with the host, other pods, and external resources.

### **Deploy Pods for Testing**

1. **Deploy the following YAML configuration file** (`deploy.yaml`):

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

2. **Deploy the YAML file**:

   ```bash
   kubectl apply -f deploy.yaml
   ```

3. **Verify IP assignment for each pod**:

   ```bash
   kubectl get pods -o wide
   ```

   The `nginx` and `bash` containers should now have **dynamically assigned IP addresses** from the `10.244.x.x` subnet, confirming that IP assignment has been successfully implemented.


## **Test Pod Communication**

1. **Ping the host from within a pod**:

   ```bash
   kubectl exec -it bash-worker-1 -- ping 10.244.1.1
   ```

2. **Ping another pod** (on the same node):

   ```bash
   kubectl exec -it bash-worker-1 -- ping 10.244.1.2
   ```

3. **Ping an external resource (Google DNS)**:

   ```bash
   kubectl exec -it bash-worker-1 -- ping 8.8.8.8
   ```

   **Note**: The pod should be able to ping only the host.Although each pods have unique ip address still it can't ping to other pods,and external networks.In our Next Labs we will address this issues.

## **Conclusion**

In this lab, we successfully implemented **dynamic IP assignment** for Kubernetes pods using a custom **Bash CNI** plugin. By configuring the `cni0` bridge and veth pairs, and dynamically assigning IP addresses. This lab is critical for building robust networking setups in Kubernetes environments.In our next we will be address the connection problem betweeen pods.

