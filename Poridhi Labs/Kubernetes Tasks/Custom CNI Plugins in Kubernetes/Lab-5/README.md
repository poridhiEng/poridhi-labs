# **Fixing Pod Connectivity and External Access in Kubernetes**

In this lab, we will address the issues of pod-to-pod communication across nodes and enable external access to the internet for the pods. We will set up routes for pod subnets, adjust iptables rules, and use NAT (Network Address Translation) to allow outgoing traffic from the pods to external networks.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/architecture.svg)

## **Objectives**

By the end of this lab, you will:

- Provision the necessary infrastructure for a Kubernetes cluster on AWS using Terraform.
- Enable pod-to-pod communication across nodes by setting up routes.
- Allow pods to communicate with external networks using NAT.
- Verify the proper setup of pod communication and external access.

## **Prerequisites**

Before starting this lab, ensure you have:

- An AWS account with programmatic access enabled.
- AWS CLI installed and configured.
- Terraform installed on your local machine.

If you don’t have the `AWS CLI` and `Terraform` installed, follow the official documentation to get them set up.We will use `Poridhi's Vscode` where `AWS CLI` and `Terraform` is preinstalled.

## **Provision Infrastructure for Kubernetes Cluster**

We will provision the necessary infrastructure for our Kubernetes cluster using **Terraform**.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/infra.svg)

### **AWS CLI Configuration**

Configure your AWS CLI by running the following command:

```bash
aws configure
```

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/1.png)

This will prompt you to enter:

- **AWS Access Key ID**
- **AWS Secret Access Key**
- **Default region** (e.g., `ap-southeast-1`)
- **Output format** (e.g., `json`)

### **Terraform Configuration (`main.tf`)**

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
  availability_zone       = "ap-southeast-1a" # Change based on your region
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

# Define AMI and instance type
variable "ami_id" {
  default = "ami-01811d4912b4ccb26"  # Replace with your desired AMI
}

variable "instance_type" {
  default = "t3.small"
}

# User data script to set hostname, update and install required packages, and enable IP forwarding
variable "user_data" {
  type = list(string)
  default = [
    <<-EOF
    #!/bin/bash
    # Set hostname to master
    hostnamectl set-hostname master
    
    # Update and install required packages
    sudo apt-get update
    sudo apt-get install -y docker.io apt-transport-https curl jq nmap iproute2
    
    # Add Kubernetes APT repository and install Kubernetes components
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    
    # Enable IP forwarding
    sudo sysctl -w net.ipv4.ip_forward=1
    EOF
    ,
    <<-EOF
    #!/bin/bash
    # Set hostname to worker-1
    hostnamectl set-hostname worker-1
    
    # Update and install required packages
    sudo apt-get update
    sudo apt-get install -y docker.io apt-transport-https curl jq nmap iproute2
    
    # Add Kubernetes APT repository and install Kubernetes components
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    
    # Enable IP forwarding
    sudo sysctl -w net.ipv4.ip_forward=1
    EOF
    ,
    <<-EOF
    #!/bin/bash
    # Set hostname to worker-2
    hostnamectl set-hostname worker-2
    
    # Update and install required packages
    sudo apt-get update
    sudo apt-get install -y docker.io apt-transport-https curl jq nmap iproute2
    
    # Add Kubernetes APT repository and install Kubernetes components
    curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    
    # Enable IP forwarding
    sudo sysctl -w net.ipv4.ip_forward=1
    EOF
  ]
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
  
  # Use the defined user_data list for each instance
  user_data                   = element(var.user_data, count.index)

  tags = {
    Name = "ec2-instance-${count.index + 1}"
    Role = lookup({
      0 = "master"
      1 = "worker-1"
      2 = "worker-2"
    }, count.index)
  }
}

# Output public IPs with roles (master, worker-1, worker-2)
output "ec2_public_ips_with_roles" {
  value = {
    "master"   = aws_instance.ec2_instances[0].public_ip
    "worker-1" = aws_instance.ec2_instances[1].public_ip
    "worker-2" = aws_instance.ec2_instances[2].public_ip
  }
}

# Get the primary network interface IDs of the EC2 instances
data "aws_network_interface" "ec2_enis" {
  count = 3
  filter {
    name   = "attachment.instance-id"
    values = [aws_instance.ec2_instances[count.index].id]
  }
  filter {
    name   = "attachment.device-index"
    values = ["0"]
  }
}

# Add routes for each pod subnet
resource "aws_route" "pod_routes" {
  count                  = 3
  route_table_id         = aws_route_table.my_rt.id
  destination_cidr_block = "10.244.${count.index}.0/24"
  network_interface_id   = data.aws_network_interface.ec2_enis[count.index].id
}

# Output the route table ID and ENI IDs for pod subnet routes
output "route_table_id" {
  value = aws_route_table.my_rt.id
}

output "eni_ids" {
  value = [for eni in data.aws_network_interface.ec2_enis : eni.id]
}
```

### **Apply the Terraform Configuration**

1. **Initialize Terraform**:

   ```bash
   terraform init
   ```

2. **Apply the Terraform Configuration**:

   ```bash
   terraform apply
   ```

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/output.png)

Terraform will create the necessary infrastructure, and it will output the public IPs of the EC2 instances and the path to the private key (`cni.pem`). You can use this information to SSH into the instances.


## **Setting Up Kubernetes Cluster**

### **SSH into EC2 Instances**

Once the instances are provisioned, SSH into the **master** and **worker** nodes to complete the Kubernetes setup:

1. **SSH into the Master Node**:

   ```bash
   ssh -i cni.pem ubuntu@<master-public-ip>
   ```
   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/m.png)

2. **Initialize the Kubernetes Cluster on the Master Node**:

   ```bash
   sudo kubeadm init --pod-network-cidr=10.244.0.0/16
   ```

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/10.png)

   Kubernetes will provide a `join command` after initialization. Note this down to connect the worker nodes to the cluster.

3. **Set Up `kubectl` for the Master Node**:

   ```bash
   mkdir -p $HOME/.kube
   sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
   sudo chown $(id -u):$(id -g) $HOME/.kube/config
   ```

4. **Join Worker Nodes to the Cluster**:

   SSH into each worker node and run the `join command` from step 2 to connect the worker nodes to the Kubernetes cluster:

   For **worker-1**:

   ```bash
   ssh -i cni.pem ubuntu@<worker-1-public-ip>
   ```
   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/w-1.png)
  
   ```bash
   sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
   ```

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/11.png)

   For **worker-2**:

   ```bash
   ssh -i cni.pem ubuntu@<worker-2-public-ip>
   ```

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/w-2.png)

   ```bash
   sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
   ```

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/12.png)

5. **Verify Cluster Status**:

   On the master node, run:

   ```bash
   kubectl get nodes
   ```

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/13.png)

## **Setting Up Network Interfaces**

### **Create the Custom CNI Plug-in Configuration**

To implement networking for Kubernetes pods, we will create a custom CNI configuration.

1. **Create the CNI Configuration on Each Node (`master`, `worker-1`, `worker-2`)**:

   ```bash
   sudo nano /etc/cni/net.d/10-bash-cni-plugin.conf
   ```

2. **Add the Following Content**:

   ```json
   {
       "cniVersion": "0.3.1",
       "name": "mynet",
       "type": "bash-cni",
       "network": "10.244.0.0/16",
       "subnet": "<node-cidr-range>"
   }
   ```

   Replace `<node-cidr-range>` with:

   - `10.244.0.0/24` for the **master** node.
   - `10.244.1.0/24` for **worker-1**.
   - `10.244.2.0/24` for **worker-2**.

### **Create the `cni0` Bridge and Assign IP Addresses**

1. **Create the Network Bridge (`cni0`) on Each Node (`master`,`worker-1` &`worker-2`)**:

   ```bash
   sudo brctl addbr cni0
   sudo ip link set cni0 up
   sudo ip addr add <bridge-ip>/24 dev cni0
   ```

   Replace `<bridge-ip>` with:
   - `10.244.0.1` for **master**.
   - `10.244.1.1` for **worker-1**.
   - `10.244.2.1` for **worker-2**.

### **Verify the Network Configuration**

After setting up the `cni0` bridge and CIDR blocks, verify the successful creation of these interfaces:

1. **Check the Status of the Network Bridge on Each Node**:

   ```bash
   sudo brctl show cni0
   ```

2. **Verify IP Assignments for Each Bridge Interface**:

   ```bash
   ip addr show cni0
   ```

The output should show the respective IP addresses (`10.244.0.1`,`10.244.1.1`, `10.244.2.1`) assigned to the `cni0` bridge on each node.

### **Check Node Status**

Run the following command to check if the nodes are in a **Ready** state:

```bash
kubectl get nodes
```
![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/17.png)

## **Implementing the Bash CNI Plugin for IP Assignment**

We will now create the Bash CNI plugin script to dynamically assign IP addresses to Kubernetes pods.

### **Create the CNI Plugin Directory and Script on Each Node**:

   ```bash
   sudo nano /opt/cni/bin/bash-cni
   ```

### **Insert the Following Script**:

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

**Make the Script Executable**:

   ```bash
   sudo chmod +x /opt/cni/bin/bash-cni
   ```

## **Deploy Pods and Verify Communication**

### **Deploy Test Pods**

1. **Create the Pod Deployment Configuration (`deploy.yaml`)**:

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

2. **Deploy the Pods**:

   ```bash
   kubectl apply -f deploy.yaml
   ```

3. **Verify Pod IP Assignments**:

   ```bash
   kubectl get pods -o wide
   ```

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/18.png)

   The pods should now have dynamically assigned IP addresses from the `10.244.x.x` subnet, confirming the successful implementation of IP assignment.

### **Test Pod Communication**

1. **Exec into `bash-worker-1` Pod**:

   ```bash
   kubectl exec -it bash-worker-1 -- /bin/bash
   ```

2. **Ping the Host from Within the Pod**:

   ```bash
   ping  10.244.1.1 -c 2
   ```

   This confirms that the pod can communicate with the host.

3. **Ping Another Pod on the Same Node**:

   ```bash
   ping  10.244.1.2 -c 2
   ```

   You might notice that the ping is unsuccessful. This is because inter-pod communication is not fully configured yet.

4. **Ping a Pod on a Different Node**:

   ```bash
   ping  10.244.2.3 -c 2
   ```

   This ping will also fail for the same reason.

5. **Ping an External Resource (Google DNS)**:

   ```bash
   ping  8.8.8.8 -c 2
   ```

   The ping will likely fail because we haven't set up NAT or proper routing to external networks.

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/ping.png)

**Note**: At this stage, the pods can only communicate with the host (the `cni0` bridge) because the necessary routing and forwarding rules are not in place. We will address these issues in the next labs.

## **Fixing Pod-to-Pod Communication within the Same Host**

In Kubernetes, you might expect pod-to-pod communication on the same host to work without any issues, even before configuring cross-host or external access. However, an inspection of the iptables **FORWARD** chain reveals the root cause of this issue.

When traffic is forwarded between pods, the Linux kernel applies the **FORWARD** chain of iptables, even if the traffic does not cross the bridge. Here's a snapshot of the iptables **FORWARD** chain:

```bash
sudo iptables -S FORWARD
```

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/40.png)

This chain handles all packets that need to be forwarded, such as traffic between network namespaces (as with pods). The key issue here is that the default **FORWARD** chain policy is set to `DROP` by Docker for security reasons. As a result, any traffic between pods on the same host is dropped by default unless specific rules are in place to allow it.

### Why Host Communication Works
Traffic from a pod to the host works because iptables uses the **INPUT** chain, not the **FORWARD** chain, when the destination is local to the host.

### Fixing the Pod-to-Pod Communication Issue
To allow traffic between pods on the same host, we need to add specific **FORWARD** rules that permit communication within the pod CIDR range. Run the following commands on each nodes (`master`,`worker-1` & `worker-2`) to resolve this issue:

```bash
sudo iptables -t filter -A FORWARD -s 10.244.0.0/16 -j ACCEPT
sudo iptables -t filter -A FORWARD -d 10.244.0.0/16 -j ACCEPT
```

These rules will enable forwarding of traffic within the pod CIDR range, fixing the pod-to-pod communication problem on the same host.

### To test the connection ping `nginx-worker-1` from `bash-worker-1`

```bash
kubectl exec -it bash-worker-1 -- /bin/bash
```
Then ping the `nginx-worker-1` with its IP
```bash
ping  10.244.1.2 -c 2
```
![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/41.png)

## **Fixing External Access Using NAT**

Pods in Kubernetes are located in a private subnet (e.g., `10.244.0.0/24`). When a pod tries to send network packets to the Internet, those packets will have a source IP from this private subnet. Since the private subnet is not routable on the public Internet, the packets will be dropped by routers. Even if the packet reaches its destination, the response cannot be routed back to the private pod IP (`10.244.0.x`), leading to communication failure.

To resolve this, we can set up **Network Address Translation (NAT)** on the host VM. NAT replaces the source IP address of outgoing packets with the public IP address of the host VM. The original pod IP is stored, and when the response packet comes back, the original pod IP is restored, allowing the packet to be forwarded correctly to the pod.

### Setting Up NAT
NAT can be set up easily using iptables with the **MASQUERADE** target. The following commands should be run on the respective nodes:

**On Worker Nodes**:

   For **master**:
   ```bash
   sudo iptables -t nat -A POSTROUTING -s 10.244.0.0/24 ! -o cni0 -j MASQUERADE
   ```
   
   For **worker-1**:

   ```bash
   sudo iptables -t nat -A POSTROUTING -s 10.244.1.0/24 ! -o cni0 -j MASQUERADE
   ```

   For **worker-2**:

   ```bash
   sudo iptables -t nat -A POSTROUTING -s 10.244.2.0/24 ! -o cni0 -j MASQUERADE
   ```

### Explanation:
- **MASQUERADE**: This iptables target is used to perform source NAT (SNAT) when the external IP of the outgoing interface is not known at the time of writing the rule.
- **Conditions**:
  - Only packets with a source IP in the pod subnet (`10.244.x.0/24`) are affected.
  - The rule excludes traffic destined for the `cni0` bridge (`! -o cni0`), which handles internal pod traffic.

Once NAT is configured, the pods will be able to access external networks, such as the Internet, and other VMs within the cluster.

### **Test External Access**

After configuring NAT, test external access by pinging Google DNS:

```bash
kubectl exec -it bash-worker-1 -- /bin/bash
```
Then ping google dns `8.8.8.8`

```bash
ping  8.8.8.8 -c 2
```

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/42.png)

The ping should now be successful, confirming that the pods can access external networks.

## **Setting Up Routing for Inter-Node Pod Communication**

To enable pod-to-pod communication across different worker nodes in the Kubernetes cluster, you need to configure routes for each worker node’s pod CIDR block. This will allow traffic between pods residing on different nodes to traverse the network properly. The process involves adding routes for each node's pod CIDR block and associating them with the network interfaces of the respective  nodes.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/architecture.svg)

In our terraform `main.tf` we already included that part

```hcl
# Get the primary network interface IDs of the EC2 instances
data "aws_network_interface" "ec2_enis" {
  count = 3
  filter {
    name   = "attachment.instance-id"
    values = [aws_instance.ec2_instances[count.index].id]
  }
  filter {
    name   = "attachment.device-index"
    values = ["0"]
  }
}

# Add routes for each pod subnet
resource "aws_route" "pod_routes" {
  count                  = 3
  route_table_id         = aws_route_table.my_rt.id
  destination_cidr_block = "10.244.${count.index}.0/24"
  network_interface_id   = data.aws_network_interface.ec2_enis[count.index].id
}
```

### What We Done Here

1. **Data Source for ENIs**:
   We first fetch the **Elastic Network Interfaces (ENIs)** associated with the EC2 instances using `data "aws_network_interface"`. Each node's ENI is crucial for routing traffic to the correct pod subnet.

2. **Defining Routes**:
   The `aws_route` resource creates a route for each **Pod CIDR block** (`10.244.0.0/24`, `10.244.1.0/24`, etc.), pointing to the appropriate network interface. The destination CIDR block corresponds to the pod network on each node.

3. **Automation via Terraform**:
   Using Terraform’s count functionality, we automate the creation of routes for multiple nodes. Each node's Pod CIDR block is routed through its ENI, ensuring smooth pod-to-pod communication.

We can verify the successfull creation of routes in AWS Console by visiting the route table (`my-rt`) ,we created with terraform.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/44.png)

### Why This is Necessary:

Each node in your Kubernetes cluster operates on its own subnet, and without proper routing, pods on different nodes cannot communicate. By adding these routes, we ensure that traffic originating from a pod on one node can reach pods on another node by passing through the appropriate network interfaces.

This is a key step for enabling inter-pod communication across the cluster, allowing services running on different nodes to communicate with each other seamlessly.

Now you will be able to ping the pods on different nodes.

### Test The Connectivity


```bash
kubectl exec -it bash-worker-1 -- /bin/bash
```

From `bash-worker-1` we ping `bash-worker-2` which is in different node(`worker-2`)

```bash
ping  10.244.2.3 -c 5
```
We also ping `nginx-worker-2` 

```bash
ping 10.244.2.2 -c 5
```

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/c3f77ff15cea059b33ab1fee2c4441d9b0a90987/Poridhi%20Labs/Kubernetes%20Tasks/Custom%20CNI%20Plugins%20in%20Kubernetes/Lab-5/images/43.png)

Both are successfull.Which suggest that our connection is working properly.

## **Conclusion**

In this lab, we successfully configured:

- Pod-to-pod communication within and across nodes.
- NAT to enable external access for the pods.

By adjusting iptables rules, setting up routes, and configuring NAT, we ensured that pods can communicate with each other and access external networks.