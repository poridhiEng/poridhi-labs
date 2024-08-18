# Deploy Redis on EC2 Using Systemd

In this lab, we will demonstrate how to launch an EC2 instance and deploy Redis using systemd. Redis is a powerful, open-source, in-memory data structure store used as a database, cache, and message broker. By the end of this lab, you will have a running Redis instance managed by systemd on an EC2 instance.

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-19.png?raw=true)

## What is Redis?

Redis is an advanced key-value store. It's often referred to as a data structure server because keys can contain strings, hashes, lists, sets, and sorted sets. Redis is commonly used for caching, session management, real-time analytics, and more.



## Step-by-Step Instructions

### Step 1: Create VPC and Subnet

1. **Create a VPC**:
   - Navigate to the VPC dashboard in the AWS Management Console.
   - Click on "Create VPC".
   - **CIDR block**: `10.0.0.0/16`
   - **Name tag**: `My-VPC`

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image.png?raw=true)

2. **Create a Public Subnet**:
   - Navigate to "Subnets" in the VPC dashboard.
   - Click on "Create Subnet".
   - **VPC**: Select `My-VPC`.
   - **Subnet name**: `My-Subnet`.
   - **Availability Zone**: `ap-southeast-1a`
   - **CIDR block**: `10.0.0.0/24`

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-1.png?raw=true)

3. **Enable Auto-Assign Public IP**:
   - Select the newly created subnet.
   - Click on "Actions" > "Modify auto-assign IP settings".
   - Check the box to enable auto-assign public IPv4 address.
   - Save the changes.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-2.png?raw=true)

4. **Create and Attach Internet Gateway**:
   - Navigate to "Internet Gateways" in the VPC dashboard.
   - Click on "Create Internet Gateway".
   - **Name tag**: `My-IG`
   - Click on "Create internet gateway".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-3.png?raw=true)

   - Select the newly created internet gateway.
   - Click on "Actions" > "Attach to VPC".
   - Select `My-VPC` and attach the gateway.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-4.png?raw=true)

5. **Create and Associate Route Table**:
   - Navigate to "Route Tables" in the VPC dashboard.
   - Click on "Create Route Table".
   - **Name tag**: `my-RT`
   - **VPC**: Select `My-VPC`
   - Click on "Create".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-5.png?raw=true)

   - Select the newly created route table.
   - Click on "Actions" > "Edit routes".
   - Add a route with destination `0.0.0.0/0` and target the internet gateway (`My-IG`).
   - Save the changes.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-6.png?raw=true)

   - Select the route table again.
   - Click on "Actions" > "Edit subnet associations".
   - Associate the route table with `My-Subnet`.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-7.png?raw=true)

### Step 2: Create Security Group

1. **Create a Security Group** for the public subnet:
   - Navigate to "Security Groups" in the VPC dashboard.
   - Click on "Create Security Group".
   - **Name tag**: `My-SG`
   - **VPC**: Select `My-VPC`.
   - **Description**: `My-SG`.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-8.png?raw=true)

2. **Inbound Rules**:
   - Click on "Inbound rules" > "Edit inbound rules".
   - Add a rule to allow TCP traffic on port 6379 (Redis):
     - **Type**: Custom TCP
     - **Port range**: 6379
     - **Source**: Custom, `0.0.0.0/0` (for testing purposes; in a real environment, restrict to specific IPs)
   - Save the changes.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-9.png?raw=true)

3. **Outbound Rules**:
   - By default, all outbound traffic is allowed. No changes are needed unless you want to restrict it.

### Step 3: Launch EC2 Instance

1. **Launch an EC2 Instance**:
   - Navigate to the EC2 dashboard.
   - Click on "Launch Instance".
   - **Name and Tags**: `Redis-instance`.
   - **AMI**: Select an Ubuntu Server 20.04 LTS AMI.
   - **Instance Type**: Choose `t2.micro` for testing purposes.
   - **Key Pair**:Generate a key pair and save it for later SSH communication. We saved it as `key.pem`.



   - **Network Settings**:
     - **VPC**: Select `My-VPC`.
     - **Subnet**: Select `My-Subnet`.
     - **Auto-assign Public IP**: Enabled.
     - **Security Group**: Select `My-SG`.
   

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-10.png?raw=true)

   - Launch the instance.


### Step 4: Connect to EC2 Instance

1. **Connect to your EC2 instance** using SSH:

    ```sh
    chmod 400 "key.pem"
    ```

    This command ensures that your private key file has the correct permissions. It prevents others from being able to read the key, which is necessary for SSH to work.

    ```sh
    ssh -i "key.pem" ubuntu@<Public-IP>
    ```

    Replace `<Public-IP>` with the public IP address of your EC2 instance. This command establishes an SSH connection to your instance.

### Step 5: Install Redis

1. **Update packages**:

    ```sh
    sudo apt update
    ```

    This command updates the package list on your instance, ensuring you have the latest information about available packages and their versions.

2. **Install Redis**:

    ```sh
    sudo apt install redis-server
    ```

    This command installs Redis server on your instance.

3. **Verify Redis installation**:

    ```sh
    redis-cli --version
    ```

    This command checks if Redis CLI is installed correctly by displaying its version.

### Step 6: Configure Redis with Systemd

1. **Edit Redis configuration**:

    ```sh
    sudo nano /etc/redis/redis.conf
    ```

    This command opens the Redis configuration file in the Nano text editor.

2. **Set supervised directive to systemd**:
    - Change `supervised no` to `supervised systemd`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-11.png?raw=true)

    This change configures Redis to use `systemd` for process supervision, which is necessary for managing Redis as a service.

3. **Restart Redis service**:

    ```sh
    sudo systemctl restart redis
    ```

    This command restarts the Redis service to apply the configuration changes.

4. **Verify systemd configuration for Redis**:

    ```sh
    cat /etc/systemd/system/redis.service
    ```

    This command displays the contents of the systemd service file for Redis, ensuring it's set up correctly.

### Step 7: Test Redis

1. **Check Redis service status**:

    ```sh
    sudo systemctl status redis
    ```
    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-12.png?raw=true)

    This command checks the status of the Redis service, ensuring it is active and running.

2. **Connect to Redis CLI**:

    ```sh
    redis-cli
    ```

    This command opens the Redis command line interface.

3. **Ping Redis** to check if it's working:

    ```sh
    redis-cli ping
    ```

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-14.png?raw=true)

    You should see `PONG` as the response, indicating that Redis is working correctly.

### Step 8: Create a Redis User

1. **Edit Redis configuration file**:

    ```sh
    sudo nano /etc/redis/redis.conf
    ```

    This command opens the Redis configuration file in the Nano text editor.

2. **Set a password for the default user**:
    - Find and uncomment `#requirepass foobared`, changing `foobared` to a secure password.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-13.png?raw=true)

    This sets a password for the default user, enhancing security. We kept the password `foobared` as it is for now. 

3. **Create a new user in Redis CLI**:

    ```sh
    redis-cli
    ACL SETUSER username on >password allkeys allcommands
    ```

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-15.png?raw=true)

    Replace `username` and `password` with your credentials. This command creates a new user with permissions to execute all commands and access all keys in Redis. In our example, we set the username to minhaz and the password was `foobared`.

4. **Add the new user to the configuration file**:

    ```sh
    sudo nano /etc/redis/redis.conf
    ```

    Add the new user details under the security section in the Redis configuration file.

5. **Restart Redis service**:

    ```sh
    sudo systemctl restart redis
    ```

    This command restarts the Redis service to apply the user configuration changes.

6. **Authenticate with the new user**:

    ```sh
    redis-cli
    AUTH username password
    ```

     ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-15.png?raw=true)

    Use the `username` and `password` you set earlier to authenticate in Redis CLI.

### Step 9: Expose Redis to Public IP

1. **Edit Redis configuration file**:

    ```sh
    sudo nano /etc/redis/redis.conf
    ```

    This command opens the Redis configuration file in the Nano text editor.

2. **Bind Redis to public IP**:
    - Find the `bind` directive
    
    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-16.png?raw=true)
    
    - Add your public IP address to it. For example:
      - `bind 0.0.0.0 ::`

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-17.png?raw=true)

    

    This change allows Redis to listen on all available IP addresses, including the public IP address.

3. **Restart Redis service**:

    ```sh
    sudo systemctl restart redis
    ```

    This command restarts the Redis service to apply the binding changes.

4. **Verify that Redis is accessible from the public IP**:



    ```sh
    redis-cli -h <Public-IP> -a <password> ping
    ```

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2011/images/image-18.png?raw=true)

    Replace `<Public-IP>` with the public IP address of your EC2 instance. You should see `PONG` as the response, indicating that Redis is accessible from the public IP address.

By following these steps, you will have successfully deployed Redis on an EC2 instance using systemd, configured it for secure access, and exposed it to a public IP address for external connections. This setup can be used for various purposes such as caching, real-time analytics, and more.