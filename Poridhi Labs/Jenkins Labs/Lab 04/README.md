# Configuring Docker Containers as Build Agents in Jenkins

In this lab, we will walk through the steps for configuring Docker containers as build agents (slaves) for Jenkins. This setup allows Jenkins to dynamically provision build agents on Docker containers, optimizing resource usage and providing scalability.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/jenkins-agent.svg)

## Docker Containers as Build Agents/Slaves

Docker containers can serve as build agents for Jenkins, allowing for isolated and reproducible build environments. This setup can be beneficial for testing and building projects in a consistent manner. To accomplish this task, we will

1. Configure a Docker Host With Remote API
2. Create a Jenkins Agent Docker Image
3. Install Docker Plugin
4. Create and configure the docker cloude agent
5. Test Jenkins Build Inside a Docker Container


### Install and Run Jenkins Server

To install and run Jenkins server, follow the steps below:

**1. Create a file named `jenkins-install.sh` and fill it with the following code:**

```sh
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

# Set Jenkins port (default 8081 or use command line argument)
JENKINS_PORT=${1:-8081}

print_message "Starting Jenkins installation..."
print_message "Jenkins will be configured to run on port: $JENKINS_PORT"

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

# Configure Jenkins port
print_message "Configuring Jenkins port..."
sed -i "s/HTTP_PORT=.*/HTTP_PORT=$JENKINS_PORT/" /etc/default/jenkins
sed -i "s/--httpPort=[0-9]*/--httpPort=$JENKINS_PORT/" /etc/default/jenkins
check_status "Port configuration completed"

# Update systemd service file
print_message "Updating systemd service..."
sed -i "s|^ExecStart=.*|ExecStart=/usr/bin/jenkins --httpPort=$JENKINS_PORT|" /lib/systemd/system/jenkins.service
check_status "Systemd service updated"

# Reload systemd and restart Jenkins
print_message "Restarting Jenkins..."
systemctl daemon-reload
systemctl restart jenkins
check_status "Jenkins restart completed"

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
print_message "Access Jenkins at: http://your-server-ip:$JENKINS_PORT"
```

#### Run the script by executing the following command:

```sh
sudo chmod +x jenkins-install.sh
./jenkins-install.sh
```

### Access Jenkins Dashboard

This lab is intended to be run on a `Poridhi's VM`. To access the Jenkins dashboard, We need to create a Load Balancer. First Go to the `Load Balancer` section and create a Load Balancer using the VM's private IP and port `8081`.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-20.png)

Then access the Jenkins dashboard using the Load Balancer's URL. Use the credentials `admin` and the password you received from the Jenkins installation script.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-21.png)


#### Jenkins login page

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-22.png)

## Step by step guide

## Step 01: Configure a Docker Host With Remote API

To use Docker containers as build agents, you need to set up a Docker host that Jenkins can connect to. Follow these steps:

**1. Spin Up a VM and Install Docker**
- Spin up a virtual machine (VM) or use an existing server. Here we using a aws ec2 instance.
- Install Docker based on your operating system. Refer to the [official Docker documentation](https://docs.docker.com/get-docker/) for installation instructions.
- Ensure the Docker service is running.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-1.png)

**2. Enable Docker Remote API**
- Log in to the server and open the Docker service file located at `/lib/systemd/system/docker.service`.

    ```sh
    vim /lib/systemd/system/docker.service
    ```

- Search for the `ExecStart` line and replace it with:
    ```bash
    ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock
    ```
    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-2.png)

- Save and close the file.

- Reload and restart the Docker service:

    ```bash
    sudo systemctl daemon-reload
    sudo service docker restart
    ```

**3. Validate the Remote API**
- Use the following `curl` commands to validate that the Docker Remote API is accessible. Replace `54.221.134.7` with your Docker host IP address:

    ```bash
    curl http://localhost:4243/version
    curl http://54.221.134.7:4243/version
    ```
- Ensure the Docker Remote API is working by referring to the [Docker API documentation](https://docs.docker.com/engine/api/v1.41/).

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-3.png)

## Step 02: Create a Jenkins Agent Docker Image

To configure a Docker container as a Jenkins build agent, create a Docker image with the following requirements:

**1. Dockerfile Example**

- Create a Dockerfile that sets up the Jenkins agent environment. Below is a sample Dockerfile for a `Maven-based` Jenkins agent:

    ```Dockerfile
    # Use an official Ubuntu base image
    FROM ubuntu:18.04

    LABEL maintainer="your_mail@gmail.com"

    # Update package repository and install necessary packages
    RUN apt-get update && \
        apt-get install -qy \
            openjdk-8-jdk \
            maven \
            openssh-server \
            git && \
        apt-get clean

    # Create Jenkins user
    RUN adduser --quiet jenkins && \
        echo "jenkins:jenkins" | chpasswd

    # Set up SSH
    RUN mkdir -p /var/run/sshd && \
        echo "jenkins:jenkins" | chpasswd

    # Copy SSH authorized keys if you have them
    # Uncomment and adjust the path as needed
    # COPY .ssh/authorized_keys /home/jenkins/.ssh/authorized_keys

    # Ensure permissions are correct
    RUN chown -R jenkins:jenkins /home/jenkins && \
        chmod 700 /home/jenkins/.ssh && \
        chmod 600 /home/jenkins/.ssh/authorized_keys

    # Expose SSH port
    EXPOSE 22

    # Start SSH service
    CMD ["/usr/sbin/sshd", "-D"]
    ```
- Now build the image and push it to dockerhub.

**2. You can also use this image, without building your own image.**

```sh
konami98/jenkins-agent:latest
```

## Step 03: Install Docker Plugin

To use docker as a build agent, we need to install the docker plugin in jenkins. Follow these steps:

- Navigate to **Jenkins Dashboard** → **Manage Jenkins** → **Manage Plugins**.
- Search for the **Docker** plugin under the **Available** tab, install it, and restart Jenkins.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-4.png)

## Step 04: Create and configure the docker cloude agent

1. Go to **Jenkins Dashboard** → **Manage Jenkins** → **Configure System** and Scroll to the **Cloud** section.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-5.png)

2. Create new cloud and give a name for example `Docker-slave`

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-6.png)

3. **Configure Docker Cloud Details**:

    - Docker Host URL: Fill up this with your docker agent Ip.
    - Check the Test connection.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-7.png)


4. **Add Docker Agent Template**
   - Under the **Docker Agent Template** section, click **Add Docker Template** and configure:
     - **Labels**: Use labels to identify the Docker agents, e.g., `docker-agent`.
     - Enable the checkbox.
     - **Name**: Use a Name, e.g., `docker-agent`
     - **Docker Image**: Specify the Docker image you created, e.g., `yourusername/jenkins-agent:latest`. or `konami98/jenkins-agent:latest`.

     ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-8.png)


     - **Remote File System Root**: Set to `/home/jenkins` as specified in the dockerfile.
     - **Connection Method**: Select `Connect with SSH`
        - In the `Connect with SSH` method, select **SSH-key**: Inject SSH key
        - **User**: jenkins (specified in the docker file)

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-9.png)

5. After configuring the agent, create or save the confugaration details.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-10.png)


## Test Jenkins Build Inside a Docker Container

1. **Create a Freestyle Job**
   - Go to **Jenkins Dashboard** → **New Item** and create a freestyle project.

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-11.png)

   - Under **Build Environment**, select **Restrict where this project can be run** and choose the Docker agent label you configured.

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-12.png)

2. **Add Build Steps**

    Add a build step to execute a shell command. For example,

    ```sh
    echo "Hello from docker agent"
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-13.png)

3. **Run and Verify**

   - Save and run the job. Jenkins will deploy a Docker container as the build agent, execute the build steps, and then clean up the container.
   - Check the build logs in the console output to ensure that the build was executed correctly inside the Docker container.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-14.png)

   - You can also check the cloud statistics.

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2004/images/image-15.png)

## Conclusion

By configuring Docker containers as Jenkins build agents, you can leverage isolated and scalable build environments. This setup allows Jenkins to dynamically allocate resources and execute builds efficiently. By following the steps outlined in this guide to configure Docker containers as build agents, you can optimize your Jenkins CI/CD pipeline.

