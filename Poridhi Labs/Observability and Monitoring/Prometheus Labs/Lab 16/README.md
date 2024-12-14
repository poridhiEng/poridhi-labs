# Prometheus Histograms and Summaries

This lab provides hands-on experience with Prometheus histograms and summaries using a Node.js/Express application. 

In Prometheus, **histograms** and **summaries** are two powerful types of metrics used to measure the distribution of values over time, such as the duration of requests, response sizes, or even memory usage.

### **Histograms**
A histogram breaks down observed values into predefined "buckets." For example, if we're measuring the response time of API requests, we could create buckets for requests that take less than 0.1 seconds, less than 0.5 seconds, 1 second, and so on. Prometheus counts how many requests fall into each of these buckets over time. This setup allows you to analyze and visualize trends in response times or other metrics and calculate quantiles (like the 95th percentile) to show how the values are distributed.

- **Example**: If you want to see how many requests take less than 1 second versus how many take more, you could set up histogram buckets to track the distribution.
- **Benefits**: Histograms can be aggregated across multiple instances, making them ideal for metrics where you need to analyze patterns or trends across distributed systems.

### **Summaries** 
A summary metric, on the other hand, directly calculates quantiles on each instance itself, without needing predefined buckets. Instead, it’s configured with target percentiles, such as the 50th, 90th, or 99th percentiles, which represent the point at which a certain percentage of requests fall below. Summaries are better for highly accurate percentile tracking within a single instance, but they can’t be aggregated across instances like histograms.

   - **Example**: If you want to monitor the exact 95th percentile of request duration, a summary can capture this precisely on each instance.
   - **Benefits**: Summaries are more precise than histograms for single-instance data but can’t be combined across multiple instances.

By the end of this lab, you’ll be able to see how each metric type works, learn when to use one over the other, and configure them in an application to capture valuable performance data.


## Task Description
In this lab, you'll set up a Node.js application to expose Prometheus metrics and configure both `histogram` and `summary` metrics to monitor request durations. You'll then use Docker to run Prometheus and collect these metrics from your app. Finally, you'll generate traffic to your app and use the Prometheus UI to analyze and compare the collected data, gaining hands-on experience with both metric types.

## **Setting Up the Express Service**

### 1. **Initialize Project**
   Start by creating a new project directory and installing the required packages.

   ```bash
   mkdir prometheus-metrics-lab
   cd prometheus-metrics-lab
   npm init -y
   npm install express prom-client
   ```

### 2. **Create the Application File**

   In the project root, create `app.js` and add the following code:

   ```javascript
   const express = require('express');
   const client = require('prom-client');
   const app = express();

   // Register metrics
   const register = new client.Registry();
   client.collectDefaultMetrics({ register });

   // Histogram setup
   const httpRequestDurationHistogram = new client.Histogram({
       name: 'http_request_duration_seconds',
       help: 'Duration of HTTP requests in seconds histogram',
       labelNames: ['method', 'route'],
       buckets: [0.1, 0.5, 1, 2, 5]
   });

   // Summary setup
   const httpRequestDurationSummary = new client.Summary({
       name: 'http_request_duration_summary_seconds',
       help: 'Duration of HTTP requests in seconds summary',
       labelNames: ['method', 'route'],
       percentiles: [0.5, 0.9, 0.95, 0.99]
   });

   register.registerMetric(httpRequestDurationHistogram);
   register.registerMetric(httpRequestDurationSummary);

   app.use((req, res, next) => {
       const start = process.hrtime();
       res.on('finish', () => {
           const duration = process.hrtime(start);
           const durationSeconds = duration[0] + duration[1] / 1e9;
           httpRequestDurationHistogram.labels(req.method, req.route?.path || req.path).observe(durationSeconds);
           httpRequestDurationSummary.labels(req.method, req.route?.path || req.path).observe(durationSeconds);
       });
       next();
   });

   // Endpoint for Prometheus metrics
   app.get('/metrics', async (req, res) => {
       res.setHeader('Content-Type', register.contentType);
       res.send(await register.metrics());
   });

   // Additional endpoints for testing
   app.get('/fast', (req, res) => res.json({ message: 'Fast response' }));
   app.get('/medium', (req, res) => setTimeout(() => res.json({ message: 'Medium response' }), 500));
   app.get('/slow', (req, res) => setTimeout(() => res.json({ message: 'Slow response' }), 2000));

   const PORT = 3000;
   app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
   ```

Here's a simplified explanation for this code:

1. **Set Up Express Server**:
   - We create an Express server using `express()`, which will handle HTTP requests.

2. **Prometheus Client Library**:
   - The `prom-client` library is used to create and manage metrics that Prometheus can scrape.

3. **Metrics Registration**:
   - We set up a **Registry** (`register`) to store all our metrics and enable default metrics (like memory usage, CPU, etc.).

4. **Histogram and Summary Metrics**:
   - We define two metrics:
     - **Histogram** (`httpRequestDurationHistogram`): Measures request duration and sorts them into "buckets" based on predefined time intervals (0.1s, 0.5s, 1s, etc.).
     - **Summary** (`httpRequestDurationSummary`): Measures request duration and calculates specific percentiles (50th, 90th, etc.) to show how fast most requests are handled.

5. **Middleware for Measuring Request Duration**:
   - We use middleware to track how long each request takes:
     - `process.hrtime()` records the start time.
     - After the request finishes, we calculate the duration and log it in both the histogram and summary metrics.

6. **Metrics Endpoint**:
   - We create an endpoint (`/metrics`) that returns all metrics data in a format Prometheus understands, so it can scrape and collect the metrics.

7. **Test Endpoints with Different Response Times**:
   - We define three endpoints (`/fast`, `/medium`, `/slow`) that respond with different delays to simulate varied processing times. This lets us test how the histogram and summary metrics capture request duration.

8. **Run the Server**:
   - The server listens on port 3000, ready to handle requests and expose metrics at `/metrics` for Prometheus to scrape. 

This code allows us to monitor request duration patterns in Prometheus, giving insights into how long each request takes.

## **Configuring Prometheus**

### 1. **Create Prometheus Configuration**

   In the project root, create a `prometheus.yml` file for setting up Prometheus to scrape metrics from the Express app.

   ```yaml
   global:
     scrape_interval: 15s

   scrape_configs:
     - job_name: 'express-app'
       static_configs:
         - targets: ['host.docker.internal:3000']
   ```

   - **Scrape Interval**: Sets Prometheus to scrape metrics every 15 seconds.
   - **Target Configuration**: Configures Prometheus to scrape the Express app’s `/metrics` endpoint on port 3000.

### 2. **Set Up Docker Compose**

   Create a `docker-compose.yml` file to start Prometheus with this configuration:

   ```yaml
   version: '3'
   services:
     prometheus:
       image: prom/prometheus:latest
       ports:
         - "9090:9090"
       volumes:
         - ./prometheus.yml:/etc/prometheus/prometheus.yml
       extra_hosts:
         - "host.docker.internal:host-gateway"
   ```

   - **Prometheus Container**: Exposes Prometheus on port `9090` and loads the `prometheus.yml` configuration.
   - **Docker Network Configuration**: `host.docker.internal` enables Docker to access local network services.



## **Running the service and prometheus**

### 1. **Start the Express Application**

   Run the Express server:

   ```bash
   node app.js
   ```

### 2. **Start Prometheus**

   Launch Prometheus with Docker Compose:

   ```bash
   docker-compose up
   ```

### 3. **Generate Traffic**

   Use `curl` or Postman to test endpoints and generate sample metrics:

   ```bash
   curl http://localhost:3000/fast
   curl http://localhost:3000/medium
   curl http://localhost:3000/slow
   ```



## **Visualizing Metrics in Prometheus**

### 1. **Access Prometheus**

   Open `http://localhost:9090` in your browser to access the Prometheus UI.

### 2. **Query Histogram Metrics**

   - **Basic Histogram Data**: Shows all histogram data for request durations.
     ```prometheus
     http_request_duration_seconds_bucket
     ```

     ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2016/images/image-1.png?raw=true)

   - **Rate of Requests**: Calculates the request rate over the last 5 minutes.
     ```prometheus
     rate(http_request_duration_seconds_bucket[5m])
     ```

     ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2016/images/image-2.png?raw=true)

   - **Quantile Calculation (95th Percentile)**: Visualizes the 95th percentile of request durations.
     ```prometheus
     histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
     ```

     ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2016/images/image-3.png?raw=true)

### 3. **Query Summary Metrics**

   - **Basic Summary Data**: Fetches all summary data for request durations.
     ```prometheus
     http_request_duration_summary_seconds
     ```

     ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2016/images/image-4.png?raw=true)

   - **Quantile (95th Percentile)**: Shows the 95th percentile of request durations as calculated in the summary.
     ```prometheus
     http_request_duration_summary_seconds{quantile="0.95"}
     ```

     ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2016/images/image-5.png?raw=true)



## **Understanding Histograms vs. Summaries**

### Histograms
   - **Buckets**: Observations are grouped into predefined intervals, allowing analysis of data distribution.
   - **Aggregatable**: Histograms can be aggregated across multiple instances, making them ideal for distributed systems.
   - **Use Cases**: Request durations, response sizes.

### Summaries
   - **Quantiles**: Summaries calculate percentiles based on individual instance observations.
   - **Instance-Specific**: Better suited for single-instance scenarios, as summaries cannot be aggregated across instances.
   - **Use Cases**: Memory usage, application-specific metrics.

**Key Differences**:
   - **Aggregation**: Histograms aggregate across instances, while summaries are instance-specific.
   - **Configuration**: Histograms use buckets; summaries use quantiles.
   - **Resource Usage**: Summaries require more memory and CPU to maintain precise quantiles.


## **Conclusion**

This lab has demonstrated how to:
- Implement Prometheus histograms and summaries in an Express.js app.
- Use Prometheus UI to visualize and analyze these metrics.
- Understand the unique characteristics of histograms and summaries for different use cases.

This foundational knowledge will help you build observability into your applications and make informed choices between metric types based on your system’s needs.