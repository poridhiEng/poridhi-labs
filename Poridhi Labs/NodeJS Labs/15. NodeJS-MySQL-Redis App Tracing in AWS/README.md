# Tracing a NodeJS-Redis-MySQL App with OpenTelemetry and Grafana Tempo in AWS 

Tracing is a method to monitor and track requests as they traverse through various services and systems. This guide will help you set up distributed tracing in a Node.js application using OpenTelemetry and Grafana Tempo. 


![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-1.png?raw=true)

## Components 

**Node.js App**:
- The Node.js application is instrumented with the OpenTelemetry SDK to generate telemetry data (traces).
- It connects to the MySQL database to store and retrieve application data.
- It connects to the Redis server for caching purposes.

**MySQL**:
- The database server where the application's persistent data is stored.

**Redis**:
- The caching layer used by the Node.js application to store frequently accessed data for faster retrieval.

**OpenTelemetry (OTel) Collector**:
- Receives telemetry data from the Node.js application.
- Collects, processes, and exports telemetry data to Tempo.

**Tempo**:
- Stores the telemetry data (traces) received from the OTel Collector.

**Grafana**:
- Connects to Tempo to visualize the collected traces and provides monitoring and visualization capabilities for the distributed tracing setup.

## How the Connections Work

- **Node.js App to MySQL**: The Node.js application uses a MySQL client library to connect to the MySQL database.
- **Node.js App to Redis**: The Node.js application uses a Redis client library to connect to the Redis server.
- **Node.js App to OTel Collector**: The OpenTelemetry SDK in the Node.js application sends telemetry data to the OTel Collector.
- **OTel Collector to Tempo**: The OTel Collector exports the telemetry data to Tempo for storage.
- **Grafana to Tempo**: Grafana queries Tempo to retrieve and visualize the stored traces.



## Deploy AWS Infrastucture with Pulumi using GitHub Actions 

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image.png?raw=true)


### Step 0: Generate key for Instace

Run the following command locally:

```
ssh-keygen -t rsa -b 2048 
```

This will generate two files, typically in the ~/.ssh directory:

- id_rsa (private key)
- id_rsa.pub (public key)

Create a `.pem` file for ssh:

```shell
cd .ssh
ssh-keygen -f id_rsa -m PEM -e > my-key-pair.pem
```

Here are the files in  `.ssh`:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-9.png?raw=true)





### Step 1: Set Up Pulumi

#### Install Pulumi CLI
Follow the installation instructions on the Pulumi installation page.

#### Create a New Pulumi Project

```bash
mkdir pulumi-aws-setup
cd pulumi-aws-setup
pulumi new aws-javascript
```

<!-- #### Configure AWS CLI

Ensure you have the AWS CLI installed and configured with your credentials.
```bash
aws configure
``` -->

### Step 2: Write Pulumi Code

#### Install Pulumi AWS SDK

```bash
npm install @pulumi/aws
```

#### Modify index.js to Create Resources

You should use `ap-southeast-1` as Region and `ap-southeast-1a` as Availability Zone.

```js
"use strict";
const pulumi = require("@pulumi/pulumi");
const aws = require("@pulumi/aws");

// Create a VPC
const vpc = new aws.ec2.Vpc("my-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
    tags: {
        Name: "my-vpc",
    },
});

// Create an Internet Gateway
const internetGateway = new aws.ec2.InternetGateway("my-igw", {
    vpcId: vpc.id,
    tags: {
        Name: "my-igw",
    },
});

// Create a Public Subnet
const publicSubnet = new aws.ec2.Subnet("public-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "us-east-1a", // Change this to your desired AZ
    mapPublicIpOnLaunch: true,
    tags: {
        Name: "public-subnet",
    },
});

// Create a Route Table
const routeTable = new aws.ec2.RouteTable("public-rt", {
    vpcId: vpc.id,
    routes: [
        {
            cidrBlock: "0.0.0.0/0",
            gatewayId: internetGateway.id,
        },
    ],
    tags: {
        Name: "public-rt",
    },
});

// Associate the Route Table with the Public Subnet
const routeTableAssociation = new aws.ec2.RouteTableAssociation("public-rta", {
    subnetId: publicSubnet.id,
    routeTableId: routeTable.id,
});

// Create a Security Group
const securityGroup = new aws.ec2.SecurityGroup("web-sg", {
    description: "Allow inbound HTTP and SSH traffic",
    vpcId: vpc.id,
    ingress: [
        {
            protocol: "tcp",
            fromPort: 80,
            toPort: 80,
            cidrBlocks: ["0.0.0.0/0"],
        },
        {
            protocol: "tcp",
            fromPort: 22,
            toPort: 22,
            cidrBlocks: ["0.0.0.0/0"], // For better security, replace with your IP
        }
    ],
    egress: [{
        protocol: "-1",
        fromPort: 0,
        toPort: 0,
        cidrBlocks: ["0.0.0.0/0"],
    }],
    tags: {
        Name: "web-sg",
    },
});

// Create a key pair
const keyPair = new aws.ec2.KeyPair("my-key-pair", {
    publicKey: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDrBtUDgbLUtQzrFcRw9tLx0z9I6mI2VQdjPtMQ/qcupPE20DiXtWx57jkK3p0CayZk/+5e0nZJwjXCQkls0mSpCk0YUINQx22Ix09dPcuQc7dBZS3yZPFQAlZkjyVijT2cToaqwZyZzE2M5vD04gdGXBzpU2XZ4s/ifLTGP/VWX/2ZYq+yDaWw1TOe8vzFQ7LoK9qY28x6woZ+9VmDp0bBaeMIZ5cEUdf76fSusvsnwbJ4sVAmxibRfYOsX5UwQo9nSUq82PvqkjYMpiWowMgQwYyLseXDrQIizrBtUFpgnl3Vo2+wWItQr6vNnVQSGEw+Tb9WJYfTCPE18hQr1NMF minha@myLegion", // Replace with your public key
});

// Create two EC2 instances
const createEC2Instance = (name, az) => {
    return new aws.ec2.Instance(name, {
        instanceType: "t3.small",
        ami: "ami-04a81a99f5ec58529",  // Change with your ami ID
        subnetId: publicSubnet.id,
        associatePublicIpAddress: true,
        vpcSecurityGroupIds: [securityGroup.id],
        availabilityZone: az,
        keyName: keyPair.keyName,
        tags: {
            Name: name,
        },
    });
};

const instance1 = createEC2Instance("instance-1", "us-east-1a");
const instance2 = createEC2Instance("instance-2", "us-east-1a");

// Export the VPC ID and EC2 instance public IPs
exports.vpcId = vpc.id;
exports.instance1PublicIp = instance1.publicIp;
exports.instance2PublicIp = instance2.publicIp;
```

### Step 3: Set Up GitHub Actions
Create `.github/workflows/deploy.yml`

```yaml
name: Pulumi Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '14.x'

      - name: Install Pulumi
        run: npm install -g pulumi

      - name: Install Dependencies
        run: npm install

      - name: Pulumi Preview
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: pulumi preview

      - name: Pulumi Up
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: pulumi up --yes
```

### Step 4: Add GitHub Secrets
Go to your **GitHub repository** > **Settings** > **Secrets and variables** > **Actions**. Add the following secrets:
- PULUMI_ACCESS_TOKEN
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-2.png?raw=true)

### Step 5: Push Changes to GitHub
```bash
git add .
git commit -m "Initial Pulumi setup"
git push origin main
```

This setup will create a `VPC`, a public `subnet` with the necessary `route tables` and `gateways`, and two `EC2 instances` within that subnet using Pulumi.js and GitHub Actions for CI/CD.

If we got to **github repository** > **Actions** we can see the workflow that we created running. We can also see the details by clicking it:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-5.png?raw=true)

### Step 6: Verify the Infrastructure in AWS

#### Resource map:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-3.png?raw=true)

#### Security group inbound rules:

Here I have allowed `all traffic` manually for now: 

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-4.png?raw=true)

#### EC2 Instances:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-6.png?raw=true)


## Setup NodeJS service, MySQL and Redis in instance-1

Go to `instance-1` and click `connect`. Go to `SSH client`. You will get a SSH command something like this:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-7.png?raw=true)

Go to your .`.ssh` folder where we have the private key to SSH into the instance. Use it from your terminal to SSH into that instance.

Once you are connected to the instance, follow the steps below:

### Install Docker

```
sudo apt update
sudo apt install vim -y
```
#### Save this `install.sh` 
Open install.sh using vim : `vim install.sh`:

```bash
echo "Updating package database..."
sudo apt update

echo "Upgrading existing packages..."
sudo apt upgrade -y

echo "Installing required packages..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

echo "Adding Docker’s GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "Adding Docker APT repository..."
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Updating package database with Docker packages..."
sudo apt update

echo "Installing Docker..."
sudo apt install -y docker-ce

echo "Starting Docker manually in the background..."
sudo dockerd > /dev/null 2>&1 &

echo "Adding current user to Docker group..."
sudo usermod -aG docker ${USER}

echo "Applying group changes..."
newgrp docker

echo "Setting Docker socket permissions..."
sudo chmod 666 /var/run/docker.sock

echo "Verifying Docker installation..."
docker --version

echo "Running hello-world container in the background..."
docker run -d hello-world

echo "Docker installation completed successfully."
echo "If you still encounter issues, please try logging out and logging back in."

```

Run the command:
```
chmod +x install.sh
./install.sh
```

After running the command docker will be installed.



### Run MySQL and Redis using Docker Compose

Edit `docker-compose.yaml`:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:latest
    container_name: mysql
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: my_db
      MYSQL_USER: my_user
      MYSQL_PASSWORD: my_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis/redis-stack:latest
    container_name: redis
    ports:
      - "6379:6379"
      - "8001:8001"
    volumes:
      - redis_data:/data

volumes:
  mysql_data:
  redis_data:
```

Use the following command to run the compose file:

```
docker compose up -d
```


### Setup NodeJS service


#### Init Project
```bash
npm init -y
```

#### Install packages

At first install `node` and `npm`:

```bash
sudo apt install nodejs
sudo apt install npm
```

Install all the dependencies. you can use the following npm install command:

```bash
npm install @opentelemetry/api@^1.9.0 @opentelemetry/auto-instrumentations-node@^0.47.1 @opentelemetry/exporter-metrics-otlp-http@^0.52.1 @opentelemetry/exporter-otlp-grpc@^0.26.0 @opentelemetry/exporter-trace-otlp-grpc@^0.52.1 @opentelemetry/exporter-trace-otlp-http@^0.52.1 @opentelemetry/sdk-metrics@^1.25.1 @opentelemetry/sdk-node@^0.52.1 @opentelemetry/sdk-trace-node@^1.25.1 express@^4.19.2 mysql2@^3.10.1 redis@^4.6.14 sequelize@^6.37.3
```
You can run this command in your terminal within the project directory to install all the necessary packages at once.


#### Set the config files 

Edit the config files for `MySQL` and `Redis`.

Open `config/database.js` and edit:

```js
// config/database.js
const { Sequelize } = require('sequelize');

const sequelize = new Sequelize('my_db', 'my_user', 'my_password', {
  host: 'localhost',
  dialect: 'mysql',
});

module.exports = sequelize;

```

Open `config/redis.js` using `vim` or `nano` and edit:

```js
// config/redis.js
const redis = require('redis');
const client = redis.createClient({
  url: 'redis://localhost:6379'
});

client.connect().catch(console.error);

client.on('error', (err) => {
  console.error('Redis error:', err);
});

module.exports = client;
```

#### Create model for the server

Open `models/User.js`   using `vim` or `nano` and edit:

```js
// models/User.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const User = sequelize.define('User', {
  username: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  email: {
    type: DataTypes.STRING,
    allowNull: false,
  },
});

module.exports = User;
```

#### Setup Trace SDK
Open `tracing.js`   using `vim` or `nano` and edit:

```js
// tracing.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-otlp-grpc');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

const resource = Resource.default().merge(
  new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'user-service',
  })
);

const traceExporter = new OTLPTraceExporter({
  url: 'http://localhost:4317',
});

const sdk = new NodeSDK({
  resource: resource,
  traceExporter,
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
```

#### Setup the server

Open `index.js`   using `vim` or `nano` and edit:

```js
require('./tracing');
const express = require('express');
const sequelize = require('./config/database');
const redisClient = require('./config/redis');
const User = require('./models/User');
const { trace } = require('@opentelemetry/api');

const app = express();
app.use(express.json());

// Middleware to cache responses
const cache = async (req, res, next) => {
  const { username } = req.params;
  try {
    const data = await redisClient.get(username);
    if (data) {
      return res.json(JSON.parse(data));
    } else {
      next();
    }
  } catch (err) {
    console.error('Redis error:', err);
    next();
  }
};

// Invalidate cache middleware
const invalidateCache = async (req, res, next) => {
  const { username } = req.params;
  if (username) {
    try {
      await redisClient.del(username);
    } catch (err) {
      console.error('Redis error:', err);
    }
  }
  next();
};

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/user', async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('get_all_users');
  try {
    const users = await User.findAll();
    res.json(users);
  } catch (error) {
    span.recordException(error);
    res.status(500).json({ error: error.message });
  } finally {
    span.end();
  }
});

app.get('/user/:username', cache, async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('get_user_by_username');
  span.setAttribute('username', req.params.username);
  try {
    const { username } = req.params;
    const user = await User.findOne({ where: { username } });

    if (user) {
      await redisClient.setEx(username, 3600, JSON.stringify(user));
      res.json(user);
    } else {
      res.status(404).send('User not found');
    }
  } catch (error) {
    span.recordException(error);
    res.status(500).send(error.message);
  } finally {
    span.end();
  }
});

app.post('/user', async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('create_user');
  try {
    const { username, email } = req.body;
    span.setAttributes({ username, email });
    const newUser = await User.create({ username, email });
    res.status(201).json(newUser);
  } catch (error) {
    span.recordException(error);
    res.status(500).send(error.message);
  } finally {
    span.end();
  }
});

app.put('/user/:username', invalidateCache, async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('update_user');
  span.setAttribute('username', req.params.username);
  try {
    const { username } = req.params;
    const { email } = req.body;
    span.setAttribute('new_email', email);
    const user = await User.findOne({ where: { username } });

    if (user) {
      user.email = email;
      await user.save();
      await redisClient.setEx(username, 3600, JSON.stringify(user));
      res.json(user);
    } else {
      res.status(404).send('User not found');
    }
  } catch (error) {
    span.recordException(error);
    res.status(500).send(error.message);
  } finally {
    span.end();
  }
});

app.delete('/user/:username', invalidateCache, async (req, res) => {
  const span = trace.getTracer('user-service').startSpan('delete_user');
  span.setAttribute('username', req.params.username);
  try {
    const { username } = req.params;
    const user = await User.findOne({ where: { username } });

    if (user) {
      await user.destroy();
      await redisClient.del(username);
      res.status(204).send();
    } else {
      res.status(404).send('User not found');
    }
  } catch (error) {
    span.recordException(error);
    res.status(500).send(error.message);
  } finally {
    span.end();
  }
});

const startServer = async () => {
  try {
    await sequelize.sync({ force: true });
    app.listen(5000, () => {
      console.log('Server is running on http://localhost:5000');
    });
  } catch (error) {
    console.error('Unable to connect to the database:', error);
  }
};

startServer();

```


#### Run/start the NodeJS application
```
node index.js
```

## Setup Otel-collector, Tempo and Grafana in instance-2

Go to `instance-2` and click `connect`. Go to `SSH client`. You will get a SSH command something like this:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-7.png?raw=true)

Use it from your terminal to SSH into that instance.

Once you are connected to the instance, follow the steps below:

### Install Docker

We have already installed docker in instance-1. Follow the same steps here to install the Docker in this instance.

### Setup Otel-Collector configuration

Open `otel-collector-config.yml` using `vim` or `nano` and edit:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

exporters:
  logging:
  otlp:
    endpoint: tempo:4317
    tls:
      insecure: true
  debug:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: []
      exporters: [logging, otlp]

    metrics:
      receivers: [otlp]
      exporters: [debug]
      
    logs:
      receivers: [otlp]
      exporters: [debug]
```

### Setup Tempo configuration

Open `tempo.yaml`  using `vim` or `nano` and edit:
```yaml
server:
  http_listen_port: 3100

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317

ingester:
  trace_idle_period: 30s
  max_block_bytes: 1048576  # 1MiB in bytes

querier:
  frontend_worker:
    frontend_address: 127.0.0.1:9095

storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/traces

compactor:
  compaction:
    block_retention: 48h

```


### Create Dockcer compose file

Edit `docker-compose.yaml`:

```yaml
version: '3.8'

services:

  otel-collector:
    image: otel/opentelemetry-collector-contrib
    container_name: otel-collector
    ports:
      - "4317:4317"
      - "55681:55681"
    volumes:
      - ./otel-collector-config.yml:/etc/otel-collector-config.yml
    command:
      --config etc/otel-collector-config.yml


  tempo:
    image: grafana/tempo:latest
    container_name: tempo
    ports:
      - "3100:3100"
    volumes:
      - ./tempo.yaml:/etc/tempo.yaml
    command:
      -config.file=/etc/tempo.yaml


  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - tempo
```

Use the following command to run the compose file:

```
docker compose up -d
```





## Verify the traces 

If we visit `https://<instance-1-public-ip>:5000` we will see our node app:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/15.%20NodeJS-MySQL-Redis%20App%20Tracing%20in%20AWS/images/image-8.png?raw=true)

We can also perform CRUD operations with `/user` route. We can see traces of  our operations in grafana.

Once the application is running, access Grafana at `http://<instance-2-public-ip>:3000` and log in with the default credentials (`admin`/`admin`).

### Configure Data Source in Grafana

1. Navigate to **Configuration** > **Data Sources**.
2. Click on **Add data source**.
3. Select **Tempo** from the list.
4. Configure the URL as `http://tempo:3100`.
5. Click **Save & Test** to ensure the connection is working.

### Create Dashboards and Panels

1. Navigate to **Create** > **Dashboard**.
2. Add a new panel and configure it to visualize traces.
3. Use the data source you just configured (Tempo) to query and display trace data.

### Trying different queries

wehave tried some different queries regarding http `methods` and `status code`. wehave also made some panels in dashboard. 

Here are the TraceQL queries:

1. TraceQL query for Successful HTTP requests (`2xx` status codes):

    ```sql
    { span.http.status_code >= 200 && span.http.status_code < 300 }
    ```

2. TraceQL for client error HTTP requests (`4xx` status codes):

    ```sql
    { span.http.status_code >= 400 && span.http.status_code <500 }
    ```

3. TraceQL query for HTTP `GET` requests:

    ```sql
    { span.http.method = "GET" }
    ```

4. TraceQL query for HTTP `POST` requests:

    ```sql
    { span.http.method = "POST" }
    ```


We have some panels here in our dashboard created from these queries:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/8.%20Tracing%20a%20NodeJS%20App%20with%20OpenTelemetry%20and%20Grafana%20Tempo/images/img1.jpg?raw=true)

The image shows a Grafana dashboard with multiple panels, each displaying metrics related to HTTP requests.
- Successful HTTP requests (2xx status codes).
- Client error HTTP requests (4xx status codes).
- HTTP GET requests.
- HTTP POST requests.


### Displaying Trace data

Now go to **`Menu`** > **`Explore`**. Here let's try to trace the `MySQL` and `Redis` from our server using some query.

1. TraceQL query for Redis query data:

    ```
    { span.db.system = "redis" }
    ```

2. TraceQL query for MySQL query data:

    ```
    { span.db.system = "mysql" }
    ```

We have added the trace tables of a particular query in a different dashboard:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/8.%20Tracing%20a%20NodeJS%20App%20with%20OpenTelemetry%20and%20Grafana%20Tempo/images/image.png?raw=true)

If we click on any of the TraceID, we will see the trace information in details:

Here is one example for a redis query trace:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/8.%20Tracing%20a%20NodeJS%20App%20with%20OpenTelemetry%20and%20Grafana%20Tempo/images/image-1.png?raw=true)

Here is another example for a MySQL query trace:

![alt text](https://github.com/Minhaz00/NodeJS-Tasks/blob/main/8.%20Tracing%20a%20NodeJS%20App%20with%20OpenTelemetry%20and%20Grafana%20Tempo/images/image-2.png?raw=true)

## Summary
We have now set up a Node.js application with distributed tracing using OpenTelemetry and Grafana Tempo. The traces collected from our application are sent to the OpenTelemetry Collector, which then forwards them to Grafana Tempo for storage and visualization. By following these steps, we can monitor and analyze the performance and behavior of our distributed system.