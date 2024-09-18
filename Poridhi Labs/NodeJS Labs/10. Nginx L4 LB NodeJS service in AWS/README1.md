# Nginx Layer 4 Load Balancing on Node.js servers (public subnet) in AWS

This document outlines the process of setting up a layer 4 load-balanced Node.js application environment using Nginx. The setup consists of two identical Node.js applications, an Nginx server for load balancing. Here we will deploy it in AWS.

![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/Diagram.png)

## Task
Create a load-balanced environment with two Node.js applications, Nginx as a load balancer, all running in AWS EC2 instance.

## Setup in AWS

## Create VPC, subnets, route table and gateways 

### Step 1: Create Your VPC
1. **Open the AWS Management Console** and search for "VPC" in the search bar.
2. On the left-hand side, click on "Your VPCs".
3. Click on "Create VPC" at the top right corner.

   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/create-vpc.jpeg)

4. Name your VPC using a tag.
5. Set the IPv4 CIDR block to `10.0.0.0/16`.

   Congratulations on creating your VPC!

### Step 2: Create a Public Subnet
1. After creating your VPC, click on "Subnets" on the left-hand side.
2. Click on "Create Subnet".

   <!-- ![Create Subnet](image) -->
   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/Create-subnet.jpeg)

3. Designate the VPC you just created.
4. Assign a CIDR block within your VPC’s range (e.g., `10.0.1.0/24`).
5. Click on the created subnet and then "Edit subnet settings".
6. Enable "Auto-assign public IPv4 address" and save.

   <!-- ![Enable Auto-assign IPv4](image) -->
   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/edit-subnet-settings.jpeg)

### Step 3: Create and Attach an Internet Gateway
1. Click on "Internet Gateways" on the left-hand side.
2. Click "Create internet gateway".

   <!-- ![Create Internet Gateway](image) -->
   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/create-internet-gateway.jpeg)

3. Once created, click "Actions" and then "Attach to VPC".
4. Select your VPC and attach the Internet Gateway.

   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/Attach-to-VPC.jpeg)

### Step 4: Create Route Tables
1. Click on "Route Tables" on the left-hand side.
2. Click "Create route table".
3. Associate the new route table with your VPC.
4. Edit the route table and add a route to allow internet traffic by specifying the destination `0.0.0.0/0` and target as your Internet Gateway.

    ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/edit-route.png)

    ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/add-route.png)

5. Click on the "Subnet Associations" tab, then "Edit Subnet Associations".
6. Select your public subnet and save.

   <!-- ![Associate Subnet](image) -->
   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/subnet-association.png)

### Network Diagram
Below is a visual representation of the VPC setup with subnets.

   <!-- ![VPC Network Diagram](image) -->
   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/resource-map.png)

### Step 5: Launch three EC2 Instances
1. In the AWS console, search for "EC2" and click on "Launch Instance".
2. Select the Ubuntu image for Amazon Linux.

   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/instance.png)

3. Choose the instance type, e.g., `t2.micro`.
4. Configure instance details, selecting the VPC and public subnet you created.
5. Create a key pair (.pem file) and save it securely.
6. Configure the security group to allow SSH (port 22) and HTTP (port 80) access.
7. Select `Number of instances` 3 for creating three instances.
8. Click "Launch".
9. Now rename the instances for deploying nginx and node applications.

### Step 6: Configuring Inbound Rules to Allow All Traffic

1. To allow all network traffic to your EC2 instance, navigate to the Amazon EC2 console, select "Security Groups" from the left pane, and choose the security group associated with your instance. 
2. Edit the inbound rules, add a rule for "All traffic" with the protocol set to "All" and the port range set to "All." For the source, select "Anywhere-IPv4" (0.0.0.0/0). Save the rules to apply the changes.

![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/nginx-inbound.png)

### Step 7: Access the EC2 Instance
1. Select your running instance in the EC2 console.
2. Click "Connect".

   <!-- ![Connect to Instance](image) -->
   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/ssh-connect.png)

3. SSH into the Public Instance:
   - Open a terminal where you saved the key pair and run:
     
     ```sh
     ssh -i MyKeyPair.pem ubuntu@<public_instance_ip>
     ```
     
   - Replace <public_instance_ip> with the public IP address of the public instance.

   ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/ssh-nginx.png)

Do this step to access all three instances.

## Set up Node.js Applications

Connect to `node-app-1` and configure as follows:

### Create Node App 1

Install npm:
```sh
sudo apt update
sudo apt install npm
```

Then, 
```bash
mkdir Node-app
cd Node-app
npm init -y
npm install express
```

Create `index.js` in the Node-app-1 directory with the following code:

```javascript
const express = require('express');
const app = express();
const port = process.env.PORT;

app.get('/', (req, res) => {
  res.status(200).send(`Hello, from Node App on PORT: ${port}!`);
});

app.listen(port, () => {
  console.log(`App running on http://localhost:${port}`);
});
```


### Create Node App 2

Connect to the `Node-app-2` instance. 
Here, do the similar steps as `Node-app-1`.
 

### Start Node.js Applications
Navigate to each Node.js application directory and run:
```bash
export PORT=3001
node index.js
```

Do the same for both nodejs app instances. Make sure they are running and connected to the database properly. Note that, you need to set the `PORT=3002` in `Node-app-2` instance.


## Set up Nginx

Now, connect to the `nginx` instance and create a `nginx.conf` file and a `Dockerfile`. You also need to install `Docker`. 

### Create Nginx Configuration
```bash
mkdir Nginx
cd Nginx
```

Create `nginx.conf` in the Nginx directory with the following configuration:

```nginx
events {}

stream {
    upstream nodejs_backend {
        server <Node-app-1 private-ip>:3001; # Node-app-1
        server <Node-app-2 private-ip>:3002; # Node-app-2
    }

    server {
        listen 80;

        proxy_pass nodejs_backend;

        # Enable TCP load balancing
        proxy_connect_timeout 1s;
        proxy_timeout 3s;
    }
}
```

Replace the private ip of nodejs app according to your ec2 instances.

This configuration sets up Nginx to act as a TCP load balancer, distributing traffic between the two Node.js applications. Let's break down the key components:

- `stream {}:` This block is used for TCP and UDP load balancing. It's different from the http {} block used in HTTP load balancing. It allows it to handle TCP and UDP traffic at the transport layer (Layer 4) of the OSI model.

- `upstream nodejs_backend {}:` This defines a group of backend servers. We're using host.docker.internal to refer to the host machine from within the Docker container. The ports 3001 and 3002 correspond to our two Node.js applications.

- `server {}:` This block defines the server configuration for the load balancer.
listen 80: This tells Nginx to listen on port 80 for incoming TCP connections.


This configuration provides a simple round-robin load balancing across our Node.js applications at the TCP level, which can be more efficient than HTTP-level load balancing for certain use cases.

### Install Docker in Nginx Instance

```
sudo apt update
sudo apt install vim -y
```
#### Save this install.sh 

```bash
#!/bin/bash

# Update package database
#!/bin/bash

# Update package database
echo "Updating package database..."
sudo apt update

# Upgrade existing packages
echo "Upgrading existing packages..."
sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker’s official GPG key
echo "Adding Docker’s GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker APT repository
echo "Adding Docker APT repository..."
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package database with Docker packages
echo "Updating package database with Docker packages..."
sudo apt update

# Install Docker
echo "Installing Docker..."
sudo apt install -y docker-ce

# Start Docker manually in the background
echo "Starting Docker manually in the background..."
sudo dockerd > /dev/null 2>&1 &

# Add current user to Docker group
echo "Adding current user to Docker group..."
sudo usermod -aG docker ${USER}

# Apply group changes
echo "Applying group changes..."
newgrp docker

# Set Docker socket permissions
echo "Setting Docker socket permissions..."
sudo chmod 666 /var/run/docker.sock

# Print Docker version
echo "Verifying Docker installation..."
docker --version

# Run hello-world container in the background
echo "Running hello-world container in the background..."
docker run -d hello-world

echo "Docker installation completed successfully."
echo "If you still encounter issues, please try logging out and logging back in."

```

```
chmod +x install.sh
./install.sh
```


### Create Dockerfile for Nginx
Create a file named `Dockerfile` in the Nginx directory with the following content:

```Dockerfile
FROM nginx:latest
COPY nginx.conf /etc/nginx/nginx.conf
```

### Build Nginx Docker Image
```bash
docker build -t custom-nginx .
```

This command builds a Docker image for Nginx with our custom configuration.

### Run Nginx Container
```bash
docker run -d -p 80:80 --name my_nginx custom-nginx
```

This command starts the Nginx container with our custom configuration.

## Verification

1. Visit `http://<nginx-public-ip>` in a web browser. You should see a response from one of the Node.js applications.

3. Refresh the browser or make multiple requests to observe the load balancing in action. You should see responses alternating between Node app 1 and Node app 2 running on different port.

    Example:

    ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/node-1-output.png)

    ![alt text](https://raw.githubusercontent.com/Minhaz00/NodeJS-Tasks/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/node-2-output.png)

## Conclusion

By configuring Nginx with the stream module as described, you have effectively set up Nginx as a `Layer 4 load balancer`. It handles TCP connections based on IP addresses and port numbers, making routing decisions at the transport layer without inspecting higher-layer protocols like HTTP. This setup is suitable for scenarios where efficient TCP load balancing across multiple backend services is required.