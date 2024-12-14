# Jenkins Installation on Ubuntu

This guide will walk you through the process of installing Jenkins on an Ubuntu server using recommended configurations. Jenkins is an open-source automation server that is widely used for Continuous Integration (CI) and Continuous Delivery (CD) in software development. It allows developers to automate various stages of their development processes, such as building, testing, and deploying applications.

## Prerequisites

- A server running Ubuntu with sudo access.
- Basic understanding of Linux command line operations.

## Install Jenkins on Ubuntu With Recommended Configurations

### Step 1: Update Package List

Before installing Jenkins, update your server's package list:

```bash
sudo apt -y update
```

### Step 2: Install Java Runtime

Jenkins requires Java to run. Install OpenJDK 11:

```bash
sudo apt install default-jdk -y
```

Make sure java is installed successfully using:

```bash
java -version
```

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2001/images/jen-install-01.png)

### Step 3: Add Jenkins Debian Repository

Add the Jenkins repository and import the GPG keys:

```bash
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
```

### Step 4: Update Package List Again

Refresh the package list to include Jenkins packages:

```bash
sudo apt update -y
```

### Step 5: Install Jenkins

Install the latest Long-Term Support (LTS) version of Jenkins:

```bash
sudo apt-get install jenkins -y
```

### Step 6: Start and Enable Jenkins Service

Start Jenkins and enable it to run at boot:

```bash
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

To verify that Jenkins is running:

```bash
sudo systemctl status jenkins
```

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2001/images/jen-install-02.png)

### Step 7: Access Jenkins

By default, Jenkins runs on port 8080. You can access it by navigating to `http://your_server_ip:8080` in your web browser.

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2001/images/jen-install-03.png)

### Step 8: Unlock Jenkins

To unlock Jenkins, retrieve the initial administrative password:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Enter the password on the Jenkins setup page to proceed.

### Step 9: Install Suggested Plugins

During the initial setup, choose "Install Suggested Plugins." This will install all the required plugins for building and managing Jenkins projects. The installation might take a few minutes.

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2001/images/jen-install-04.png)

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2001/images/jen-install-05.png)

### Step 10: Create Admin User

After the plugins are installed, you will be prompted to create an admin user. Enter the desired username and password, then click "Save and Finish."

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2001/images/jen-install-06.png)

## Installing Jenkins Using Docker

If you prefer to run Jenkins within a Docker container, follow these steps:

1. Ensure Docker is installed on your server.
2. Deploy Jenkins using Docker:

   ```bash
   docker run -p 8080:8080 -p 50000:50000 --name jenkins jenkinsci/jenkins:latest
   ```

To persist data, mount a host volume to the container:

```bash
docker run -p 8080:8080 -p 50000:50000 -v /home/ubuntu:/var/jenkins_home jenkinsci/jenkins:latest
```

## Conclusion

This guide has provided step-by-step instructions to install Jenkins on an Ubuntu server. With Jenkins installed on your Ubuntu server, you are now equipped to automate your development processes, reducing manual effort, minimizing errors, and accelerating your software delivery pipeline.
