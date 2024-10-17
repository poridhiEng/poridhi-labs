# Prometheus: Use Cases, Basics, and Architecture

Imagine a scenario where your team is facing server outages from high memory usage and performance slowdowns, so your team requires a proactive monitoring solution. This documentation introduces how Prometheus can help by setting up alerts for memory utilization, analyzing metrics like average file size versus request latency, and understanding its use cases, basics, and architecture to keep your systems running smoothly and efficiently.

![alt text](./images/Prom-Arch.svg)

## What is Prometheus?

Prometheus is an open-source monitoring and alerting toolkit designed to collect, store, and analyze metrics from various services and applications. It is widely used for performance monitoring and alerting due to its scalability and ease of integration with other tools.

- Provides tools to **visualize the collected data**.
- Allows users to configure **alerts** when metrics reach specified thresholds.
- Collects metrics by **scraping targets** that expose data through an **HTTP endpoint**.
- Stores the scraped metrics in a **time series database (TSDB)**.
- Metrics can be queried using **Prometheus' built-in query language (PromQL)**.

## Prometheus Basic Architecture

### Metrics Collection

![alt text](./images/metric-scrap.svg)

- **Scraping Targets:** Prometheus collects metrics by sending HTTP requests to the `/metrics` endpoint of each target. Targets are systems or services that expose metrics in a format Prometheus understands.
- **Time Series Database:** Scraped metrics are stored in a time series database, enabling efficient querying and storage.

### Types of Metrics Monitored

Prometheus is designed to monitor numeric time series data. It can monitor a wide range of metrics, including:

- **System Metrics:** CPU usage, memory utilization, disk space, network I/O.
- **Application Metrics:** Request rates, error rates, latency, number of exceptions.
- **Custom Metrics:** Business-specific metrics exposed via client libraries.

### Metrics Not Suitable for Prometheus

Prometheus is not designed to monitor:

- **Events:** Discrete occurrences without a continuous numeric value.
- **System Logs:** Log files or unstructured log data.
- **Traces:** Distributed tracing data for individual requests.

For these types of data, specialized tools like ELK Stack (for logs) or Jaeger (for tracing) are more appropriate.

### Exporters

**Exporters** are agents that collect metrics from a system and expose them in a format Prometheus can scrape. Since most systems do not natively expose metrics compatible with Prometheus, exporters bridge this gap.

#### Common Exporters

- **Node Exporter:** Collects hardware and OS metrics from Linux kernels.
- **Windows Exporter:** Collects metrics from Windows systems.
- **MySQL Exporter:** Exposes MySQL server metrics.
- **Apache Exporter:** Gathers metrics from Apache HTTP servers.
- **HAProxy Exporter:** Provides metrics from HAProxy load balancers.

### Client Libraries

To monitor application-specific metrics, developers can instrument their code using Prometheus **client libraries**. These libraries enable applications to expose custom metrics via an HTTP endpoint.

#### Supported Languages

- **Go**
- **Java**
- **Python**
- **Ruby**
- **Rust**

#### Use Cases for Client Libraries

- **Application Performance:** Measure request latency, throughput, and error rates.
- **Business Metrics:** Track user sign-ups, purchases, or other domain-specific metrics.
- **Job Execution Times:** Monitor durations of background tasks or batch jobs.

## Pull-Based Model

Prometheus operates on a **pull-based** model:

- **Active Scraping:** Prometheus server periodically scrapes metrics from targets.
- **Target List:** Maintains a list of targets to scrape, either statically configured or dynamically discovered.
- **Centralized Control:** Prometheus controls when and how often metrics are collected.

### Advantages of Pull-Based Model

- **Detection of Down Targets:** Easier to determine if a target is unavailable when it fails to respond to a scrape.
- **Scalability:** Reduces the risk of overloading the Prometheus server since it controls the scraping rate.
- **Security:** Targets do not need to know where to send data, reducing configuration overhead.

### Other Pull-Based Systems

- **Zabbix**
- **Nagios**

## Push-Based Model

In a **push-based** model:

- **Targets Push Metrics:** Targets send metrics data to the monitoring server.
- **Event-Based Systems:** Useful when immediate data is required or for handling events.

### Disadvantages of Push-Based Model

- **Overloading Risk:** The monitoring server can be overwhelmed by too many incoming connections.
- **Unknown Target Status:** Difficult to discern whether a target is down or simply not sending data.

### Examples of Push-Based Systems

- **Logstash**
- **Graphite**
- **OpenTSDB**

## Prometheus and Pushgateway

![alt text](./images/pushgateway.svg)

While Prometheus is primarily pull-based, it provides a **Pushgateway** component for specific scenarios:

- **Short-Lived Jobs:** For jobs that run briefly and may not be running when Prometheus scrapes, they can push metrics to the Pushgateway.
- **Intermediary Storage:** Pushgateway acts as an intermediary, exposing metrics that Prometheus can scrape.

## Use Cases

### 1. Monitoring Server Memory Utilization

**Scenario:** Several outages have occurred due to high memory usage on a server hosting a MySQL database. The operations team wants to be notified via email when memory usage reaches 80% of maximum capacity to take proactive measures.

![alt text](./images/usecase-01.svg)

**Prometheus Solution:**

- **Metric Collection:** Use a **Node Exporter** to collect memory utilization metrics from the server.
- **Alerting:** Configure Prometheus to monitor the `node_memory_Active` metric and set up an alert rule to trigger when memory usage exceeds 80%.
- **Notification:** Integrate Prometheus with Alertmanager to send email notifications to the operations team when the alert condition is met.

### 2. Analyzing Application Performance with Video Uploads

**Scenario:** A new video upload feature has been added to a website. There are concerns about users uploading excessively large videos, potentially degrading application performance. The team needs a chart plotting the average file size of uploads against the average latency per request to identify performance degradation points.

![alt text](./images/usecase-02.svg)

**Prometheus Solution:**

- **Instrumentation:** Use Prometheus client libraries to instrument the application code, exposing metrics for upload file sizes and request latency.
- **Metric Collection:** Configure Prometheus to scrape these custom metrics from the application's `/metrics` endpoint.
- **Visualization:** Utilize Prometheus's querying capabilities or integrate with Grafana to create charts plotting average file size versus average request latency.

## Conclusion

Prometheus provides a robust solution for monitoring and alerting in modern infrastructure environments. Its pull-based model, flexible querying language, and rich ecosystem of exporters and client libraries make it suitable for a wide range of use cases.

