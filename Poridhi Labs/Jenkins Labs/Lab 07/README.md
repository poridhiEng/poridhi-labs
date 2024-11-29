# Build a Java application with Maven using Jenkins Agent node

This guide demonstrates how to use Jenkins to build a Java application with Maven. For this tutorial, we are using the Jenkins agents for handling build jobs. Additionally, we will use a Freestyle project for this setup. In future configurations, we will explore using pipeline projects.

The lab covers the following tasks:

1. Create a Jenkins job to build and test a Java application using Maven.
2. Run the Jenkins job on `agent node` to build and test the Java application.
3. View the build results in Jenkins.
4. Configure the job to deploy the JAR file locally.
5. Visualize the build results graphically.

The example Java application used is from the GitHub repository [simple-java-maven-app](https://github.com/Konami33/simple-java-maven-app). It outputs "Hello world!" and includes unit tests. The test results are saved in a **JUnit XML report**, which will be used for visualization.

Here is the graphical representation of what we will do in this lab.

![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-11.png)

## Prerequisites

1. Ensure your Jenkins server is up and running.
2. Ensure Jenkins agent node connected to the controller and online.
![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-10.png)
3. Java is installed in the Agent node. Check it by running `java --version`. Make sure to have the same version of java both in Jenkins controller node and agent node.
![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image.png)


## Step-by-Step Guide

### Step 1: Install Necessary Plugins and Tools

1. **Install the Maven Integration Plugin:**
   - Go to **Manage Jenkins** -> **Manage Plugins**.
   - In the **Available** tab, search for `Maven Integration (Build Tools)`.
   - Install this plugin.

   ![Install Maven Integration Plugin](https://github.com/Konami33/Jenkins-Labs/blob/main/Lab%2006/images/image-4.png?raw=true)

2. **Configure Maven Installation:**
   - Go to **Manage Jenkins** -> **Global Tool Configuration**.
   - Scroll down to the **Maven** section.
   - Add a new Maven installation:
     - Give it a name, e.g., `Maven-jenkins`.
     - Select the required version and save.

   ![Configure Maven Installation](https://github.com/Konami33/Jenkins-Labs/blob/main/Lab%2006/images/image-5.png?raw=true)

### Step 2: Create a Jenkins Job

1. Log in to your Jenkins server and click on **New Item**.
2. Enter a name for your job, e.g., "Simple Java Maven App", and select **Freestyle project**.
3. Click **OK** to create the job.

![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-1.png)

4. Mark `Restrict where this project can be run` and add the Label of your agent node.

![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-2.png)

5. In the **Source Code Management** section, select **Git** and enter the URL of the GitHub repository:

   ```sh
   https://github.com/Konami33/simple-java-maven-app
   ```

![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-3.png)

5. Save the configuration and build the job. This will clone the repository from GitHub.

![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-4.png)

### Step 3: Configure the Build Step

1. Go to the **Configure** section of the job.
2. In the **Build** section, click **Add build step** and select **Invoke top-level Maven targets**.

   ![Add Build Step](https://github.com/Konami33/Jenkins-Labs/blob/main/Lab%2006/images/image-6.png?raw=true)

3. Select your `Maven Version`.

4. In the **Goals** field, enter the following command to clean, package, and skip tests:

   ```sh
   -B -DskipTests clean package
   ```

   ![Configure Maven Goals](https://github.com/Konami33/Jenkins-Labs/blob/main/Lab%2006/images/image-7.png?raw=true)

### Step 4: Configure the Test Step

1. Go to the **Configure** section of the job.
2. In the **Build** section, click **Add build step** and select **Invoke top-level Maven targets**.
3. Select your `Maven Version`.
4. In the **Goals** field, enter the following command to run tests:

   ```sh
   test
   ```

   ![Configure Test Goals](https://github.com/Konami33/Jenkins-Labs/blob/main/Lab%2006/images/image-9.png?raw=true)


### Step 5: Deploy the JAR File

1. Go to the **Configure** section of the job.
2. In the **Build** section, click **Add build step** and select **Execute shell**.
3. In the **Command** field, enter the command to run the JAR file:

   ```sh
   java -jar <path_to_your_jar_file>
   ```

   Replace `<path_to_your_jar_file>` with the path to your JAR file, typically found in `/var/jenkins_home/workspace/your_job_name/target/`.

   ![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-5.png)

### Step 6: Build the job

1. Build the job and check the output console for any error.

- build step:
![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-6.png)
- test step:
![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-7.png)
- deploy step:
![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-8.png)

### Step 6: Visualize the Build Results

1. In the **Workspace** directory of the job, navigate to:

   **Workspace** -> **YOUR_JOB_NAME** -> **target** -> **surefire-reports**. Locate the XML file containing the build information.

2. Return to the job configuration and scroll down to **Post-build Actions**. Click **Add post-build action** and select **Publish JUnit test result report**.

   ![Add Post-build Action](https://github.com/Konami33/Jenkins-Labs/blob/main/Lab%2006/images/image-15.png?raw=true)

3. In the **Test report XMLs** field, enter the path to the XML files:

   ```sh
   target/surefire-reports/*.xml
   ```

   ![Configure Test Result Report](https://github.com/Konami33/Jenkins-Labs/blob/main/Lab%2006/images/image-16.png?raw=true)

4. Save the configuration and build the job. This will publish the test results on the Jenkins dashboard with graphical representations such as graphs and charts.

   ![alt text](https://github.com/Konami33/Jenkins-Labs/raw/main/Lab%2007/images/image-9.png)

---

## Conclusion

You have successfully set up Jenkins to build, test, deploy, and visualize the results of a Java application using Maven. 