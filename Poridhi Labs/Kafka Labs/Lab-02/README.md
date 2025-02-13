# Setting up Apache Kafka with Docker

## Introduction

This lab gives us an overview on how can we setup Apache Kafka with Docker by creating a very simple Producer and Consumer from scratch.

## Table of Contents

1. Create a docker-compose.yml file
2. Creating a Producer
3. Creating a Consumer
4. Setting up
5. Testing
6. Cleanup

### Creating a docker-compose.yml file

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
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

### Creating a Producer which will write messages to Kafka

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send sample message
producer.send('test_topic', {'message': 'Hello Kafka!'})
producer.flush()
```

### Creating a Consumer to read messages from Kafka

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    print(f"Received: {message.value}")
```

### Requirements.txt file

```python
kafka-python==2.0.2
```

### Setting up

- Start Kafka Cluster using the docker compose file
    
    ```bash
    docker-compose up -d
    ```
    

this will expose the Kafka Broker in localhost:9092

- Creating virtual environment
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    

- Installing dependencies
    
    ```bash
    pip install -r requirements.txt
    ```
    

- Run the Consumer in one terminal
    
    ```bash
    python [consumer.py](http://consumer.py/)
    ```
    
- Run Producer in another terminal
    
    ```bash
    python [producer.py](http://producer.py/)
    ```
    

### Testing
    1. The producer will send a message: `{'message': 'Hello Kafka!'}`
    2. The consumer should receive and print the message
    3. Check container status: `docker-compose ps`
    4. View logs: `docker-compose logs`

### Cleanup
    
    ```bash
    docker-compose down
    ```
    

