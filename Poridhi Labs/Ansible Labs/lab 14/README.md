# Automating MySQL Installation on an EC2 Instance Using Ansible and GitHub Actions

This guide provides a detailed step-by-step approach to automating the installation and configuration of MySQL on an Amazon EC2 instance using Ansible and GitHub Actions.  The process involves writing an Ansible playbook to handle the installation and configuration tasks and creating a GitHub Actions workflow to execute the playbook whenever changes are pushed to the main branch or manually triggered.

![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql-Github-Actions/images/ansible-diagram.png)

## Prerequisites

1. **EC2 Instance:**
   - An Ubuntu-based EC2 instance running on AWS.
   - Security group allowing inbound SSH traffic from your IP address.

2. **GitHub Repository:**
   - A GitHub repository to store your Ansible playbook and workflow files.
   - GitHub Secrets configured to store your SSH public key and public IP address.

## Steps

### Step 1: Set up Your EC2 Instance

Ensure you have an EC2 instance running and accessible via SSH. Make sure the security group associated with your instance allows inbound SSH traffic from your IP address.

### Step 2: Create Ansible Playbook and Inventory File

1. **Create a directory for your Ansible project:**

    ```bash
    mkdir ansible-mysql
    cd ansible-mysql
    ```

2. **Create an inventory file named `hosts.ini`:**

    ```ini
    [mysql_servers]
    ec2-instance ansible_host={{ EC2_PUBLIC_IP }} ansible_user=ubuntu ansible_ssh_private_key_file={{ SSH_PRIVATE_KEY_PATH }}
    ```

    Store `{{ EC2_PUBLIC_IP }}` with the public IP address of your EC2 instance and `{{ SSH_PRIVATE_KEY_PATH }}` with your SSH private key file in the github repository secrets.

3. **Create a playbook file named `install_mysql.yml`:**

    ```yaml
    ---
    - name: Install and configure MySQL on EC2 instance
      hosts: mysql_servers
      become: yes
      vars:
        mysql_root_password: 'your_new_password_here'

      tasks:
        - name: Update apt cache
          apt:
            update_cache: yes

        - name: Install MySQL server and Python MySQL library
          apt:
            name: "{{ item }}"
            state: present
          loop:
            - mysql-server  # MySQL Server
            - python3-mysqldb  # MySQL Python library for Python 3.x

        - name: Start and enable MySQL service
          service:
            name: mysql
            state: started
            enabled: yes

        - name: Check if MySQL root password is already set
          shell: >
            mysql -u root -p'{{ mysql_root_password }}' -e "SELECT 1" > /dev/null 2>&1
          ignore_errors: yes
          register: mysql_root_password_check

        - name: Set MySQL root password if not set
          mysql_user:
            login_user: root
            login_password: ''
            name: root
            host_all: yes
            password: "{{ mysql_root_password }}"
          when: mysql_root_password_check.failed

        - name: Ensure MySQL root password is set
          mysql_user:
            login_user: root
            login_password: "{{ mysql_root_password }}"
            name: root
            host_all: yes
            password: "{{ mysql_root_password }}"
          when: not mysql_root_password_check.failed

        - name: Remove anonymous users
          mysql_user:
            name: ''
            host_all: yes
            state: absent
            login_user: root
            login_password: "{{ mysql_root_password }}"

        - name: Disallow root login remotely
          mysql_user:
            name: root
            host: "{{ item }}"
            state: absent
            login_user: root
            login_password: "{{ mysql_root_password }}"
          loop:
            - "{{ ansible_hostname }}"
            - '127.0.0.1'
            - '::1'

        - name: Remove test database and access to it
          mysql_db:
            name: test
            state: absent
            login_user: root
            login_password: "{{ mysql_root_password }}"

        - name: Reload privilege tables
          mysql_query:
            query: "FLUSH PRIVILEGES;"
            login_user: root
            login_password: "{{ mysql_root_password }}"
    ```

    Replace `"your_new_password_here"` with a secure password of your choice.

### Step 3: Create a GitHub Actions Workflow File

1. **Create a directory named `.github/workflows` in the root of your repository:**

    ```bash
    mkdir -p .github/workflows
    ```

2. **Inside this directory, create a file named `ansible-mysql.yml`:**

    ```yaml
    name: Deploy MySQL using Ansible

    on:
      push:
        branches:
          - main
      workflow_dispatch:

    jobs:
      deploy:
        runs-on: ubuntu-latest

        steps:
        - name: Checkout repository
          uses: actions/checkout@v2

        - name: Set up Python
          uses: actions/setup-python@v2
          with:
            python-version: '3.x'

        - name: Install Ansible
          run: |
            sudo apt update
            sudo apt install ansible -y

        - name: Set up SSH Key and known_hosts
          env:
            SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
            EC2_PUBLIC_IP: ${{ secrets.EC2_PUBLIC_IP }}
          run: |
            mkdir -p ~/.ssh
            echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
            chmod 600 ~/.ssh/id_rsa
            ssh-keyscan -H $EC2_PUBLIC_IP >> ~/.ssh/known_hosts

        - name: Replace placeholders in inventory file
          run: |
            sed -i "s/{{ EC2_PUBLIC_IP }}/${{ secrets.EC2_PUBLIC_IP }}/g" <Path-to-your-host-files>/hosts.ini
            sed -i "s|{{ SSH_PRIVATE_KEY_PATH }}|~/.ssh/id_rsa|g" <Path-to-your-host-files>/hosts.ini

        - name: Run Ansible Playbook
          run: |
            ansible-playbook -i <Path-to-your-host-files>/hosts.ini <Path-to-your-playbook>/install_mysql.yml
    ```

    Replace the `<Path-to-your-host-files>` and `<Path-to-your-playbook>` with the direcrtory path of your files.

### Step 4: Store the SSH Key as a GitHub Secret

1. **Go to your repository on GitHub.**
2. **Navigate to Settings > Secrets and variables > Actions.**
3. **Click on "New repository secret".**
4. **Add the following secrets:**

   - **Name:** `SSH_PRIVATE_KEY`

     **Value:** Paste the content of your SSH private key.
   - **Name:** `EC2_PUBLIC_IP`
   
     **Value:** The public IP address of your EC2 instance.


     ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql-Github-Actions/images/mysql-actions-01.png)

### Step 5: Push the code to Github

1. **Initialize a Git Repository:**
   - If you haven't already, initialize a Git repository in your project directory:

     ```bash
     git init
     ```

2. **Add Your Remote Repository:**
   - Add your GitHub repository as a remote:

     ```bash
     git remote add origin https://github.com/your-username/your-repo-name.git
     ```

3. **Add Your Files:**
   - Add all the files using:

     ```bash
     git add .
     ```

4. **Commit the Staged Files:**
   - Create a commit with a descriptive message:

     ```bash
     git commit -m "Add Ansible playbook"
     ```

5. **Push Your Changes:**
   - Push the commit to the main branch of your GitHub repository:

     ```bash
     git push -u origin main
     ```


### Step 6: Run the Workflow

- **Push to Main Branch:** Whenever you push changes to the main branch, the workflow will execute and run the Ansible playbook.
- **Manual Trigger:** You can also manually trigger this workflow from the GitHub Actions tab in your repository.

## Verification

Ensure the Ansible playbook (`install_mysql.yml`) and the GitHub Actions workflow (`ansible-mysql.yml`) are committed and pushed to the main branch of your repository. This will trigger the GitHub Actions workflow to run the Ansible playbook on your EC2 instance.

1. **Check the Workflow Execution:**
   - Go to the "Actions" tab in your GitHub repository.
   - Monitor the workflow run to ensure it completes successfully without errors.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql-Github-Actions/images/mysql-actions-02.png)

2. **Connect to the EC2 instance:**

    ```bash
    ssh -i /path/to/your-key.pem ubuntu@<EC2_PUBLIC_IP>
    ```

3. **Verify MySQL is running:**

    ```bash
    sudo systemctl status mysql
    ```

    The output should indicate that MySQL is active and running.

    ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql-Github-Actions/images/mysql-actions-03.png)

3. **Log in to the MySQL shell:**

    ```bash
    mysql -u root -p
    ```

    Enter the root password set in the Ansible playbook.

4. **Check the MySQL version:**

    ```sql
    SELECT VERSION();
    ```

    This will display the version of MySQL that is installed.

    ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql-Github-Actions/images/mysql-actions-04.png)

## Verification Steps for Checking Idempotency with Table Creation

1. **Create a Table in MySQL:**

     - Create a test database and table:

        ```sql
        CREATE DATABASE test_db;
        USE test_db;
        CREATE TABLE test_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        ``` 


   - Insert some data into the table:

     ```sql
     INSERT INTO test_table (name) VALUES ('test1'), ('test2');
     ```

   - Verify the data in the table:

     ```sql
     SELECT * FROM test_table;
     ```

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql-Github-Actions/images/mysql-actions-05.png)

2. **Trigger the Workflow Again:**
   - Manually trigger the workflow from the "Actions" tab by selecting the workflow and clicking "Run workflow".
   - Alternatively, make a small change (e.g., update the README file) and push it to the main branch to trigger the workflow again.

3. **Check the Second Workflow Execution:**
   - Go to the "Actions" tab in your GitHub repository.
   - Monitor the workflow run to ensure it completes successfully without errors.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql-Github-Actions/images/mysql-actions-06.png)

4. **Verify Idempotency and Table Integrity:**
   - Connect to your EC2 instance via SSH:

     ```bash
     ssh -i /path/to/your-key.pem ubuntu@<EC2_PUBLIC_IP>
     ```

   - Check the status of the MySQL service again:

     ```bash
     sudo systemctl status mysql
     ```

     Ensure the service is still active and running, with no changes or restarts triggered by the second playbook run.

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql-Github-Actions/images/mysql-actions-07.png)

   - Log in to the MySQL shell again:

     ```bash
     mysql -u root -p
     ```

   - Use the test database and verify the table data:

     ```sql
     USE test_db;
     SELECT * FROM test_table;
     ```

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql-Github-Actions/images/mysql-actions-08.png)

If the table and its data remain unchanged after both runs of the playbook, it indicates that the playbook is idempotent. The second run should not alter the existing table or data, confirming that the playbook only makes necessary changes and leaves the system state unchanged when rerun.

## Conclusion

By following the steps outlined in this guide, we have successfully automated the installation and configuration of MySQL on an Amazon EC2 instance using Ansible and GitHub Actions. The process involved creating an Ansible playbook to handle the installation and configuration tasks and setting up a GitHub Actions workflow to execute the playbook whenever changes are pushed to the main branch or manually triggered. The idempotency of the Ansible playbook further enhances the robustness of the solution, making it suitable for repeated and large-scale deployments.