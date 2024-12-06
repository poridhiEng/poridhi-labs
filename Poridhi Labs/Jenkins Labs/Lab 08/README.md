# Ensuring Jenkins Data and Configuration Integrity on AWS EC2

Backing up Jenkins data and configurations is essential for maintaining the continuity and reliability of your CI/CD pipeline, especially when Jenkins is deployed on an AWS EC2 instance. Jenkins stores its configurations, job settings, build logs, and plugins in the Jenkins home directory. Regular backups help mitigate risks during Jenkins upgrades, plugin updates, and other maintenance activities. This guide outlines the steps for installing Jenkins on an AWS EC2 instance, backing up Jenkins data and configurations using the ThinBackup plugin, creating a sample test job, and restoring it after deletion.

## Step 1: Setup an EC2 Instance on AWS

- Set up an Ubuntu EC2 instance with a security group allowing inbound traffic on ports 8080 and 22 (for SSH).

## Step 2: Install Jenkins on EC2 instance

- Ensure your jenkins server is up and running in the ec2 instance. If you do not have one, follow this lab: [Jenkins Installation on Ubuntu](https://github.com/AhnafNabil/Jenkins-Labs/tree/main/Lab%2001)

## Step 3: Install ThinBackup Plugin

1. **Navigate to Plugin Management**:
   - Go to **Manage Jenkins** → **Manage Plugins**.

2. **Install ThinBackup Plugin**:
   - Under the **Available** tab, search for "ThinBackup".
   - Install the plugin and restart Jenkins if prompted.

## Step 3: Configure ThinBackup Plugin

1. **Access ThinBackup Settings**:
   - Go to **Manage Jenkins** → **ThinBackup** → **Settings**.

2. **Configure Backup Settings**:
   - **Backup Directory**: Specify a writable directory where backups will be stored, such as `/var/jenkins_backups`.
     ```bash
     sudo mkdir /var/jenkins_backups
     sudo chown jenkins:jenkins /var/jenkins_backups
     ```
   - **Backup Schedule**: Configure the schedule for automatic backups (e.g., daily at midnight).
   - **Backup Retention**: Define how many backups to keep.
   - **Backup Types**: Choose between full or differential backups based on your requirements.

3. **Save the Configuration**.

## Step 4: Create a Sample Test Job

1. **Create a New Job**:
   - Go to the Jenkins dashboard and click **New Item**.
   - Name the job "Test-Job", select **Freestyle project**, and click **OK**.
   - Configure the job as needed and save it.

2. **Run the Job**:
   - Click **Build Now** to run the job and generate some build history.

## Step 5: Backup Jenkins Data

1. **Manual Backup**:
   - Navigate to **Manage Jenkins** → **ThinBackup** → **Backup Now**.
   - Verify that a backup is created in the specified backup directory. Each backup will have a timestamp attached to the folder name.

## Step 6: Delete the Sample Test Job

1. **Delete the Job**:
   - Go to the Jenkins dashboard, click on the "Test-Job", and choose **Delete Project**.
   - Confirm the deletion.

## Step 7: Restore Jenkins Data

1. **Restore from Backup**:
   - Navigate to **Manage Jenkins** → **ThinBackup** → **Restore**.
   - Select the backup you wish to restore from and click **Restore**.
   - Jenkins will restore the job, configurations, and any other data from the selected backup.

2. **Verify Restoration**:
   - Check that the "Test-Job" is restored with its configuration and build history intact.

## Conclusion

Backing up and restoring Jenkins data and configurations on an AWS EC2 instance is vital for ensuring business continuity and minimizing downtime. The ThinBackup plugin provides an efficient way to manage backups, making it easy to recover from accidental deletions, updates, or other disruptions. Regularly test your backup and restore process to ensure the integrity and reliability of your Jenkins environment.