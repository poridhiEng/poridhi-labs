# Kafka Node.js Application

This project demonstrates the architecture of an event-driven application using Apache Kafka. It features a producer that sends messages to a Kafka topic, which is partitioned across a cluster, and multiple consumer groups that subscribe to these messages, enabling horizontal scaling.

## What is Kafka?

Apache Kafka is a distributed event streaming platform primarily used for building real-time data pipelines and streaming applications. It allows applications to publish (write) and subscribe to (read) streams of data in real-time and to process these streams as they occur. Kafka is highly scalable, fault-tolerant, and designed for distributed systems.

![alt text](https://github.com/Minhaz00/Kafka-NodeJS/blob/main/images/image-3.png?raw=true)

### Key Kafka Concepts

1. **Producer**: The component that writes messages to a Kafka topic.
2. **Consumer**: The component that reads messages from Kafka topics.
3. **Kafka Broker**: A Kafka server that handles message read/write requests.
4. **Topic**: A stream of messages categorized by a name (e.g., "riders_update").
5. **Partition**: A topic is split into partitions to enable parallelism and scalability. Each partition stores a portion of the messages.

### Why Kafka is Important

Kafka plays a vital role in applications that require real-time data processing, such as:

- **Log Aggregation**: Collecting and analyzing logs from multiple sources.
- **Metrics**: Monitoring and aggregating data to get real-time metrics.
- **Event Streaming**: Handling events from multiple sources for processing and decision-making.

For example, in an e-commerce application, Kafka could be used to track user actions (clicks, purchases) and send those actions to other services (inventory updates, recommendations) in real-time.





## Task Description

In this project, we will implement a Kafka setup with a producer and multiple consumers. The project will:

1. Start a Kafka environment using Docker.
2. Create a Kafka topic with multiple partitions.
3. Set up a producer that sends rider location updates to the topic.
4. Run multiple consumers in different consumer groups, each consuming messages from the topic.



Let's get started with the step-by-step solution.


## Project Structure

Here’s a folder structure along with the necessary files and code for our Kafka Node.js project.

```
Kafka-NodeJS/
├── docker-compose.yml
├── src/
│   ├── client.js
│   ├── admin.js
│   ├── producer.js
│   ├── consumer.js
└── README.md
```

### Initiate NodeJS project

Use the following command to initialize the project:

```
mkdir Kafka-NodeJS
cd Kafka-NodeJS
npm init -y
```

Install necessary packages:

```bash
npm install kafkajs readline
```

## Step 1. Kafka Setup using Docker Compose

We start by setting up Kafka and Zookeeper using Docker Compose. Zookeeper is a prerequisite for Kafka to manage broker information and coordinate services.

**docker-compose.yml**:
```yaml
version: '3'

services:
  zookeeper:
    image: zookeeper
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      - KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
```
Run the command below to start Kafka and Zookeeper:

```bash
docker-compose up -d
```

This will expose Kafka on port `9092` and Zookeeper on port `2181`.



## Step 2. Kafka Client Configuration

We use the `kafkajs` library in Node.js for managing Kafka clients (producer, consumer, and admin). Here's the Kafka client setup in `src/client.js`:

```js
const { Kafka } = require("kafkajs");

exports.kafka = new Kafka({
  clientId: "my-app",
  brokers: ["<IP-address>:9092"],
});
```

This sets up the client that will communicate with the Kafka broker on `<IP-address>:9092`.

## Step 3. Kafka Admin to Create Topic

Next, we use Kafka Admin to create a topic named `riders_update` with two partitions:

`src/admin.js`:

```js
const { kafka } = require("./client");

async function init() {
  const admin = kafka.admin();
  console.log("Admin connecting...");
  await admin.connect();
  console.log("Admin Connection Success...");

  console.log("Creating Topic [riders_update]");
  await admin.createTopics({
    topics: [
      {
        topic: "riders_update",
        numPartitions: 2,
      },
    ],
  });
  console.log("Topic Created Success [riders_update]");

  await admin.disconnect();
}

init();
```

## Step 4. Producer Implementation

The producer sends rider location updates to the `riders_update` topic. Based on the rider's location (`north` or `south`), the message is assigned to a partition.

`src/producer.js`:
```js
const { kafka } = require("./client");
const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

async function init() {
  const producer = kafka.producer();

  console.log("Connecting Producer");
  await producer.connect();
  console.log("Producer Connected Successfully");

  rl.setPrompt("> ");
  rl.prompt();

  rl.on("line", async function (line) {
    const [riderName, location] = line.split(" ");
    await producer.send({
      topic: "riders_update",
      messages: [
        {
          partition: location?.toLowerCase() === 'north' ? 0 : 1,
          key: "location-update",
          value: JSON.stringify({ name: riderName, location }),
        },
      ],
    });
  }).on("close", async () => {
    await producer.disconnect();
  });
}

init();
```


## Step 5. Consumer Implementation

Consumers are subscribed to the `riders_update` topic and listen for messages. Each consumer group will process the messages independently.

`src/consumer.js`:

```js
const { kafka } = require("./client");
const group = process.argv[2];

async function init() {
  const consumer = kafka.consumer({ groupId: group });
  await consumer.connect();

  await consumer.subscribe({ topics: ["riders_update"], fromBeginning: true });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      console.log(
        `${group}: [${topic}]: PART:${partition}:`,
        message.value.toString()
      );
    },
  });
}

init();
```

## Step 6. Create Topic, Start Producer and Consumer  

Navigate to src directory to create topic, start producer and consumer. 

![](https://github.com/Minhaz00/Kafka-NodeJS/blob/main/images/image-1.png?raw=true)

- Run the following command to create the topic:

    ```bash
    node admin.js
    ```

- Open new terminal and start the producer:
    ```bash
    node producer.js
    ```
    Input rider name and location (`north` or `south`) to send location updates. We will see that in the next step.


- Open 3 new terminal for 3 consumers. Start consumers in different groups (2 consumers in group 1 and 1 consumer in group 2):

    ```bash
    node consumer.js group1 # group 1 consumer 1
    node consumer.js group1 # group 1 consumer 2
    node consumer.js group2 # group 2 consumer 1
    ```

    Each consumer group will receive and process the messages from the topic.

## Step 7. Final Testing

### Kafka Load Balancing in Consumer Groups

Kafka handles load balancing among consumers using **consumer groups**, where each group works together to consume messages from partitions of a topic. This allows Kafka to scale message consumption horizontally.

![alt text](https://github.com/Minhaz00/Kafka-NodeJS/blob/main/images/image-5.png?raw=true)

#### How It Works:

1. **Consumer Group**: A group of consumers that share the workload. Each consumer in a group processes messages from a subset of partitions, ensuring messages from the same partition are only processed by one consumer within that group.
  
2. **Partition Assignment**: When consumers subscribe to a topic, Kafka dynamically assigns partitions to each consumer. If there are more partitions than consumers, a consumer will handle multiple partitions. When a new consumer joins or a consumer leaves, Kafka rebalances the partitions among the available consumers.

3. **Rebalancing**: Whenever a consumer joins or leaves the group, Kafka redistributes the partitions to maintain even load distribution across active consumers. This ensures continued message processing without downtime.

4. **Load Balancing**: Kafka ensures each partition is processed by only one consumer per group. If a consumer fails, Kafka reassigns its partitions to other consumers, ensuring fault tolerance.



### Example in Our Project

![alt text](https://github.com/Minhaz00/Kafka-NodeJS/blob/main/images/image-4.png?raw=true)

In  project, where the topic `riders_update` has 2 partitions, and we have multiple consumers, Kafka distributes the partitions dynamically:

- **Two consumers in the same group**:
   When we run two consumers in the same group (`group1`), Kafka assigns one partition to each consumer. For example:
   
   ```bash
   node consumer.js group1  # Consumer 1
   node consumer.js group1  # Consumer 2
   ```

   - `Consumer 1` processes messages from **Partition 0**.
   - `Consumer 2` processes messages from **Partition 1**.


- **Separate consumer groups**:
   If we run two consumers in different group it will independently consume all partitions:

   ```bash
   node consumer.js group2 ## Consumer 1
   ```

   Each group will have its own copy of the data, allowing independent processing.


The following image shows how messages are partitioned and consumed by different consumer groups:

![](https://github.com/Minhaz00/Kafka-NodeJS/blob/main/images/image-2.png?raw=true)


In the producer, input "rider name" and "location" (`north` or `south`) to send location updates.


## Conclusion

This Kafka Node.js project demonstrates the foundational architecture of an event-driven system, showcasing how Kafka producers, consumers, and topics interact to enable scalable message processing. With Kafka's dynamic load balancing and consumer group capabilities, this project serves as a solid starting point for understanding distributed systems and real-time data streaming.