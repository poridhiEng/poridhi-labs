# Nginx Layer 7 Load Balancing on NodeJS-MySQL App in AWS

This document outlines the process of setting up a layer 7 load-balanced Node.js application environment using Nginx. The setup consists of two identical Node.js applications, an Nginx server for load balancing. We will use mysql database for this app. Here we will deploy it in AWS.

<img src="https://github.com/Minhaz00/NodeJS-MySQL/blob/main/11.%20Nginx%20L4%20LB%20NodeJS-MySQL%20App%20in%20AWS/images/nginx-01.PNG?raw=true" />

## Task
Create a load-balanced environment with two Node.js applications, Nginx as a load balancer, and a MySQL database, all running in AWS EC2 instance.


## Setup in AWS

### Create VPC, subnets, route table and gateways 

At first, we need to create a VPC in AWS, configure subnet, route tables and gateway.

- At first, we have created a VPC named `my-vpc`.

- Then, we have created 2 subnets: `public-subnet` and `private-subnet` in `my-vpc`.

- Creat necessary internet gateway, NAT gateways and route tables.

Here is the `resource-map` of our VPC:

<img src="https://github.com/Minhaz00/NodeJS-MySQL/blob/main/10.%20Nginx%20L4%20LB%20NodeJS%20service%20in%20AWS/image/image.jpg?raw=true" />

### Create EC2 instance

We need to create `3 instances` in EC2. 

#### Create the NodeJS App EC2 Instances:
- Launch two EC2 instances (let's call them `node-app-1` and `node-app-2`) in our private subnet.
- Choose an appropriate AMI (e.g., Ubuntu).
- Configure the instances with necessary security group rules to allow HTTP/HTTPS traffic (typically port 80/443).
- Assign a key pair for SSH access.

#### Create the NGINX EC2 Instance:
- Launch another EC2 instance for the NGINX load balancer (let's call it `nginx-lb`) in our public subnet.
- Configure the instance with a security group to allow incoming traffic on the load balancer port (typically port 80/443) and outgoing traffic to the NodeJS servers.
- Assign a key pair for SSH access.

#### Create the mysql EC2 Instance:
- Launch another EC2 instance for the MySQL Database (let's call it `mysql`).

### Access the Public Instance via SSH

1. **Set File Permissions**:
   - **For Windows**: Open PowerShell and navigate to the directory where `MyKeyPair.pem` is located. Then, use the following command to set the correct permissions:
     ```powershell
     icacls MyKeyPair.pem /inheritance:r
     icacls MyKeyPair.pem /grant:r "$($env:USERNAME):(R)"
     ```

   - **For Linux**:
     ```sh
     chmod 400 MyKeyPair.pem
     ```

2. **SSH into the Public Instance**:
   - Open a terminal and run:
     ```sh
     ssh -i MyKeyPair.pem ubuntu@<public_instance_ip>
     ```
   - Replace `<public_instance_ip>` with the public IP address of the public instance.

### Copy the Key Pair to the Public Instance

3. **Copy the Key Pair to the Public Instance**:
   - On your local machine, run the following command to copy the key pair to the public instance:
     ```sh
     scp -i MyKeyPair.pem MyKeyPair.pem ubuntu@<public_instance_ip>:~
     ```
   - Replace `<public_instance_ip>` with the public IP address of the public instance.

### SSH from the Public Instance to the Private Instance

3. **SSH into the Private Instance from the Public Instance**:
   - On the public instance, change the permissions of the copied key pair:
     ```sh
     chmod 400 MyKeyPair.pem
     ```
   - Then, SSH into the private instance:
     ```sh
     ssh -i MyKeyPair.pem ubuntu@<private_instance_ip>
     ```
   - Replace `<private_instance_ip>` with the private IP address of the private instance.


### Step 1: Install NGINX on the Load Balancer Instance

1. **Update the package list and install NGINX:**
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

### Step 2: Configure NGINX for Load Balancing

1. **Edit the NGINX default site configuration:**
   ```bash
   sudo nano /etc/nginx/sites-available/default
   ```

2. **Add the following configuration to the file:**
   ```nginx
   upstream nodejs_backend {
       server 10.0.2.25:5001;  # Node-app-1
       server 10.0.2.100:5002;  # Node-app-2
   }

   server {
       listen 80 default_server;
       listen [::]:80 default_server;

       server_name _;

       location / {
           proxy_pass http://nodejs_backend;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;

           # Additional headers for proper proxying
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Save and exit the file** (`Ctrl+O`, `Enter`, `Ctrl+X`).

4. **Reload NGINX to apply the changes:**
   ```bash
   sudo systemctl reload nginx
   ```

### Step 3: Setup MySQL Database in a Docker Container

1. **SSH into your instance where you want to run the MySQL Docker container.**

2. **Install Docker:**
   ```bash
   sudo apt update
   sudo apt install apt-transport-https ca-certificates curl software-properties-common
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   sudo apt update
   sudo apt install docker-ce
   ```

3. **Run the MySQL Docker container:**
   ```bash
   docker run --name my_mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=my_db -e MYSQL_USER=my_user -e MYSQL_PASSWORD=my_password -p 3306:3306 -v mysql_data:/var/lib/mysql -d mysql:latest
   ```

### Step 4: Setup Node.js Applications on Different Instances

1. **SSH into each Node.js instance and perform the following steps:**

2. **Update the package list and install npm:**
   ```bash
   sudo apt update
   sudo apt install npm
   ```

3. **Create a directory for your Node.js application and navigate into it:**
   ```bash
   mkdir node-app
   cd node-app
   ```

4. **Initialize a new Node.js project:**
   ```bash
   npm init -y
   ```

5. **Install Express and MySQL2 libraries:**
   ```bash
   npm install express mysql2 body-parser
   ```

6. **Create the application file:**
   ```bash
   nano index.js
   ```

7. **Add the following code to `index.js`:**
   ```javascript
   const express = require('express');
   const mysql = require('mysql2');
   const bodyParser = require('body-parser');

   const app = express();
   const port = process.env.PORT || 3000;

   const dbConfig = {
     host: "<mysql-instance-private-ip>",
     user: 'my_user',
     password: 'my_password',
     database: 'my_db'
   };

   app.use(bodyParser.json());

   function createConnection() {
     const connection = mysql.createConnection(dbConfig);
     connection.connect(error => {
       if (error) {
         console.error('Error connecting to the database:', error);
         return null;
       }
       console.log('Connected to MySQL database');
     });
     return connection;
   }

   function createTable() {
     const connection = createConnection();
     if (connection) {
       const createTableQuery = `
         CREATE TABLE IF NOT EXISTS users (
           id INT AUTO_INCREMENT PRIMARY KEY,
           name VARCHAR(255) NOT NULL,
           email VARCHAR(255) NOT NULL UNIQUE
         )
       `;
       connection.query(createTableQuery, (error, results) => {
         connection.end();
         if (error) {
           console.error('Error creating table:', error);
         } else {
           console.log('Table "users" ensured to exist');
         }
       });
     }
   }

   createTable();

   app.get('/', (req, res) => {
     const connection = createConnection();
     if (connection) {
       res.status(200).json({ message: `Hello, from Node App on PORT: ${port}! Connected to MySQL database.` });
       connection.end();
     } else {
       res.status(500).json({ message: 'Failed to connect to MySQL database' });
     }
   });

   app.get('/users', (req, res) => {
     const connection = createConnection();
     if (connection) {
       connection.query('SELECT * FROM users', (error, results) => {
         connection.end();
         if (error) {
           return res.status(500).json({ message: 'Error fetching users', error });
         }
         res.json(results);
       });
     } else {
       res.status(500).json({ message: 'Failed to connect to MySQL database' });
     }
   });

   app.post('/users', (req, res) => {
     const connection = createConnection();
     const { name, email } = req.body;

     if (!name || !email) {
       return res.status(400).json({ message: 'Name and email are required' });
     }

     if (connection) {
       const query = 'INSERT INTO users (name, email) VALUES (?, ?)';
       connection.query(query, [name, email], (error, results) => {
         connection.end();
         if (error) {
           return res.status(500).json({ message: 'Error adding user', error });
         }
         res.status(201).json({ message: 'User added', userId: results.insertId });
       });
     } else {
       res.status(500).json({ message: 'Failed to connect to MySQL database' });
     }
   });

   app.listen(port, () => {
     console.log(`App running on port :${port}`);
   });
   ```

8. **Set the port environment variable and start the application:**
   ```bash
   export PORT=5001  # or 5002 for the second instance
   node index.js
   ```

### Step 5: Verify the Load Balancing Setup

1. **Access the public IP of your NGINX load balancer in a web browser**:
   ```http
   http://<load-balancer-public-ip>
   ```
   <img src="https://github.com/Minhaz00/NodeJS-MySQL/blob/main/11.%20Nginx%20L4%20LB%20NodeJS-MySQL%20App%20in%20AWS/images/app1.png?raw=true" />

    <img src="https://github.com/Minhaz00/NodeJS-MySQL/blob/main/11.%20Nginx%20L4%20LB%20NodeJS-MySQL%20App%20in%20AWS/images/app2.png?raw=true" />

By following these steps, you set up a Layer-7 load balancer using NGINX to distribute traffic between two Node.js applications running on different instances and connect these applications to a MySQL database running in a Docker container. This ensures that the load is balanced and provides high availability for your applications.