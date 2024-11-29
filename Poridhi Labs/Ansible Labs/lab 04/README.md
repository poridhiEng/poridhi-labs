# Installing Docker Using Ansible

In this lab, we will walk through the process of installing `Docker and related packages` on remote servers using Ansible.

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2004/images/image-6.png)


## Prerequisites

1. **Ansible Installed on Control Node**: Ensure that Ansible is installed on your control node. Here we are using the Poridhi vs-code ubuntu terminal as the control node.
2. **SSH Access**: Ensure that the control node can SSH into the remote servers using a key pair.

## Step by step guide

## Step 1: Create an Inventory File

- Create a directory for your Ansible project and navigate into it.

  ```sh
  mkdir ansible
  cd ansible
  ```

- Create a file named `inventory` and add the IP addresses or hostnames of your remote servers in the `inventory` file:

  ```ini
  <remote_server_1_IP>
  <remote_server_2_IP>
  ```

## Step 2: Create an Ansible Playbook for the installing of Docker
- Create a directory named `playbooks` and then create a playbook named `install_docker.yml`:

  ```sh
  mkdir playbooks
  nano install_nginx.yml
  ```

- Add the following content to the playbook file:

```yml
---
- name: Install Docker on Ubuntu
  hosts: all
  become: true
  vars:
    arch_mapping:
      x86_64: amd64
      aarch64: arm64

  tasks:
    - name: Update and upgrade all packages to the latest version
      ansible.builtin.apt:
        update_cache: true
        upgrade: dist
        cache_valid_time: 3600

    - name: Install required packages
      ansible.builtin.apt:
        pkg:
          - apt-transport-https
          - ca-certificates
          - curl
          - gnupg
          - software-properties-common

    - name: Create directory for Docker's GPG key
      ansible.builtin.file:
        path: /etc/apt/keyrings
        state: directory
        mode: '0755'

    - name: Add Docker's official GPG key
      ansible.builtin.shell:
        cmd: curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor --output /etc/apt/keyrings/docker.gpg
        creates: /etc/apt/keyrings/docker.gpg

    - name: Print architecture variables
      ansible.builtin.debug:
        msg: "Architecture: {{ ansible_architecture }}, Codename: {{ ansible_lsb.codename }}"

    - name: Add Docker repository
      ansible.builtin.apt_repository:
        repo: >-
          deb [arch={{ arch_mapping[ansible_architecture] | default(ansible_architecture) }}
          signed-by=/etc/apt/keyrings/docker.gpg]
          https://download.docker.com/linux/ubuntu {{ ansible_lsb.codename }} stable
        filename: docker
        state: present

    - name: Install Docker and related packages
      ansible.builtin.apt:
        name: "{{ item }}"
        state: present
        update_cache: true
      loop:
        - docker-ce
        - docker-ce-cli
        - containerd.io
        - docker-buildx-plugin
        - docker-compose-plugin

    - name: Add Docker group
      ansible.builtin.group:
        name: docker
        state: present

    - name: Add user to Docker group
      ansible.builtin.user:
        name: "{{ ansible_user }}"
        groups: docker
        append: true

    - name: Enable and start Docker services
      ansible.builtin.systemd:
        name: "{{ item }}"
        enabled: true
        state: started
      loop:
        - docker.service
        - containerd.service   
```

### Playbook explanation:

1. **Playbook Initialization**
   - **hosts**: all - Targets all hosts.
   - **become**: true - Runs tasks with elevated privileges.

2. **Update and Upgrade Packages**
   - Updates the package list and upgrades all packages to their latest versions.

3. **Install Required Packages**
   - Installs essential packages for Docker installation (`apt-transport-https`, `ca-certificates`, `curl`, `gnupg`, `software-properties-common`).

4. **Create Directory for Docker's GPG Key**
   - Creates a directory `/etc/apt/keyrings` to store Docker’s GPG key.

5. **Add Docker's Official GPG Key**
   - Downloads and adds Docker’s GPG key to `/etc/apt/keyrings/docker.gpg`.

6. **Print Architecture Variables**
   - Prints system architecture and Ubuntu codename for debugging purposes.

7. **Add Docker Repository**
   - Adds Docker's official APT repository to the system's sources list.

8. **Install Docker and Related Packages**
   - Installs Docker packages (`docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`).

9. **Add Docker Group**
   - Ensures the Docker group is present.

10. **Add User to Docker Group**
    - Adds the current user to the Docker group to allow running Docker commands without `sudo`.

11. **Enable and Start Docker Services**
    - Enables and starts Docker and containerd services.

## Step 3: Create an Ansible Configuration File

- Create an `ansible.cfg` file to define configuration settings for your Ansible environment:

    ```sh
    nano ansible.cfg
    ```

- Add the following content to the configuration file:

    ```ini
    [defaults]
    inventory = inventory
    remote_user = ubuntu
    private_key_file = ~/.ssh/id_rsa
    host_key_checking = False
    ```
### Explanation

- `inventory`: Specifies the path to the inventory file.
- `remote_user`: The username for SSH connections.
- `private_key_file`: The path to the SSH private key file.
- `host_key_checking`: Disables host key checking for convenience.

## Step 4: Run the Playbook

Now run the playbook using this command:

```sh
ansible-playbook -i inventory <path_to_your>/playbook.yml
```
Check the logs if all the tasks are completed successfully or not:

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2004/images/image-3.png)

## Step 5: Verify Docker Installation

After running the playbook, verify that Docker is installed correctly or not.
- First ssh into the remote servers.

```sh
ssh -i <path_to_your_sshkey>/id_rsa ubuntu@<remote_server_ip
```

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2004/images/image-1.png)

- After entering into the remote server, check the docker version:

```sh
docker --version
docker ps
```

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2004/images/image.png)
![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2004/images/image-4.png)


*NOTE: Possible problems:*

After running this command `docker ps`, you might face this problem:

```sh
ubuntu@ip-10-0-1-237:~$ docker ps
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.46/containers/json": dial unix /var/run/docker.sock: connect: permission denied
```

This happens if you have already ssh into the remote servers terminal before running the playbook which will install the docker. Because for the `group membership` changes to take effect, the user needs to `log out` and `log back in`. So to solve, this close this terminal and create a new terminal. It will solve the issue.

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2004/images/image-5.png)

- We can also check by pulling any images from docker hub

```sh
docker pull nginx
docker pull redis
```

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2004/images/image-2.png)

So, we have completed our task of installing Docker and other packages into the remote servers using Ansible playbook. We have created an inventory file to define the remote hosts, wrote a playbook to install and start `Docker`, configured Ansible settings, and ran the playbook to complete the installation. This approach allows for efficient and repeatable deployment of software across multiple servers.