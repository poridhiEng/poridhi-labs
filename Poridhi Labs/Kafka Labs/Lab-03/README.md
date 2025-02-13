# Consumer Groups in Apache Kafka

## Introduction

This lab will help you to get the idea of Consumer Groups, an important topic of Kafka faced while working with multiple partitions of Topics and Consumers.

## Table of Contents

1. What is Consumer groups?
2. Setting up Docker for Kafka
3. Setting up Kafka
4. Monitoring
5. Starting Kafka Server
6. Building using Docker

## What is Consumer groups?

A **consumer group** is a collection of consumer instances that work together to consume messages from one or more Kafka topics in parallel. Consumer groups allow for scalable and fault-tolerant message consumption. 

It works as parallel consumption so that if one of the consumer fails, another consumer will take it’s place to give a unpaused experience to the users. Also if a new consumer is added to the group Kafka will rebalance its partitions among the remaining consumers.

![image01.svg](https://raw.githubusercontent.com/nakibworkspace/kafkalab/171d3c957c5ad874ad73edc26bec0411f6bae23e/Kafka-Labs/Lab-03/images/image01.svg)


## Project Structure
```
project_directory/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── kafka_consumer_groups.py
```

## Setting up Docker for Kafka

- Docker-compose file

```python
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  kafka-app:
    build: .
    depends_on:
      - kafka
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
```

- Dockerfile

```python
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["python", "kafka_consumer_groups.py"]
```

- requirements.txt

```python
kafka-python==2.0.2
```

## Setting Up Kafka

- Importing the necessary libraries

```python
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
```

- Configuring the Kafka Server

```python
BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092').split(',')
TOPIC_NAME = 'test-topic'
GROUP_ID = 'test-consumer-group'
NUM_PARTITIONS = 3
REPLICATION_FACTOR = 1
```

- Waiting for Kafka to get started with Docker

```python
def wait_for_kafka():
    """Wait for Kafka to become available"""
    admin_client = None
    while True:
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)
            break
        except Exception as e:
            print("Waiting for Kafka to become available...")
            time.sleep(3)
    return admin_client
```

- Creating the Topic

```python
def create_topic():
    """Create a topic with multiple partitions"""
    admin_client = wait_for_kafka()
    
    topic = NewTopic(
        name=TOPIC_NAME,
        num_partitions=NUM_PARTITIONS,
        replication_factor=REPLICATION_FACTOR
    )
    
    try:
        admin_client.create_topics([topic])
        print(f"Created topic {TOPIC_NAME} with {NUM_PARTITIONS} partitions")
    except TopicAlreadyExistsError:
        print(f"Topic {TOPIC_NAME} already exists")
    finally:
        admin_client.close()
```

- Creating Producer

```python
def produce_messages():
    """Produce sample messages to the topic"""
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    for i in range(20):
        message = {'message_id': i, 'content': f'Message {i}'}
        producer.send(TOPIC_NAME, value=message)
        time.sleep(0.5)  # Slow down message production for demonstration
    
    producer.close()
```

- Creating Consumer

```python
def start_consumer(consumer_id):
    """Start a consumer instance"""
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    print(f"Consumer {consumer_id} started")
    try:
        while True:
            # Poll for messages
            messages = consumer.poll(timeout_ms=1000)
            
            for partition in messages:
                for message in messages[partition]:
                    print(f"Consumer {consumer_id} | "
                          f"Partition: {message.partition} | "
                          f"Offset: {message.offset} | "
                          f"Message: {message.value}")
    except KeyboardInterrupt:
        print(f"Consumer {consumer_id} stopping...")
    finally:
        consumer.close()

```

## Monitoring Consumer Group

```python
def monitor_consumer_group():
    """Monitor consumer group status"""
    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=None  # No group_id for admin client
    )
    
    while True:
        # Get consumer group information
        group_info = consumer.describe_consumer_groups([GROUP_ID])[0]
        members = group_info.members
        
        print("\nConsumer Group Status:")
        print(f"State: {group_info.state}")
        print(f"Number of members: {len(members)}")
        
        for member in members:
            assignment = member.member_metadata
            print(f"Member {member.member_id}:")
            print(f"  Client ID: {member.client_id}")
            print(f"  Host: {member.host}")
        
        time.sleep(5)
```

##Starting the Kafka server

```python
def main():
    # Create topic
    create_topic()
    
    # Start monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_consumer_group, daemon=True)
    monitor_thread.start()
    
    # Start producer in a separate thread
    producer_thread = threading.Thread(target=produce_messages, daemon=True)
    producer_thread.start()
    
    # Start multiple consumers using a thread pool
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(3):
            executor.submit(start_consumer, i)

if __name__ == "__main__":
    main()
```

## Build and starting the docker containers

```python
docker-compose up --build
```
![Screenshot 2025-02-09 at 08.09.29.png](https://github.com/nakibworkspace/kafkalab/blob/main/Kafka-Labs/Lab-03/images/image02.png?raw=true)


To scale the numbers of consumer instances

```python
docker-compose up --scale kafka-app=3
```

Additional Monitoring tools using CLI

```bash
#List of consumer groups
[kafka-consumer-groups.sh](http://kafka-consumer-groups.sh/) --bootstrap-server localhost:9092 --list

#Describing a specific consumer group
[kafka-consumer-groups.sh](http://kafka-consumer-groups.sh/) --bootstrap-server localhost:9092 --describe --group test-consumer-group
```

Shutting down the docker containers

```python
docker-compose down
```

