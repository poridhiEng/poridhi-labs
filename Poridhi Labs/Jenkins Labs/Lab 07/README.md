# Build a Java application with Maven using Jenkins Agent node

This guide demonstrates how to use Jenkins to build a Java application with Maven. For this tutorial, we are using the Jenkins agents for handling build jobs. Additionally, we will use a Freestyle project for this setup. In future configurations, we will explore using pipeline projects.

The lab covers the following tasks:

1. Create a Jenkins job to build and test a Java application using Maven.
2. Run the Jenkins job on `agent node` to build and test the Java application.
3. View the build results in Jenkins.
4. Configure the job to deploy the JAR file locally.
5. Visualize the build results graphically.

The example Java application is a simple Java application that outputs "Hello world!" and includes unit tests. The test results are saved in a **JUnit XML report**, which will be used for visualization.

Here is the graphical representation of what we will do in this lab.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/lab-7-arch.drawio.svg)

## Prerequisites

1. Ensure your Jenkins server is up and running.
2. Ensure Jenkins agent node connected to the controller and online.
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-10.png)
3. Java is installed in the Agent node. Check it by running `java --version`. Make sure to have the same version of java both in Jenkins controller node and agent node.
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image.png)


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

Run the script by executing the following command:

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


## Step-by-Step Guide

### Step 1: Install Necessary Plugins and Tools

**1. Install the Maven Integration Plugin:**
- Go to **Manage Jenkins** -> **Manage Plugins**.
- In the **Available** tab, search for `Maven Integration (Build Tools)`.
- Install this plugin.

   ![Install Maven Integration Plugin](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-4.png?raw=true)

**2. Configure Maven Installation:**
- Go to **Manage Jenkins** -> **Global Tool Configuration**.
- Scroll down to the **Maven** section.
- Add a new Maven installation:
   - Give it a name, e.g., `Maven-jenkins`.
   - Select the required version and save.

   ![Configure Maven Installation](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-5.png?raw=true)

### Step 2: Create a Jenkins Job

1. Log in to your Jenkins server and click on **New Item**.
2. Enter a name for your job, e.g., "**Simple Java Maven App**", and select **Freestyle project**.
3. Click **OK** to create the job.

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-1.png)

4. Mark `Restrict where this project can be run` and add the Label of your agent node.

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-2.png)

5. In the **Source Code Management** section, select **Git** and enter the URL of the GitHub repository:

   ```sh
   https://github.com/Konami33/simple-java-maven-app
   ```

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-3.png)

5. Save the configuration and build the job. This will clone the repository from GitHub.

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-4.png)

### Step 3: Configure the Build Step

1. Go to the **Configure** section of the job.
2. In the **Build** section, click **Add build step** and select **Invoke top-level Maven targets**.

   ![Add Build Step](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-6.png?raw=true)

3. Select your `Maven Version`.

4. In the **Goals** field, enter the following command to clean, package, and skip tests:

   ```sh
   -B -DskipTests clean package
   ```

   ![Configure Maven Goals](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-7.png?raw=true)

### Step 4: Configure the Test Step

1. Go to the **Configure** section of the job.
2. In the **Build** section, click **Add build step** and select **Invoke top-level Maven targets**.
3. Select your `Maven Version`.
4. In the **Goals** field, enter the following command to run tests:

   ```sh
   test
   ```

   ![Configure Test Goals](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-9.png?raw=true)


### Step 5: Deploy the JAR File

1. Go to the **Configure** section of the job.
2. In the **Build** section, click **Add build step** and select **Execute shell**.
3. In the **Command** field, enter the command to run the JAR file:

   ```sh
   java -jar <path_to_your_jar_file>
   ```

   Replace `<path_to_your_jar_file>` with the path to your JAR file, typically found in `/var/jenkins_home/workspace/your_job_name/target/`.

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-5.png)

### Step 6: Build the job

Build the job and check the output console for any error.

**build step:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-6.png)

**test step:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-7.png)

**deploy step:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-8.png)

### Step 7: Visualize the Build Results

1. In the **Workspace** directory of the job, navigate to:

   **Workspace** -> **YOUR_JOB_NAME** -> **target** -> **surefire-reports**. Locate the XML file containing the build information.

2. Return to the job configuration and scroll down to **Post-build Actions**. Click **Add post-build action** and select **Publish JUnit test result report**.

   ![Add Post-build Action](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2006/images/image-15.png?raw=true)

3. In the **Test report XMLs** field, enter the path to the XML files:

   ```sh
   target/surefire-reports/*.xml
   ```

   ![Configure Test Result Report](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2006/images/image-16.png?raw=true)

4. Save the configuration and build the job. This will publish the test results on the Jenkins dashboard with graphical representations such as graphs and charts.

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2007/images/image-9.png)

## Conclusion

You have successfully set up Jenkins to build, test, deploy, and visualize the results of a Java application using Maven.  