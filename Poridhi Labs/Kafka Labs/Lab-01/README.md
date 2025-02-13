# Introduction to Apache Kafka
## What is Apache Kafka?

Apache Kafka is a distributed streaming platform that enables building the real-time data processing pipelines and streaming platform. 

## Why use Kafka?

Kafka is used for real-time streaming, messaging and event-driven architectures. Other than that it has high-throughput, fault-tolerance and distributed system, which helps to process big data to store in a database like PostgresDB, MongoDB etc. Kafka tracks was being consumed using consumer offset store within kafka itself, for which  consumer can resume it’s processing where it was left off.

## Architecture of Apache Kafka

![kafka.svg](https://raw.githubusercontent.com/nakibworkspace/kafkalab/1b35000171cdb84e3badee3db6833281c7b5aaef/Kafka-Labs/Lab-01/images/image1.svg)

## Components of Kafka

Apache Kafka consists of the following components

### Producers

Application to produce Kafka message. It produces and send it to the partitions as randomly and it will sent to a given location if key is determined.

![producers.svg](https://raw.githubusercontent.com/nakibworkspace/kafkalab/1b35000171cdb84e3badee3db6833281c7b5aaef/Kafka-Labs/Lab-01/images/image2.svg)

### Messages

**Headers** carries metadata

**Key** for organisation

**Value** actual deploy payload

![message.svg](https://raw.githubusercontent.com/nakibworkspace/kafkalab/1b35000171cdb84e3badee3db6833281c7b5aaef/Kafka-Labs/Lab-01/images/image3.svg)

### Kafka Clusters 

is a group of interconnected Kafka Brokers that works together to handle messages processing, storage, and distribution. A cluster provides **scalability, fault tolerance, and high availability**.

If one broker fails, another one will take over to maintain it’s scalability and distribute the loads of data streaming.

### Brokers

Kafka runs in a cluster of brokers to distribute the load. It is basically responsible for handling read and write requests, storing message data, and ensuring fault tolerance.

![broker.svg](https://raw.githubusercontent.com/nakibworkspace/kafkalab/1b35000171cdb84e3badee3db6833281c7b5aaef/Kafka-Labs/Lab-01/images/image4.svg)

### Topics & Partitions

A logical channel to which messages are sent. Topics are splitted into partitions for enabling parallel processing and scalability. Also topics are logical partitioning of the messages. So for the specific topics are made for different database over types of the data.

Partitions are mainly happen in the Topics where the datas are distributed by depending over various types of conditions and parameters.

### Consumers

Reads message from Kafka topics

## Issues with Partitions and Consumers

Each consumer in a group will reads from a unique partition

If there’s more partitions than consumers, some consumers will read from multiple partitions.

If more consumers than the partitions, some consumer will sit idle.

Consumer groups allow consumption and fault tolerance (if one consumer fails, another one will take over)

![consumer.svg](https://raw.githubusercontent.com/nakibworkspace/kafkalab/1b35000171cdb84e3badee3db6833281c7b5aaef/Kafka-Labs/Lab-01/images/image5.svg)

### Zookeeper

Used to manage metadata, leader election and cluster state

## How Kafka works?

1. The Producers creates messages, from various sources for streaming messages and sends it to the Kafka Clusters randomly or by following keys to definitive Broker.
2. The Brokers takes all the messages and then divides them into multiple partitions following conditions.
3. The Consumers receives messages from single or multiple brokers and then use it as needed for further.