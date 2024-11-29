# Creating and Managing Your First Jenkins Job

In this tutorial, we'll walk you through creating, configuring, and running your first Jenkins job. We'll also explore how to manage the job workspace, run script files, pass parameters to jobs, and schedule jobs to run periodically.

## Prerequisites

Before starting, ensure that:
- Jenkins is installed and running on your server.
- You can access the Jenkins dashboard via a web browser.

## Task 01: Create Your First Jenkins Job

### Step 1: Log in to Jenkins

To start, access your Jenkins server using a web browser by navigating to the following URL:

```plaintext
http://localhost:8080
```

Log in with the appropriate credentials. Once logged in, you'll be greeted with the Jenkins dashboard, the central hub where you can manage all your Jenkins jobs and configurations.

![Jenkins Dashboard](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image.png)

### Step 2: Create a New Job

To create your first job:

1. Click on the `New Item` option on the Jenkins dashboard.
2. Enter a name for your job, such as `first-job`.
3. Select `Freestyle project` as the job type. This is the most basic type of Jenkins job, suitable for running simple tasks.

![Create New Job](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-1.png)

### Step 3: Configure Your Job

Once the job is created, you’ll be directed to the configuration page. Here’s how to set it up:

1. Scroll down to the `Build` section.
2. Click on `Add build step` and select `Execute shell` from the dropdown.
3. Enter a simple shell command, such as `echo "Hello, World!"`.
4. Save the configuration.

![Configure Job](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-2.png)

### Step 4: Build the Job

To run your job:

1. Navigate to your job’s dashboard.
2. Click the `Build Now` button to execute the job.

![Build Job](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-3.png)

After the build completes, you can view the output by clicking on the `Console Output` link. Here, you'll see details about the job execution, including the shell command output, the user who triggered the job, and the job’s workspace.

![Console Output](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-5.png)

Congratulations! You’ve successfully created and built your first Jenkins job.

## Task 02: Explore the Job Workspace

Each Jenkins job has a dedicated workspace where files related to the job are stored. To explore the workspace:

1. Go to the job’s dashboard and click on the `Workspace` link.

Initially, you might find the workspace empty. To create a file within the workspace:

1. Go back to the job’s configuration.
2. Add a shell command to create a text file, such as `touch hello.txt`.

![Create File in Workspace](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-6.png)

After building the job again, navigate to the workspace. You should now see the newly created `hello.txt` file.

![File in Workspace](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-7.png)

### Command-Line Access to Workspace

If you're running Jenkins in a Docker container, you can also access the workspace via the command line:

1. Exec into the Docker container:

   ```bash
   docker exec -it <container_name_or_id> /bin/bash
   ```

2. Navigate to the workspace directory:

   ```bash
   cd /var/lib/jenkins/workspace/your_job_name
   ```

Here, you can see and manipulate the files related to the job directly.

![CLI Workspace Access](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-8.png)

## Task 03: Running a Script File in the Job

To run a script file within a Jenkins job:

1. Create a script file (e.g., `demo.sh`) in the workspace or another directory.
2. Configure the job to execute this script by adding the following shell command:

   ```bash
   bash <path_to_your_bash_file>/demo.sh
   ```

![Run Script in Job](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-13.png)

After building the job, check the `Console Output` to ensure the script executed successfully.

![Script Execution Output](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-14.png)

## Task 04: Parameterizing a Job

Jenkins allows you to pass parameters to jobs, making them more flexible. To configure a job with parameters:

1. Go to the job's configuration page.
2. Check the `This project is parameterized` option.
3. Choose the type of parameter you want (e.g., `String Parameter`).
4. Name the parameter and provide a default value.

![Add Parameter to Job](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-16.png)

You can then use the parameter in your shell command, like so:

```bash
echo "The parameter value is: $(parameter_name)"
```

![Use Parameter in Command](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-18.png)

When you build the job, you’ll be prompted to enter a value for the parameter.

![Parameter Input](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-19.png)

## Task 05: Running the Job Periodically

To automate job execution, you can configure Jenkins to run jobs at specified intervals, similar to a cron job:

1. In the job's configuration, navigate to the `Build Triggers` section.
2. Select the `Build periodically` option.
3. Define the schedule using cron syntax. For example, `* * * * *` will run the job every minute.

![Configure Periodic Build](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-10.png)

Jenkins will automatically trigger the build at the specified intervals, and you can monitor this in the `Build History` section.

![Periodic Build History](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2002/images/image-15.png)

## Conclusion

Creating and managing jobs in Jenkins is straightforward and powerful, allowing you to automate a wide range of tasks with ease. In this guide, you've learned how to create a basic Jenkins job, explore its workspace, run script files, use parameters, and schedule jobs to run periodically. With these foundational skills, you can start leveraging Jenkins to streamline your development and deployment processes.