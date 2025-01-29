# Installing MySQL on an EC2 Instance Using Ansible

## Overview

This documentation provides a comprehensive guide to installing and configuring MySQL on an Amazon EC2 instance using Ansible. The process involves setting up an EC2 instance, installing Ansible on your local machine, writing an Ansible playbook, executing it to ensure MySQL is installed and secured, and verifying the installation.

![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql/images/diagram-mysql-ansible.png)

## Prerequisites

1. **EC2 Instance:**
   - An Ubuntu-based EC2 instance running on AWS.
   - Security group allowing inbound SSH traffic from your IP address.

2. **Local Machine:**
   - Ansible installed on your local machine.
   - SSH access to the EC2 instance using a key pair.
   - Python and necessary libraries installed.

## Steps

### Step 1: Set up Your EC2 Instance

Ensure you have an EC2 instance running and accessible via SSH. Make sure the security group associated with your instance allows inbound SSH traffic from your IP address.

### Step 2: Install Ansible

If Ansible is not already installed on your local machine, you can install it using `pip`:

```bash
sudo apt update
sudo apt install ansible
```

Verify the installation by checking the Ansible version:

```bash
ansible --version
```

### Step 3: Create an Ansible Playbook

Create a directory for your Ansible project:

```bash
mkdir ansible-mysql
cd ansible-mysql
```

Create an inventory file named `hosts.ini` to specify your EC2 instance details:

```ini
[mysql_servers]
ec2-instance ansible_host=<EC2_PUBLIC_IP> ansible_user=ubuntu ansible_ssh_private_key_file=/path/to/your-key.pem
```

Replace `<EC2_PUBLIC_IP>` with the public IP address of your EC2 instance and `/path/to/your-key.pem` with the path to your SSH private key file.

Create a playbook file named `install_mysql.yml`:

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

### Step 4: Run the Ansible Playbook

Change the permissions of your private key file:

```bash
chmod 600 /path/to/your-key.pem
```

Run the playbook using the following command:

```bash
ansible-playbook -i hosts.ini install_mysql.yml
```

This command will connect to your EC2 instance and perform the steps defined in the playbook to install and configure MySQL.

![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql/images/ansible-01.png)

### Step 5: Verify the Installation

1. **Connect to the EC2 instance:**

   ```bash
   ssh -i /path/to/your-key.pem ubuntu@<EC2_PUBLIC_IP>
   ```

2. **Verify MySQL is running:**

   Check the status of the MySQL service:

   ```bash
   sudo systemctl status mysql
   ```

   The output should indicate that MySQL is active and running.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql/images/ansible-02.png)

3. **Log in to the MySQL shell:**

    Try logging in to the MySQL shell using the root user and the password you set in the Ansible playbook:

    ```bash
    mysql -u root -p
    ```

    You will be prompted to enter the root password. If MySQL is installed correctly, you should be able to log in and see the MySQL prompt:

    ```bash
    mysql>
    ```
  
4. **Check the MySQL version:**

   While in the MySQL shell, you can check the installed MySQL version with the following command:

   ```sql
   SELECT VERSION();
   ```

   This will display the version of MySQL that is installed.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/Ansible-Labs/main/Ansible-Mysql/images/ansible-03.png)


## Additional Tips

- **Security Group:** Ensure the security group associated with your EC2 instance allows inbound SSH traffic from your IP address.
- **Permissions:** Keep the permissions of your private key secure (`chmod 600 /path/to/your-key.pem`).

## Conclusion

By following these steps, you will successfully install and configure MySQL on your EC2 instance using Ansible. This process included setting up your EC2 instance, preparing your local machine with Ansible, creating a detailed Ansible playbook, and executing it to ensure MySQL is installed and properly secured.