# Automating Docker Image Builds and Pushes to Docker Hub using Jenkins

In this lab, we will walk through the process of setting up a CI/CD pipeline using Jenkins to build Docker images from a Node.js application and push them to Docker Hub. The pipeline will be set up on an AWS EC2 instance running Ubuntu, ensuring an automated, streamlined approach to deploying applications. By the end of this tutorial, you will have a fully functioning Jenkins server capable of building Docker images and pushing them to your Docker Hub repository upon each commit to your GitHub repository.

![alt text](./images/jenkins-pipeline.drawio.svg)

## Prerequisites

- AWS account
- Basic knowledge of AWS EC2, Jenkins, Docker, and Git
- GitHub account
- Docker Hub account

## Step 1: Set Up AWS EC2 Instance

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/pulumi-diagram.png)

1. Configure AWS CLI with your credentials:

   ```
   aws configure
   ```

2. Create a new directory for the project:

   ```
   mkdir infra
   cd infra
   ```

3. Initialize a new Pulumi project:

   ```
   pulumi new aws-python
   ```

4. Generate an SSH key pair:

   Generate a new SSH key pair on your local machine. This key pair will be used to SSH into the EC2 instances.

   ```
   ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa_pulumi
   ```

   This will generate two files, typically in the `~/.ssh` directory:

   - `id_rsa_pulumi` (private key)
   - `id_rsa_pulumi.pub` (public key)

   Go to the SSH Folder

   Navigate to the `.ssh` directory where the keys were generated.

   ```sh
   cd ~/.ssh
   ```

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-01.png)


## Project Structure

```
infra/
│
├── __main__.py          # Main Pulumi program
├── requirements.txt     # Python dependencies
├── Pulumi.dev.yaml
└── Pulumi.yaml          # Pulumi project file
```

## Code

Replace the contents of `__main__.py` with the following code:

```python
import pulumi
from pulumi_aws import ec2, get_availability_zones
import os

# Create a new VPC
vpc = ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "my-vpc"})

# Create an Internet Gateway
igw = ec2.InternetGateway("my-igw",
    vpc_id=vpc.id,
    tags={"Name": "my-igw"})

# Create a public subnet
public_subnet = ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone=get_availability_zones().names[0],
    tags={"Name": "public-subnet"})

# Create a route table
route_table = ec2.RouteTable("public-route-table",
    vpc_id=vpc.id,
    routes=[ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=igw.id,
    )],
    tags={"Name": "public-route-table"})

# Associate the route table with the public subnet
route_table_association = ec2.RouteTableAssociation("public-route-table-association",
    subnet_id=public_subnet.id,
    route_table_id=route_table.id)

# Create a security group for SSH access
ssh_security_group = ec2.SecurityGroup("ssh-security-group",
    description="Allow SSH access",
    vpc_id=vpc.id,
    ingress=[
      ec2.SecurityGroupIngressArgs(
        description="SSH from anywhere",
        from_port=22,
        to_port=22,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
      ),
      ec2.SecurityGroupIngressArgs(
        description="HTTP from anywhere",
        from_port=8080,
        to_port=8080,
        protocol="tcp",
        cidr_blocks=["0.0.0.0/0"],
      ),
    ],
    egress=[ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol="-1",
        cidr_blocks=["0.0.0.0/0"],
    )],
    tags={"Name": "ssh-security-group"})


# Create a new key pair
key_pair = ec2.KeyPair("my-key-pair",
    key_name="my-key-pair",
    public_key=open(os.path.expanduser("~/.ssh/id_rsa_pulumi.pub")).read())

# Create an EC2 instance
instance = ec2.Instance("jenkins-instance",
    instance_type="t2.micro",
    ami="ami-060e277c0d4cce553",  # Ubuntu Server AMI (HVM), SSD Volume Type
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[ssh_security_group.id],
    key_name=key_pair.key_name,
    tags={"Name": "jenkins-instance"})

# Output the public IP of the instance
pulumi.export("instance_public_ip", instance.public_ip)

# Output a command to SSH into the instance
pulumi.export("ssh_command", pulumi.Output.concat("ssh -i ~/.ssh/id_rsa_pulumi ubuntu@", instance.public_ip))
```

## Deployment

1. Ensure you're in the project directory.

2. Deploy the infrastructure:

   ```
   pulumi up
   ```

3. Review the proposed changes and confirm by typing 'yes'.

4. Wait for the deployment to complete. Pulumi will output the public IP of the EC2 instance and an SSH command.

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-02.png)

## Check Inbound Rules of EC2 Instance

Check rules to allow SSH (port 22) and Jenkins (port 8080) access:

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-03.png)

## Accessing the EC2 Instance

Use the SSH command provided in the Pulumi output to connect to your EC2 instance:

```sh
ssh -i ~/.ssh/id_rsa_pulumi ubuntu@<public-ip>
```

Replace `<public-ip>` with the actual IP address provided in the output.

## Step 2: Install Jenkins on EC2

1. **Update the Package Manager**:

   Run the following command to update the package manager:

   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Install Java (required for Jenkins)**:

   ```bash
   sudo apt install openjdk-11-jdk -y
   ```

3. **Add Jenkins Repository and Install Jenkins**:

   ```bash
   # Download the Jenkins key and add it to the trusted key list
   wget -q -O - https://pkg.jenkins.io/debian/jenkins.io-2023.key | sudo tee /etc/apt/trusted.gpg.d/jenkins.asc

   # Add the Jenkins repository to the sources list
   sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'

   # Update the package list
   sudo apt update

   # Install Jenkins
   sudo apt install jenkins -y
   ```

4. **Start and Enable Jenkins**:

   ```bash
   sudo systemctl start jenkins
   sudo systemctl enable jenkins
   ```

   Check the status of the jenkins using:

   ```bash
   sudo systemctl status jenkins
   ```

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-06.png)

## Step 3: Install Docker on EC2

Run the following command to update the package manager:

```
sudo apt update
sudo apt install vim -y
```

### Save this install.sh

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

```bash
chmod +x install.sh
```

```bash
./install.sh
```

**Add Jenkins User to Docker Group**:

```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

## Step 4: Open Jenkins in a Web Browser

- Retrieve the initial admin password:

  ```bash
  sudo cat /var/lib/jenkins/secrets/initialAdminPassword
  ```

- Open your browser and navigate to `http://your-ec2-public-dns:8080`.

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-04.png)

- Enter the initial admin password.
- Follow the setup wizard to complete the installation (install suggested plugins, create an admin user, etc.).

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-05.png)

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-06.png)

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-07.png)

- **Install Docker Pipeline Plugin (if not installed)**:

  If you do not find the Docker Pipeline plugin in the list, switch to the `Available` tab.
  Search for `Docker Pipeline`. Check the box next to `Docker Pipeline` and click `Install without restart` or `Install and restart` if you prefer.

  ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-08.png)

## Step 5: Create Node.js Application

1. **Create `app.js`**:

   ```javascript
   // app.js

   const express = require("express");
   const app = express();
   const port = 8080;

   app.get("/", (req, res) => {
     res.send("Hello, World!");
   });

   app.listen(port, () => {
     console.log(`App listening at http://localhost:${port}`);
   });
   ```

2. **Create `package.json`**:

   ```json
   {
     "name": "simple-node-app",
     "version": "1.0.0",
     "description": "A simple Node.js app",
     "main": "app.js",
     "scripts": {
       "start": "node app.js"
     },
     "author": "Your Name",
     "license": "ISC",
     "dependencies": {
       "express": "^4.17.1"
     }
   }
   ```

   Use `npm install` to install all the dependencies and run `npm start` to start the nodejs application.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-05.png)

3. **Create `Dockerfile`**:

   ```Dockerfile
   FROM node:14

   WORKDIR /usr/src/app

   COPY package*.json ./

   RUN npm install

   COPY . .

   EXPOSE 8080

   CMD ["node", "app.js"]
   ```

## Step 6: Push Code to Git Repository

1. **Initialize Git Repository**:

   ```bash
   git init
   ```

2. **Add Files and Commit**:

   ```bash
   git add .
   git commit -m "Initial commit"
   ```

3. **Create a Repository on GitHub**:

   - Go to GitHub and create a new repository.

4. **Add Remote and Push**:

   ```bash
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

## Step 7: Configure Jenkins Pipeline

1. **Open Jenkins Dashboard**:

   - Navigate to `http://your-ec2-public-dns:8080`.

2. **Add Docker Hub Credentials to Jenkins**:

   - Go to `Manage Jenkins` -> `Credentials` -> `(global)` -> `Add Credentials`.

      ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-09.png)

   - Select `Kind` as `Username with password`.
   - Enter your Docker Hub username and password.
   - Optionally, provide an ID for these credentials (e.g., `docker-hub-credentials`).

      ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-10.png)

3. **Create a New Pipeline Job**:

   - Click on `New Item`.
   - Enter a name for your job, select `Pipeline`, and click `OK`.

      ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-11.png)

4. **Define the Pipeline Script**:
   - Go to the job configuration page by clicking on the job name and then `Configure`.
   - In the `General` section, select `Github Project` and give the url of the project repository.
   - Select `GitHub hook trigger for GITScm polling` from `Build Triggers`.
   - In the `Pipeline` section, select `Pipeline script`.
   - For getting the pipeline syntax for `checkout` and `withCredentials` select `Pipeline Syntax` and get the syntax by filling up the necessary information.

      For Example, for `checkout` github repository

      ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-12.png)

   - You don't need to add github credentails if you are using a public git repository.
   - Enter the following Groovy script with the syntax you generated:

```groovy
pipeline {
    agent any

    environment {
        DOCKER_HUB_REPO = 'your-dockerhub-username/your-repo'
        DOCKER_HUB_CREDENTIALS_ID = 'docker-hub-credentials'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/your-username/your-repo.git']])
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def customImage = docker.build("my-app:${env.BUILD_NUMBER}")
                    customImage.inside {
                        sh 'echo "Docker image built successfully"'
                    }
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USERNAME')]) {
                        sh 'echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKER_HUB_USERNAME --password-stdin'
                    }
                }
            }
        }

        stage('Tag and Push Docker Image') {
            steps {
                script {
                    def imageTag = "${env.DOCKER_HUB_REPO}:latest"
                    def imageTagBuildNumber = "${env.DOCKER_HUB_REPO}:${env.BUILD_NUMBER}"
                    sh "docker tag my-app:${env.BUILD_NUMBER} ${imageTag}"
                    sh "docker tag my-app:${env.BUILD_NUMBER} ${imageTagBuildNumber}"

                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_HUB_USERNAME', passwordVariable: 'DOCKER_HUB_PASSWORD')]) {
                        sh "docker push ${imageTag}"
                        sh "docker push ${imageTagBuildNumber}"
                    }
                }
            }
        }
    }

    post {
        always {
            sh "docker rmi my-app:${env.BUILD_NUMBER} || true"
            sh "docker rmi ${env.DOCKER_HUB_REPO}:latest || true"
            sh "docker rmi ${env.DOCKER_HUB_REPO}:${env.BUILD_NUMBER} || true"
        }
    }
}
```

Replace the github repo and dockerhub credentials with your credentials.

## Step 8: Verify Jenkins Pipeline Execution

1. **Save the Job Configuration**:

   - After entering the pipeline script, click `Save`.

2. **Build the Pipeline**:

   - On the job page, click `Build Now` to run the pipeline.
   - Monitor the build progress and check for any errors.

3. **Check Jenkins Console Output**:

   - Click on the build number and then `Console Output`.
   - Ensure each stage completes successfully without errors.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-01.png)

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-02.png)

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-03.png)

## Step 9: Verification of Docker Image on Docker Hub

1. **Log In to Docker Hub**:

   - Open a web browser and go to [Docker Hub](https://hub.docker.com/).
   - Log in with your Docker Hub credentials.

2. **Navigate to Your Repository**:

   - In your Docker Hub dashboard, go to the repository specified in your Jenkins pipeline (`your-dockerhub-username/your-repo`).
   - Verify that the new image with the correct tag(s) (`latest` and `BUILD_NUMBER`) is present.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-04.png)

## Step 10: Configure GitHub Webhook that Notifies Jenkins of New Commits

1. **Add a Webhook**:

   - Go to your GitHub repository where your Node.js application is hosted.
   - Click on the Settings tab of your repository.
   - In the left sidebar, click on `Webhooks`.
   - Click the `Add webhook` button.
   - In the Payload URL field, enter your Jenkins server's URL followed by /github-webhook/. For example:

   ```bash
   http://your-ec2-public-dns:8080/github-webhook/
   ```

   - In the Content type field, select `application/json`
   - Choose `Just the push event` to trigger the webhook on pushes to the repository.
   - Click the `Add webhook` button to save the webhook configuration.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-13.png)

2. **Configure Jenkins Job to Use GitHub Webhook**:

   - Go to your Jenkins server and click on the `Configure` link of your Jenkins job.
   - In the `Build Triggers` section, select `GitHub hook trigger for GITScm polling`
   - Click `Save` to save the configuration.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-14.png)

3. **Verify Setup**:

   - Make a change to your repository and push the commit to GitHub.
   - Wait for a few minutes and check the Jenkins job's build history to see if the build
     was triggered by the webhook.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-07.png)

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Test-Demo/main/images/jenkins-new-15.png)

## Conclusion

By following these steps, you will successfully set up Jenkins on an AWS EC2 instance, build a Docker image for a Node.js application, and push it to Docker Hub automatically. This setup ensures that your application is built, tested, and deployed with minimal manual intervention, enhancing your development workflow.
