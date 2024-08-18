# Deploying MySQL in a Private Subnet on AWS using Docker Compose

## Overview

In this lab, we will deploy a MySQL server on an EC2 instance within a private subnet. The setup will ensure that the MySQL server is securely configured, protecting its data and operations.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/systemd-diagram.png)

Now, we're tasked with deploying a MySQL server on any EC2 instance within that private subnet. This means we'll need to take careful steps to ensure the MySQL server is securely configured to safeguard its data and operations. Let's dive into deploying the MySQL server in the private subnet.

### Step 1: VPC and Subnet Configuration

1. **Create a VPC**
   - **CIDR:** `10.0.0.0/16`

2. **Create a Private Subnet**
   - **CIDR:** `10.0.1.0/24`
   - **Availability Zone:** `ap-southeast-1a`
   - **Do not enable Auto-assign Public IPv4 Address**

3. **Create a Public Subnet**
   - **CIDR:** `10.0.2.0/24`
   - **Availability Zone:** `ap-southeast-1a`
   - **Enable Auto-assign Public IPv4 Address**

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-01.png)

4. **Create an Internet Gateway (IGW)**
   - Attach the IGW to the VPC.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-02.png)

5. **Create a NAT Gateway**
   - Go to the VPC Dashboard in the AWS Management Console.
   - In the left-hand menu, click on "NAT Gateways".
   - Click "Create NAT Gateway".
   - Select the public subnet (`10.0.2.0/24`).
   - Allocate an Elastic IP for the NAT Gateway.
   - Click "Create a NAT Gateway".

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-03.png)

6. **Create and Configure Route Tables**
   - **Public Route Table:**
     - Add a route with `Destination: 0.0.0.0/0` and `Target: IGW`.
     - Associate the route table with the public subnet.

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-04.png)

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-05.png)

   - **Private Route Table:**
     - Add a route with `Destination: 0.0.0.0/0` and `Target: NAT Gateway ID (select the NAT Gateway created above)`.
     - Associate the route table with the private subnet.

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-06.png)

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-07.png)

7. **Create a Security Group for MySQL**
   - **Inbound Rules:**
     - Type: MySQL/Aurora
     - Protocol: TCP
     - Port: 3306

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-08.png)

   - **Outbound Rules:**
     - Allow all outbound traffic

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-09.png)


## Network Diagram

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-10.png)

### Step 2: Launch and Connect to EC2 Instance

1. **Launch a Bastion Host in the Public Subnet**
   - **AMI:** Ubuntu Server 24.04 LTS
   - **Instance Type:** t2.micro (or as needed)
   - **Network:** Select the VPC and public subnet created earlier
   - **Security Group:** Create or use a security group that allows SSH access (port 22) from your IP.
   - **Key-pair:** Create a key pair named `my-key.pem` and save it securely.

2. **Launch MySQL EC2 Instance in the Private Subnet**
   - **AMI:** Ubuntu Server 24.04 LTS
   - **Instance Type:** t2.micro (or as needed)
   - **Network:** Select the VPC and private subnet created earlier
   - **Security Group:** Select the MySQL security group 
   - **Key-pair:** Select the key pair created earlier

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-11.png)

3. **Connect to the Bastion Host**

   Open a terminal where you saved the key pair and run:

   ```bash
   chmod 400 "my-key.pem"
   ssh -i "my-key.pem" ubuntu@<Public_IP_of_Bastion_Host>
   ```

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-12.png)

4. **Copy the Key Pair to the Public Instance:**
    - On your local machine, run the following command to copy the key pair to the public instance:

      ```sh
      scp -i <My-key.pem> <My-key.pem> ubuntu@<public_instance_ip>:~
      ```

    Replace <public_instance_ip> with the public IP address of the public instance and the <My-key.pem> with the keypair.

    ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-13.png)


5. **Connect to the MySQL Instance from the Bastion Host**

    - After coping the keypair into the public instance, ssh into public instance

      ```sh
      ssh -i "my-key.pem" ubuntu@<Public_IP_of_Bastion_Host>
      ```
    - change the file permissions of the copied key pair:
   
      ```sh
      chmod 400 "my-key.pem"
      ```
    - ssh into the private instance from the public instance:
   
      ```sh
      ssh -i "my-key.pem" ubuntu@<Private_IP_of_MySQL_Instance>
      ```

      ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-14.png)

    - Remember to Replace the <private_instance_ip> with the private IP address of the Mysql instance.

Now, We are currently within the private MySQL instance. Here we will deploy MySQL using docker compose.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-15.png)

3. **Update and Upgrade MySQL Server:**
   ```sh
   sudo apt update
   sudo apt upgrade -y
   ```

### Step 6: Install Docker and Docker Compose

1. **Install Necessary Packages:**
   ```sh
   sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
   ```

2. **Download the GPG key and save it in `/etc/apt/keyrings` directory:**
   ```sh
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg      
   ```

3. **Add the Docker repository to your APT sources list:**
   ```sh
   echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

4. **Update the APT package index and install Docker:**
   ```sh
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```

5. **Install Docker Compose:**
   ```sh
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

6. **Verify Installation:**
   ```sh
   docker-compose --version
   ```

### Step 7: Configure and Deploy MySQL with Docker Compose

1. **Create Docker Compose File:**
   ```sh
   sudo nano docker-compose.yml
   ```

2. **Paste the Following Configuration:**
   ```yaml
   version: '3.8'

   services:
     db:
       image: mysql:latest
       container_name: mysql-db
       restart: always
       environment:
         MYSQL_ROOT_PASSWORD: poridhi_pass
         MYSQL_DATABASE: poridhi
         MYSQL_USER: poridhi_user
         MYSQL_PASSWORD: poridhi_24
       volumes:
         - mysql_data:/var/lib/mysql
       ports:
         - "3306:3306"

   volumes:
     mysql_data:
   ```

3. **Deploy MySQL Container:**
   ```sh
   sudo docker-compose up -d
   ```

### Step 8: Verify MySQL Installation

1. **Check Running Containers:**
   ```sh
   sudo docker ps
   ```

   You should see an output listing the `mysql-db` container along with its status. The status should indicate that the container is up and running.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-16.png)

2. **Access the MySQL Container:**
   ```sh
   sudo docker exec -it mysql-db mysql -u poridhi_user -p
   ```

   When prompted, enter the password (`poridhi_24`).

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-17.png)

3. **Check MySQL Version:**
   ```sql
   SELECT VERSION();
   ```

   This should display the MySQL version indicating that MySQL is running correctly.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-18.png)

4. **Verify Database and User:**
   - **Show Databases:**
     ```sql
     SHOW DATABASES;
     ```
     You should see the `poridhi` database listed among the default MySQL databases.

   - **Use the `poridhi` Database:**
     ```sql
     USE poridhi;
     ```

   - **Create a Test Table:**
     ```sql
     CREATE TABLE test_table (id INT PRIMARY KEY, name VARCHAR(50));
     ```

   - **Insert Data into the Test Table:**
     ```sql
     INSERT INTO test_table (id, name) VALUES (1, 'Test Name');
     ```

   - **Query the Test Table:**
     ```sql
     SELECT * FROM test_table;
     ```

     You should see the data you inserted, confirming that the database is functioning correctly.

5. **Exit the MySQL Prompt:**
   ```sql
   EXIT;
   ```

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2005/images/dc-19.png)

## Conclusion

Congratulations! You have successfully deployed a MySQL server in a private subnet on AWS using Docker and Docker Compose. This setup ensures secure access and configuration, protecting the MySQL server's data and operations. By following the verification steps, you can confirm that MySQL is installed, running, and accessible on your EC2 instance within the private subnet.