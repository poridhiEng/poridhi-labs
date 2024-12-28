# Creating and Managing Your First Jenkins Job

In this lab, we'll walk you through creating, configuring, and running your first Jenkins job. We'll also explore how to manage the job workspace, run script files, pass parameters to jobs, and schedule jobs to run periodically.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/Jenkins.drawio.svg)

## Install and Run Jenkins Server

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

## Access Jenkins Dashboard

This lab is intended to be run on a `Poridhi's VM`. To access the Jenkins dashboard, We need to create a Load Balancer. First Go to the `Load Balancer` section and create a Load Balancer using the VM's private IP and port `8081`.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-20.png)

Then access the Jenkins dashboard using the Load Balancer's URL. Use the credentials `admin` and the password you received from the Jenkins installation script.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-21.png)


Jenkins login page

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-22.png)

## Task 01: Create Your First Jenkins Job

### Step 2: Create a New Job

To create your first job:

1. Click on the `New Item` option on the Jenkins dashboard.
2. Enter a name for your job, such as `first-job`.
3. Select `Freestyle project` as the job type. This is the most basic type of Jenkins job, suitable for running simple tasks.

![Create New Job](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-1.png)

### Step 3: Configure Your Job

Once the job is created, you’ll be directed to the configuration page. Here’s how to set it up:

1. Scroll down to the `Build` section.
2. Click on `Add build step` and select `Execute shell` from the dropdown.
3. Enter a simple shell command, such as `echo "Hello, World!"`.
4. Save the configuration.

![Configure Job](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-2.png)

### Step 4: Build the Job

To run your job:

1. Navigate to your job’s dashboard.
2. Click the `Build Now` button to execute the job.

![Build Job](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-3.png)

After the build completes, you can view the output by clicking on the `Console Output` link. Here, you'll see details about the job execution, including the shell command output, the user who triggered the job, and the job’s workspace.

![Console Output](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-5.png)

Congratulations! You’ve successfully created and built your first Jenkins job.

## Task 02: Explore the Job Workspace

Each Jenkins job has a dedicated workspace where files related to the job are stored. To explore the workspace:

- Go to the job’s dashboard and click on the `Workspace` link.

Initially, you might find the workspace empty. To create a file within the workspace:

- Go back to the job’s configuration.
- Add a shell command to create a text file, such as `touch hello.txt`.

![Create File in Workspace](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-6.png)

After building the job again, navigate to the workspace. You should now see the newly created `hello.txt` file.

![File in Workspace](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-7.png)

### Command-Line Access to Workspace

If you're running Jenkins in a Docker container, you can also access the workspace via the command line:

**1. Exec into the Docker container:**

```bash
docker exec -it <container_name_or_id> /bin/bash
```

**2. Navigate to the workspace directory:**

```bash
cd /var/lib/jenkins/workspace/your_job_name
```

Here, you can see and manipulate the files related to the job directly.

![CLI Workspace Access](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-8.png)

## Task 03: Running a Script File in the Job

To run a script file within a Jenkins job:

**1. Create a script file (e.g., `demo.sh`) in the workspace or another directory.**
**2. Configure the job to execute this script by adding the following shell command:**

```bash
bash <path_to_your_bash_file>/demo.sh
```

![Run Script in Job](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-13.png)

After building the job, check the `Console Output` to ensure the script executed successfully.

![Script Execution Output](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-14.png)

## Task 04: Parameterizing a Job

Jenkins allows you to pass parameters to jobs, making them more flexible. To configure a job with parameters:

1. Go to the job's configuration page.
2. Check the `This project is parameterized` option.
3. Choose the type of parameter you want (e.g., `String Parameter`).
4. Name the parameter and provide a default value.

![Add Parameter to Job](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-16.png)

You can then use the parameter in your shell command, like so:

```bash
echo "The parameter value is: $(parameter_name)"
```

![Use Parameter in Command](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-18.png)

When you build the job, you’ll be prompted to enter a value for the parameter.

![Parameter Input](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-19.png)

## Task 05: Running the Job Periodically

To automate job execution, you can configure Jenkins to run jobs at specified intervals, similar to a cron job:

1. In the job's configuration, navigate to the `Build Triggers` section.
2. Select the `Build periodically` option.
3. Define the schedule using cron syntax. For example, `* * * * *` will run the job every minute.

![Configure Periodic Build](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-10.png)

Jenkins will automatically trigger the build at the specified intervals, and you can monitor this in the `Build History` section.

![Periodic Build History](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Jenkins%20Labs/Lab%2002/images/image-15.png)

## Conclusion

Creating and managing jobs in Jenkins is straightforward and powerful, allowing you to automate a wide range of tasks with ease. In this guide, you've learned how to create a basic Jenkins job, explore its workspace, run script files, use parameters, and schedule jobs to run periodically.