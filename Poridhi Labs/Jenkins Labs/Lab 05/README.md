# Running Jenkins on Port 80: Two Different Methods

By default, Jenkins runs on port 8080 after installation. However, there are scenarios, especially in production environments, where you may need Jenkins to be accessible on port 80, the default port for HTTP traffic. This document outlines two effective methods to achieve this:

1. **Using IP Table Forwarding Rule**: A straightforward approach that redirects traffic from port 80 to Jenkins's default port 8080.
2. **Using Nginx as a Reverse Proxy**: A robust and scalable solution ideal for production environments, where Nginx handles traffic on port 80 and forwards it to Jenkins on port 8080.

Both methods will be demonstrated on two separate EC2 instances, ensuring a clear and practical understanding of the setup process.

![alt text](./images/jenkins-port.svg)

## Prerequisites
- Create two EC2 instances for checking both the methods.
- Ensure your jenkins server is up and running in both the instances.

## Create EC2 Instances

### Configure AWS CLI

- Configure AWS CLI with the necessary credentials. Run the following command and follow the prompts to configure it:

  ```bash
  aws configure
  ```

  This command sets up your AWS CLI with the necessary credentials, region, and output format.

  ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2005/images/image.png)

- You will find the `AWS Access key` and `AWS Seceret Access key` on Lab description page,where you generated the credentials. 

  ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2005/images/image-1.png)

### Setup a Pulumi Project

Now, let's create a new Pulumi project and write the code to provision our EC2 instances.

1. **Create a new directory and initialize a Pulumi project:**

   ```bash
   mkdir jenkins-pulumi && cd jenkins-pulumi
   pulumi new aws-javascript
   ```

    This command creates a new directory with the basic structure for a Pulumi project. Follow the prompts to set up your project.

2. **Create Key Pair:**

    Create a new key pair for our instances using the following command:

    ```sh
    aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > MyKeyPair.pem
    ```

3. **Set File Permissions of the key files:**

    ```sh
    chmod 400 MyKeyPair.pem
    ```

4. **Replace the contents of `index.js` with the following code:**

    ```js
    const pulumi = require("@pulumi/pulumi");
    const aws = require("@pulumi/aws");

    // Create a VPC
    const vpc = new aws.ec2.Vpc("lab-vpc", {
        cidrBlock: "10.0.0.0/16",
        enableDnsHostnames: true,
        enableDnsSupport: true,
        tags: {
            Name: "lab-vpc",
        },
    });
    exports.vpcId = vpc.id;

    // Create a public subnet
    const publicSubnet = new aws.ec2.Subnet("lab-subnet", {
        vpcId: vpc.id,
        cidrBlock: "10.0.1.0/24",
        availabilityZone: "ap-southeast-1a",
        mapPublicIpOnLaunch: true,
        tags: {
            Name: "lab-subnet",
        },
    });
    exports.publicSubnetId = publicSubnet.id;

    // Create an Internet Gateway
    const internetGateway = new aws.ec2.InternetGateway("lab-igw", {
        vpcId: vpc.id,
        tags: {
            Name: "lab-igw",
        },
    });
    exports.igwId = internetGateway.id;

    // Create a Route Table
    const publicRouteTable = new aws.ec2.RouteTable("lab-rt", {
        vpcId: vpc.id,
        tags: {
            Name: "lab-rt",
        },
    });
    exports.publicRouteTableId = publicRouteTable.id;

    // Create a route for the Internet Gateway
    const route = new aws.ec2.Route("igw-route", {
        routeTableId: publicRouteTable.id,
        destinationCidrBlock: "0.0.0.0/0",
        gatewayId: internetGateway.id,
    });

    // Associate the Route Table with the Subnet
    const rtAssociation = new aws.ec2.RouteTableAssociation("rt-association", {
        subnetId: publicSubnet.id,
        routeTableId: publicRouteTable.id,
    });

    // Create a Security Group for the EC2 Instances
    const labSecurityGroup = new aws.ec2.SecurityGroup("lab-secgrp", {
        vpcId: vpc.id,
        description: "Allow SSH and HTTP access",
        ingress: [
            { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] }, // SSH
            { protocol: "tcp", fromPort: 80, toPort: 80, cidrBlocks: ["0.0.0.0/0"] }, // HTTP
            { protocol: "tcp", fromPort: 8080, toPort: 8080, cidrBlocks: ["0.0.0.0/0"] }, // Jenkins
        ],
        egress: [
            { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] }, // Allow all outbound traffic
        ],
        tags: {
            Name: "lab-secgrp",
        },
    });
    exports.labSecurityGroupId = labSecurityGroup.id;

    // Define an AMI for the EC2 instances
    const amiId = "ami-01811d4912b4ccb26"; // Ubuntu 24.04 LTS

    // Create EC2 Instances
    const createInstance = (name) => {
        return new aws.ec2.Instance(name, {
            instanceType: "t2.micro",
            vpcSecurityGroupIds: [labSecurityGroup.id],
            ami: amiId,
            subnetId: publicSubnet.id,
            keyName: "MyKeyPair", // Update with your key pair
            associatePublicIpAddress: true,
            tags: {
                Name: name,
                Environment: "Lab",
                Project: "JenkinsLab",
            },
        });
    };

    const method1Instance = createInstance("method-1-instance");
    const method2Instance = createInstance("method-2-instance");

    exports.method1InstanceId = method1Instance.id;
    exports.method1PublicIp = method1Instance.publicIp;
    exports.method2InstanceId = method2Instance.id;
    exports.method2PublicIp = method2Instance.publicIp;
    ```

5. **Deploy the infrastructure:**

   ```bash
   pulumi up
   ```

   ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2005/images/image-2.png)

This will create 2 EC2 instances, one for method 1 and one for method 2.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2005/images/image-3.png)

## Install Jenkins on both the instances

Now, ssh into both the instances and install Jenkins on both the instances using the following installation script:

1. Create a file named `jenkins_install.sh` and add the following code:

    ```bash
    #!/bin/bash

    # Function to print colored output
    print_message() {
        GREEN='\033[0;32m'
        NC='\033[0m'
        echo -e "${GREEN}$1${NC}"
    }

    # Function to check if command was successful
    check_status() {
        if [ $? -eq 0 ]; then
            print_message "✓ Success: $1"
        else
            echo "✗ Error: $1"
            exit 1
        fi
    }

    # Check if script is run as root
    if [ "$EUID" -ne 0 ]; then 
        echo "Please run as root (use sudo)"
        exit 1
    fi

    print_message "Starting Jenkins installation..."
    print_message "Jenkins will be configured to run on its default port: 8080"

    # Update system packages
    print_message "Updating system packages..."
    apt update
    apt upgrade -y
    check_status "System update completed"

    # Install Java
    print_message "Installing Java..."
    apt install -y openjdk-17-jre-headless
    check_status "Java installation completed"

    # Verify Java installation
    java -version
    check_status "Java verification"

    # Add Jenkins repository
    print_message "Adding Jenkins repository..."
    curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | tee \
        /usr/share/keyrings/jenkins-keyring.asc > /dev/null

    echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
        https://pkg.jenkins.io/debian-stable binary/ | tee \
        /etc/apt/sources.list.d/jenkins.list > /dev/null
    check_status "Jenkins repository added"

    # Install Jenkins
    print_message "Installing Jenkins..."
    apt update
    apt install -y jenkins
    check_status "Jenkins installation completed"

    # Start and enable Jenkins service
    print_message "Starting and enabling Jenkins service..."
    systemctl enable jenkins
    systemctl start jenkins
    check_status "Jenkins service started"

    # Wait for Jenkins to start
    print_message "Waiting for Jenkins to start..."
    sleep 30

    # Get initial admin password
    if [ -f /var/lib/jenkins/secrets/initialAdminPassword ]; then
        ADMIN_PASSWORD=$(cat /var/lib/jenkins/secrets/initialAdminPassword)
        print_message "Jenkins initial admin password: $ADMIN_PASSWORD"
    else
        echo "Warning: Could not find initial admin password"
    fi

    print_message "\nInstallation completed!"
    print_message "Please allow a few minutes for Jenkins to fully start"
    print_message "Access Jenkins at: http://your-server-ip:8080"
    ```

2. Execute the script:

    ```bash
    chmod +x jenkins_install.sh
    ```

3. Run the script:

    ```bash
    ./jenkins_install.sh
    ```

## Method 1: Using IP Table Forwarding Rule

This method involves creating an IP table forwarding rule that redirects traffic from port 80 to Jenkins's default port 8080. This is the simplest method and doesn't require additional software.

1. **Create the IP Table Forwarding Rule:**

    At first, find out the network interface name of the ec2 instance.

    ```
    ip a
    ```

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2005/images/image-4.png)

    Now, add the correct rule using the correct interface name (`enX0`):

    ```bash
    sudo iptables -A PREROUTING -t nat -i enX0 -p tcp --dport 80 -j REDIRECT --to-port 8080
    ```

2. **Save the IP Table Rules:**

    - For Ubuntu-based systems:

      ```bash
      sudo sh -c "iptables-save > /etc/iptables.rules"
      ```

Now, when you access Jenkins on port 80, the IP table rule will automatically forward the requests to port 8080. Find the public ip of the instance and access the jenkins on `http://<public-ip>:80`.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2005/images/image-5.png)

## Method 2: Running Jenkins Behind an Nginx Reverse Proxy

Using Nginx as a reverse proxy is a more robust solution, especially for production environments. Nginx will handle incoming traffic on port 80 and forward it to Jenkins on port 8080.

1. **Install Nginx:**

    - For Ubuntu-based systems:

      ```bash
      sudo apt-get install nginx
      ```

2. **Configure Nginx:**

    - Open the Nginx configuration file:

      ```bash
      sudo vi /etc/nginx/nginx.conf
      ```

    - Locate the following block:

      ```nginx
      location / {
      }
      ```

    - Modify it to include the Jenkins proxy settings:

      ```nginx
      location / {
          proxy_pass http://127.0.0.1:8080;
          proxy_redirect off;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
      ```

    - Note: If Nginx is running on a different server than Jenkins, replace `127.0.0.1` with your Jenkins server's IP address.

    - If the `location /` block isn't present in the default `nginx.conf` file, you can add the necessary configuration for Jenkins by creating a new server block or modifying an existing one. Here’s how you can do it:

    - **Create a new configuration file** for Jenkins:

      ```bash
      sudo vi /etc/nginx/sites-available/jenkins
      ```

    - **Add the following configuration** to this file:

      ```nginx
      server {
          listen 80;

          server_name your_domain_or_ip;

          location / {
              proxy_pass http://127.0.0.1:8080;
              proxy_redirect off;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
          }
      }
      ```

      Replace `your_domain_or_ip` with your server's domain name or public IP address of the instance.

    - **Enable the configuration** by creating a symbolic link to the `sites-enabled` directory:

      ```bash
      sudo ln -s /etc/nginx/sites-available/jenkins /etc/nginx/sites-enabled/
      ```


3. **Restart Nginx:**

    ```bash
    sudo systemctl restart nginx
    ```

    Check the status of the nginx using:

    ```bash
    sudo systemctl status nginx
    ```

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2005/images/image-6.png)

Now, Nginx will forward all requests on port 80 to Jenkins on port 8080. Now, find the public ip of the instance and access the jenkins on `http://<public-ip>:80`.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2005/images/image-7.png)

## Conclusion

This lab explored two effective methods to run Jenkins on port 80: **IP Table Forwarding** and **Nginx Reverse Proxy**. The IP table method is lightweight and quick to implement, making it ideal for test or non-critical environments. On the other hand, using Nginx provides a more robust and scalable solution, suitable for production setups where additional control and features like load balancing and SSL termination are required. Choose the method that suits your needs—simplicity for quick setups or scalability for production. Keep learning! 🚀