# Automating Nginx Website Deployment with Ansible

In this lab, we will demonstrate how to automate the deployment of two different static websites to two remote servers using Ansible. `Ansible` is an open-source automation tool that allows you to manage configurations, deploy applications, and orchestrate complex tasks.

We will walk through the process of setting up an Ansible playbook to:
1. Install `Nginx`, a popular web server, on two remote servers.
2. Deploy two different `websites` to these servers.
3. Ensure that the `Nginx service` is restarted whenever there is a change in the website content.

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2006/images/image-6.png)

To achieve this, we will:
- Define our target servers in an `inventory` file.
- Use a `variables` file to specify the paths to our website files and their destinations on the remote servers.
- Create a playbook that includes tasks for installing Nginx, copying the website files, and handling the service restart.

By the end of this, we will have a fully automated solution for deploying and managing our web server configurations, making our development and deployment processes more efficient and reliable.

## Prerequisites

1. **Ansible Installed on Control Node**: Ensure that Ansible is installed on your control node.
2. **Remote servers**: Ensure you have created the remote servers where you want to deploy the websites. Here we have used aws ec2 instance.

  ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2006/images/image.png)

2. **SSH Access**: Ensure that the control node can SSH into the remote servers using a key pair.

## Directory Structure

```sh
.
├── ansible
│   ├── ansible.cfg
│   ├── deploy_nginx_websites.yml
│   ├── hosts.ini
│   └── vars
│       └── websites.yml
├── webpage1
│   └── index.html
├── webpage2
    └── index.html
```

## Step by step guide

### Step 1: Create an Inventory File in the `ansible` directory(`ansible/hosts.ini`)

```ini
[webservers]
webserver1 ansible_host=<remote_server_ip>
webserver2 ansible_host=<remote_server_ip>
```

### Step 2: Create a Variable File to store the website files src and destination info(`ansible/vars/websites.yml`)

```yaml
websites:
  - name: webserver1
    src:  /home/user_name/path/to/webpage1/index.html
    dest: /var/www/html/index.html
  - name: webserver2
    src:  /home/user_name/path/to/webpage2/index.html
    dest: /var/www/html/index.html
```

*NOTE:* Make sure the change the src directory according to your file structure.

### Step 3: Create the ansible playbook that will install the nginx and hosts the webservers (`ansible/deploy_nginx_websites.yml`)

```yaml
---
- name: Deploy two different websites on Nginx
  hosts: webservers
  become: yes
  vars_files:
    - vars/websites.yml
  tasks:
    - name: Ensure Nginx is installed
      apt:
        name: nginx
        state: present
      tags: nginx

    - name: Copy website files
      copy:
        src: "{{ item.src }}"
        dest: "{{ item.dest }}"
      when: inventory_hostname == item.name
      with_items: "{{ websites }}"
      notify: restart nginx

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

### Step 4: Create an Ansible Configuration File (`ansible/ansible.cfg`)

- Create an `ansible.cfg` file to define configuration settings for your Ansible environment:

  ```sh
  nano ansible.cfg
  ```

- Add the following content to the configuration file:

  ```ini
  [defaults]
  inventory = inventory
  remote_user = ubuntu
  private_key_file = <path_to_your_key_file>
  host_key_checking = False
  ```

### Explanation

- `inventory`: Specifies the path to the inventory file.
- `remote_user`: The username for SSH connections.
- `private_key_file`: The path to the SSH private key file.
- `host_key_checking`: Disables host key checking for convenience.

### Step 5: Website Content

Ensure you have your HTML files with the embedded CSS:

**Webpage 1 (`webpage1/index.html`):**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Website 1</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            color: #333;
            text-align: center;
            padding: 50px;
        }
        h1 {
            color: #007BFF;
        }
    </style>
</head>
<body>
    <h1>Welcome to Website 1</h1>
    <p>This is a simple website hosted on webserver1.</p>
</body>
</html>
```

**Webpage 2 (`webpage2/index.html`):**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Website 2</title>
    <style>
        body {
            font-family: 'Trebuchet MS', sans-serif;
            background-color: #e0f7fa;
            color: #333;
            text-align: center;
            padding: 50px;
        }
        h1 {
            color: #00796B;
        }
    </style>
</head>
<body>
    <h1>Welcome to Website 2</h1>
    <p>This is a simple website hosted on webserver2.</p>
</body>
</html>
```

### Step 5: Run the Playbook

- Before running the playbook you can check if ansible can ssh into the remote servers. We can simply run this command to ping all the hosts:

  ```sh
  ansible webservers -m ping
  ```
If you get a response like this, then you are good to go:

  ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2006/images/image-1.png)

- Navigate to the `ansible` directory and execute the playbook using the following command:

  ```bash
  cd ansible
  ansible-playbook -i hosts.ini deploy_nginx_websites.yml
  ```

This command will execute the playbook and deploy the two websites on the remote servers. Check any error while running the playbook. If everything is alright, you will get output something like this:

  ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2006/images/image-2.png)

### Verification

To verify our task, we can check step by step

- First ssh into the remote servers and check the status of the nginx

  ```sh
  systemctl status nginx
  ```

  ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2006/images/image-3.png)

  Here we can see the nginx is running perfectly.

- We can check if the `index.html` file is copied to the remote servers:

  ```sh
  ls /var/www/html
  ```
  ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2006/images/image-4.png)

- Now check if the website is running successfully:

  Open your browser and navigate to the IP address of the remote server(if your remote instance is publicly accessible. Modify the inbound rules accordingly). You should see the website

  ```sh
  http://<remote_server_1_ip>
  http://<remote_server_2_ip>
  ```

  ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2006/images/image-5.png)

  Here, we can see our website are deployed and running successfully. 
---

## Conclusion
In this guide, we successfully automated the deployment of two different static websites to two remote servers using `Ansible`. By leveraging Ansible's powerful automation capabilities, we streamlined the process of setting up `Nginx`, copying website files, and managing service restarts, ensuring a consistent and efficient deployment workflow.
