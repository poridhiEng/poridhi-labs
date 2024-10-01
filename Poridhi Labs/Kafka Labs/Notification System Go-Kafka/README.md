
# Real-Time Notification System with Go and Kafka

In this tutorial, you will learn how to integrate **Apache Kafka** with **Go** to build a real-time notification system. By leveraging Kafka’s event streaming capabilities and Go’s concurrency features, you'll see how to efficiently manage and process live data streams. 

## What is Kafka? 🤔

Apache Kafka is a **distributed event streaming platform** that was initially developed by LinkedIn and later open-sourced through the Apache Software Foundation. It is now a leading tool for processing real-time data streams, used by companies like Uber, Netflix, and LinkedIn for handling large-scale, real-time event streaming.

![](https://github.com/Minhaz00/Notification-System-Go-Kafka/blob/main/images/image-3.png?raw=true)

### Kafka’s Role in Real-Time Systems
Kafka acts as an **event broker** that enables applications to communicate by producing and consuming messages (events) in real time. In this context, an "event" is simply a record of something happening, such as a user action or system event. Kafka is designed to handle high throughput and low latency, making it ideal for scenarios that require constant updates, such as notifications, logging, or stream processing.

Kafka's **key benefits** include:
- **Durability**: Kafka ensures that no data is lost, even if components fail.
- **Scalability**: Kafka is designed to scale horizontally across many servers.
- **Fault-tolerance**: Kafka can handle node failures, ensuring continuous data availability.

### Kafka’s Core Components ⚙️

1. **Events**: A message representing a change or action. Example: “Bruno started following you.”
2. **Brokers**: Servers running Kafka that store and manage events.
3. **Topics**: Categories in Kafka where messages are stored, akin to folders in a filesystem.
4. **Producers**: Entities that send messages to Kafka topics.
5. **Consumers**: Entities that read and process messages from Kafka topics.
6. **Partitions**: Subdivisions within topics that enable Kafka to manage data across different brokers.
7. **Consumer Groups**: A group of consumers working together to process messages from different partitions.
8. **Replicas**: Multiple copies of data across brokers to ensure fault tolerance.


## Task Description

In this tutorial, we will create a **real-time notification** system where:

1. `Producers` will generate events (notifications) when a user performs an action (like following another user).

2. Kafka will act as a `broker`, storing and handling these events in real-time.

3. `Consumers` will listen for new events and process them, sending out notifications to the appropriate users.

You'll set up a Kafka producer to publish notification messages, and a Kafka consumer to read and process these messages as they arrive. By the end of this tutorial, you’ll have a complete real-time system that demonstrates how to use Kafka and Go together for event-driven systems.

## **Project Workspace Setup**

### Step 1: Install Go

```bash
# 1. Download Go and extract it in one step
wget -qO- https://dl.google.com/go/go1.23.1.linux-amd64.tar.gz | sudo tar -C /usr/local -xzf -
```
```bash
# 2. Add Go to PATH
echo 'export PATH=$PATH:/usr/local/go/bin' >> $HOME/.profile
```
```bash
# 3. Apply changes
source $HOME/.profile
```
```bash
# 4. Verify Go installation
go version
```


### Step 2: Create the Project Directory

Create a new project directory named `kafka-notify`:

```bash
mkdir kafka-notify && cd kafka-notify
```

### Step 3: Set Up Kafka Using Docker
Use **Bitnami's** Kafka Docker image for a hassle-free setup:

```bash
curl -sSL https://raw.githubusercontent.com/bitnami/containers/main/bitnami/kafka/docker-compose.yml > docker-compose.yml
```

### Step 4: Modify Kafka Configuration
Before starting the Kafka broker, edit the `docker-compose.yml` file. Find the following line:

```
KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://:9092
```

Replace it with:

```
KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
```

This ensures Kafka advertises its listener on `localhost`, making it easier for the Go application to connect.

### Step 5: Start Kafka
Start the Kafka broker with Docker:

```bash
docker-compose up -d
```

### Step 6: Organize the Project Structure
Create directories for the producer, consumer, and models:

```bash
mkdir -p cmd/producer cmd/consumer pkg/models
```

### Step 7: Initialize the Go Module and Install Dependencies
Initialize a Go module for the project and install external packages **sarama** (Kafka client library) and **gin** (web framework):

```bash
go mod init kafka-notify
go get github.com/IBM/sarama github.com/gin-gonic/gin
```

## **Creating Models**

### **Step 1: Define User and Notification Models**
Navigate to the `pkg/models` directory and create the `models.go` file:

```go
package models

type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

type Notification struct {
    From    User   `json:"from"`
    To      User   `json:"to"`
    Message string `json:"message"`
}
```



## **Setting Up the Kafka Producer**

### **Step 1: Create the Producer Logic**
In the `cmd/producer` directory, create the `producer.go` file. This will define the Kafka producer and the API endpoint that sends notifications:

```go
package main

import (
    "encoding/json"
    "errors"
    "fmt"
    "log"
    "net/http"
    "strconv"

    "kafka-notify/pkg/models"

    "github.com/IBM/sarama"
    "github.com/gin-gonic/gin"
)

const (
    ProducerPort       = ":5001"
    KafkaServerAddress = "localhost:9092"
    KafkaTopic         = "notifications"
)

// ============== HELPER FUNCTIONS ==============
var ErrUserNotFoundInProducer = errors.New("user not found")

func findUserByID(id int, users []models.User) (models.User, error) {
    for _, user := range users {
        if user.ID == id {
            return user, nil
        }
    }
    return models.User{}, ErrUserNotFoundInProducer
}

func getIDFromRequest(formValue string, ctx *gin.Context) (int, error) {
    id, err := strconv.Atoi(ctx.PostForm(formValue))
    if err != nil {
        return 0, fmt.Errorf(
            "failed to parse ID from form value %s: %w", formValue, err)
    }
    return id, nil
}

// ============== KAFKA RELATED FUNCTIONS ==============
func sendKafkaMessage(producer sarama.SyncProducer,
    users []models.User, ctx *gin.Context, fromID, toID int) error {
    message := ctx.PostForm("message")

    fromUser, err := findUserByID(fromID, users)
    if err != nil {
        return err
    }

    toUser, err := findUserByID(toID, users)
    if err != nil {
        return err
    }

    notification := models.Notification{
        From: fromUser,
        To:   toUser, Message: message,
    }

    notificationJSON, err := json.Marshal(notification)
    if err != nil {
        return fmt.Errorf("failed to marshal notification: %w", err)
    }

    msg := &sarama.ProducerMessage{
        Topic: KafkaTopic,
        Key:   sarama.StringEncoder(strconv.Itoa(toUser.ID)),
        Value: sarama.StringEncoder(notificationJSON),
    }

    _, _, err = producer.SendMessage(msg)
    return err
}

func sendMessageHandler(producer sarama.SyncProducer,
    users []models.User) gin.HandlerFunc {
    return func(ctx *gin.Context) {
        fromID, err := getIDFromRequest("fromID", ctx)
        if err != nil {
            ctx.JSON(http.StatusBadRequest, gin.H{"message": err.Error()})
            return
        }

        toID, err := getIDFromRequest("toID", ctx)
        if err != nil {
            ctx.JSON(http.StatusBadRequest, gin.H{"message": err.Error()})
            return
        }

        err = sendKafkaMessage(producer, users, ctx, fromID, toID)
        if errors.Is(err, ErrUserNotFoundInProducer) {
            ctx.JSON(http.StatusNotFound, gin.H{"message": "User not found"})
            return
        }
        if err != nil {
            ctx.JSON(http.StatusInternalServerError, gin.H{
                "message": err.Error(),
            })
            return
        }

        ctx.JSON(http.StatusOK, gin.H{
            "message": "Notification sent successfully!",
        })
    }
}

func setupProducer() (sarama.SyncProducer, error) {
    config := sarama.NewConfig()
    config.Producer.Return.Successes = true
    producer, err := sarama.NewSyncProducer([]string{KafkaServerAddress},
        config)
    if err != nil {
        return nil, fmt.Errorf("failed to setup producer: %w", err)
    }
    return producer, nil
}

func main() {
    users := []models.User{
        {ID: 1, Name: "Emma"},
        {ID: 2, Name: "Bruno"},
        {ID: 3, Name: "Rick"},
        {ID: 4, Name: "Lena"},
    }

    producer, err := setupProducer()
    if err != nil {
        log.Fatalf("failed to initialize producer: %v", err)
    }
    defer producer.Close()

    gin.SetMode(gin.ReleaseMode)
    router := gin.Default()
    router.POST("/send", sendMessageHandler(producer, users))

    fmt.Printf("Kafka PRODUCER 📨 started at http://localhost%s\n",
        ProducerPort)

    if err := router.Run(ProducerPort); err != nil {
        log.Printf("failed to run the server: %v", err)
    }
}
```

Let’s break down the Kafka-related components within the code:

### **Within the `setupProducer()` function:**

- **`config := sarama.NewConfig()`**: This initializes a new default configuration object for the Kafka producer. This is akin to setting up all the necessary parameters before the Kafka client connects to the broker.
  
- **`config.Producer.Return.Successes = true`**: This configures the producer to receive an acknowledgment after the message has been successfully written to the Kafka topic. Without this, you wouldn't know whether the message was successfully sent, as Kafka can operate in fire-and-forget mode by default.

- **`producer, err := sarama.NewSyncProducer([...])`**: This creates a **synchronous Kafka producer** that connects to the broker located at the specified address (`localhost:9092`). A synchronous producer waits for an acknowledgment from Kafka before proceeding, ensuring that the message was successfully stored in the specified topic.

### **Inside the `sendKafkaMessage()` function:**

- The function begins by extracting the **message content** from the HTTP request’s context, and then it tries to find both the **sender** (`fromUser`) and **recipient** (`toUser`) based on the provided IDs.

- **`notification := models.Notification{...}`**: This creates a **Notification** struct containing details about the sender, recipient, and the actual message. This struct will be serialized and sent as the Kafka message content.

- **`notificationJSON, err := json.Marshal(notification)`**: Here, the **Notification** struct is converted into a JSON string. This makes it suitable for transmission, as Kafka messages are typically sent in JSON format to ensure consistency and ease of deserialization on the consumer side.

- **`msg := &sarama.ProducerMessage{...}`**: This constructs a **ProducerMessage**, which will be sent to Kafka. The key is set to the recipient's ID, which can be used for message partitioning within Kafka, and the value is the serialized **Notification** (the JSON string).

- **`producer.SendMessage(msg)`**: This line sends the constructed message to the **Kafka broker**. The message is added to the "notifications" topic. If successful, the function will return `nil`; otherwise, it will return an error.

### **In the `sendMessageHandler()` function:**

- This function acts as a **handler** for the `/send` endpoint. It listens for incoming **POST requests**, extracts the sender (`fromID`) and recipient (`toID`) IDs, and ensures that they are valid integers.

- Once it has the IDs, it calls **`sendKafkaMessage()`** to process the Kafka message. Based on the outcome, it responds to the client with different HTTP status codes:
    - **404 Not Found**: If either the sender or the recipient is not found.
    - **400 Bad Request**: If the provided IDs are invalid.
    - **500 Internal Server Error**: For any other unexpected errors, returning the exact error message to help with debugging.

### **Finally, within the `main()` function:**

- **Producer Initialization**: A Kafka producer is initialized using the `setupProducer()` function, setting up the connection with the Kafka broker.

- **Gin Router Setup**: A **Gin web server** is started using `gin.Default()`. This sets up a basic web server capable of handling HTTP requests.

- **Endpoint Definition**: A POST route `/send` is defined, which allows clients to send notifications. This route is handled by the `sendMessageHandler()` function, which takes care of validating the request, constructing the Kafka message, and sending it.

- **Server Start**: The web server is started on port **8080** (`ProducerPort`). When a client sends a request to `/send`, the server processes it and produces a Kafka message to the "notifications" topic.




## **Setting Up the Kafka Consumer**

### **Step 1: Create the Consumer Logic**
In the `cmd/consumer` directory, create the `consumer.go` file. This will define the Kafka consumer and the API endpoint that retrieves notifications:

```go
package main

import (
    "context"
    "encoding/json"
    "errors"
    "fmt"
    "log"
    "net/http"
    "sync"

    "kafka-notify/pkg/models"

    "github.com/IBM/sarama"
    "github.com/gin-gonic/gin"
)

const (
    ConsumerGroup      = "notifications-group"
    ConsumerTopic      = "notifications"
    ConsumerPort       = ":5002"
    KafkaServerAddress = "localhost:9092"
)

// ============== HELPER FUNCTIONS ==============
var ErrNoMessagesFound = errors.New("no messages found")

func getUserIDFromRequest(ctx *gin.Context) (string, error) {
    userID := ctx.Param("userID")
    if userID == "" {
        return "", ErrNoMessagesFound
    }
    return userID, nil
}

// ====== NOTIFICATION STORAGE ======
type UserNotifications map[string][]models.Notification

type NotificationStore struct {
    data UserNotifications
    mu   sync.RWMutex
}

func (ns *NotificationStore) Add(userID string,
    notification models.Notification) {
    ns.mu.Lock()
    defer ns.mu.Unlock()
    ns.data[userID] = append(ns.data[userID], notification)
}

func (ns *NotificationStore) Get(userID string) []models.Notification {
    ns.mu.RLock()
    defer ns.mu.RUnlock()
    return ns.data[userID]
}

// ============== KAFKA RELATED FUNCTIONS ==============
type Consumer struct {
    store *NotificationStore
}

func (*Consumer) Setup(sarama.ConsumerGroupSession) error   { return nil }
func (*Consumer) Cleanup(sarama.ConsumerGroupSession) error { return nil }

func (consumer *Consumer) ConsumeClaim(
    sess sarama.ConsumerGroupSession, claim sarama.ConsumerGroupClaim) error {
    for msg := range claim.Messages() {
        userID := string(msg.Key)
        var notification models.Notification
        err := json.Unmarshal(msg.Value, &notification)
        if err != nil {
            log.Printf("failed to unmarshal notification: %v", err)
            continue
        }
        consumer.store.Add(userID, notification)
        sess.MarkMessage(msg, "")
    }
    return nil
}

func initializeConsumerGroup() (sarama.ConsumerGroup, error) {
    config := sarama.NewConfig()

    consumerGroup, err := sarama.NewConsumerGroup(
        []string{KafkaServerAddress}, ConsumerGroup, config)
    if err != nil {
        return nil, fmt.Errorf("failed to initialize consumer group: %w", err)
    }

    return consumerGroup, nil
}

func setupConsumerGroup(ctx context.Context, store *NotificationStore) {
    consumerGroup, err := initializeConsumerGroup()
    if err != nil {
        log.Printf("initialization error: %v", err)
    }
    defer consumerGroup.Close()

    consumer := &Consumer{
        store: store,
    }

    for {
        err = consumerGroup.Consume(ctx, []string{ConsumerTopic}, consumer)
        if err != nil {
            log.Printf("error from consumer: %v", err)
        }
        if ctx.Err() != nil {
            return
        }
    }
}

func handleNotifications(ctx *gin.Context, store *NotificationStore) {
    userID, err := getUserIDFromRequest(ctx)
    if err != nil {
        ctx.JSON(http.StatusNotFound, gin.H{"message": err.Error()})
        return
    }

    notes := store.Get(userID)
    if len(notes) == 0 {
        ctx.JSON(http.StatusOK,
            gin.H{
                "message":       "No notifications found for user",
                "notifications": []models.Notification{},
            })
        return
    }

    ctx.JSON(http.StatusOK, gin.H{"notifications": notes})
}

func main() {
    store := &NotificationStore{
        data: make(UserNotifications),
    }

    ctx, cancel := context.WithCancel(context.Background())
    go setupConsumerGroup(ctx, store)
    defer cancel()

    gin.SetMode(gin.ReleaseMode)
    router := gin.Default()
    router.GET("/notifications/:userID", func(ctx *gin.Context) {
        handleNotifications(ctx, store)
    })

    fmt.Printf("Kafka CONSUMER (Group: %s) 👥📥 "+
        "started at http://localhost%s\n", ConsumerGroup, ConsumerPort)

    if err := router.Run(ConsumerPort); err != nil {
        log.Printf("failed to run the server: %v", err)
    }
}
```

Let's break down the Kafka consumer-related components in this code:

### **Within the `main()` function:**

- **`consumerStore := &NotificationStore{data: make(UserNotifications)}`**: A **`NotificationStore`** is initialized, which will store user notifications. This store is thread-safe, utilizing a **read-write mutex** (`sync.RWMutex`) to manage concurrent access to the stored notifications.

- **`consumerGroup, err := setupConsumer()`**: The **`setupConsumer()`** function sets up the **Kafka consumer group**. This group subscribes to a Kafka topic ("notifications") and receives messages from that topic.

    - Inside **`setupConsumer()`**:
        - **`config := sarama.NewConfig()`**: Creates a default Kafka consumer configuration.
        - **`config.Consumer.Group.Rebalance.Strategy = sarama.BalanceStrategyRoundRobin`**: This specifies that the **RoundRobin balancing strategy** will be used to distribute messages evenly across consumers within the group.
        - **`config.Consumer.Offsets.Initial = sarama.OffsetNewest`**: This tells the consumer to start reading from the **newest available offset** in the topic, meaning it will only consume messages that are produced after the consumer starts.

    - **`sarama.NewConsumerGroup([...])`**: This creates the Kafka consumer group, connecting it to the Kafka broker running at `localhost:9092`. If any error occurs during the setup, it logs a failure.

- **`go func() {...}`**: The consumer runs inside a **goroutine**, allowing it to continuously consume messages in the background without blocking the rest of the program. It invokes the **`Consume()`** method, which consumes messages from the Kafka "notifications" topic using the **Consumer** struct.

    - **`consumerGroup.Consume()`**: This is where the consumer starts pulling messages from Kafka. It listens for messages in the "notifications" topic and processes them using the **`Consumer.ConsumeClaim()`** function.

### **Inside the `Consumer.ConsumeClaim()` function:**

- This function is responsible for **processing Kafka messages** that are assigned to this consumer.

- **`for msg := range claim.Messages()`**: This loop reads each message from the **Kafka topic** as it arrives. Each **`msg`** represents a message that contains a key (the `userID`) and a value (the notification message content).

- **`userID := string(msg.Key)`**: The key of the Kafka message is extracted, which represents the **recipient user’s ID**.

- **`json.Unmarshal(msg.Value, &notification)`**: The value (i.e., the notification) is extracted by unmarshalling the JSON payload into a **`models.Notification`** struct. This converts the Kafka message from its JSON format into a usable Go structure.

- **`consumer.store.Add(userID, notification)`**: The newly unmarshalled **notification** is added to the **`NotificationStore`**, indexed by the user ID. The `Add()` method ensures thread-safe access to the notification store using a **write lock**.

- **`sess.MarkMessage(msg, "")`**: Once the message is successfully processed, this line marks the message as consumed, ensuring that Kafka knows the message has been handled, preventing it from being reprocessed.

### **In the `NotificationStore` struct:**

The `NotificationStore` struct is designed to store user notifications in a thread-safe manner:

- **`Add(userID string, notification models.Notification)`**: This function adds a new notification to the store for the specified user. It locks the data with a **write lock** (`mu.Lock()`), appends the notification to the user’s list of notifications, and then unlocks it.

- **`Get(userID string)`**: This function retrieves all notifications for a specific user. It uses a **read lock** (`mu.RLock()`) to ensure that the data is read safely in a concurrent environment, and then unlocks once done.

### **The `getUserNotificationsHandler()` function:**

This is the **HTTP handler** for the `/notifications` endpoint. It handles incoming GET requests and responds with a list of notifications for a specific user:

- **`userID := ctx.Query("userID")`**: The handler retrieves the user ID from the query parameters of the incoming HTTP request.

- **`notifications := store.Get(userID)`**: It fetches the list of notifications for the given user from the **NotificationStore**.

- **Error Handling**: If no notifications are found for the user (`len(notifications) == 0`), the handler responds with a **404 Not Found** error and a message saying "No notifications found."

- **`ctx.JSON(http.StatusOK, gin.H{"notifications": notifications})`**: If notifications exist, the handler returns them in the response as a **JSON object** with a status code of **200 OK**.

### **Putting It All Together:**

- **Kafka Consumer Setup**: The consumer group is configured to subscribe to the **"notifications"** topic. Each message consumed from this topic is processed by the **`Consumer.ConsumeClaim()`** function, which extracts the user ID and notification content, then stores the notification in the **`NotificationStore`**.

- **HTTP Server**: A **Gin web server** is initialized, providing a **/notifications** endpoint where users can query their notifications. When a user requests their notifications by providing their **userID** as a query parameter, the server retrieves the corresponding notifications from the **NotificationStore** and returns them in JSON format.

- **Concurrent Handling**: Kafka consumption and HTTP requests are handled concurrently. While Kafka messages are continuously consumed and stored in the background, the HTTP server responds to user requests for notifications, ensuring real-time availability of the data.




## **Testing the Notification System**

### **Step 1: Run the Producer**
In one terminal, run the producer:

```bash
go run cmd/producer/producer.go
```

### **Step 2: Run the Consumer**
In another terminal, run the consumer:

```bash
go run cmd/consumer/consumer.go
```

![alt text](https://github.com/Minhaz00/Notification-System-Go-Kafka/blob/main/images/image.png?raw=true)

### **Step 3: Send Notifications**
With both producer and consumer running, you can simulate sending notifications. Open up a third terminal and use the below `curl` commands to send notifications:

#### User 1 (Emma) receives a notification from User 2 (Bruno):
```bash
curl -X POST http://localhost:5001/send \
-d "fromID=2&toID=1&message=Bruno started following you."
```

#### User 2 (Bruno) receives a notification from User 1 (Emma):
```
curl -X POST http://localhost:5001/send \
-d "fromID=1&toID=2&message=Emma mentioned you in a comment: Great seeing you yesterday, @Bruno!"
```

#### User 1 (Emma) receives a notification from User 4 (Lena):
```bash
curl -X POST http://localhost:5001/send \
-d "fromID=4&toID=1&message=Lena liked your post: My weekend getaway!"
```

![alt text](https://github.com/Minhaz00/Notification-System-Go-Kafka/blob/main/images/image-1.png?raw=true)

### **Step 4: Retrieve Notifications**
Retrieve notifications for user 2:

```bash
curl http://localhost:5002/notifications/1 | python3 -m json.tool
```

![alt text](https://github.com/Minhaz00/Notification-System-Go-Kafka/blob/main/images/image-2.png?raw=true)

## **Conclusion**
You’ve built a basic real-time notification system using **Go**, **Kafka**, and **Gin**. The producer sends notifications via Kafka, and the consumer listens for them, storing them for later retrieval.

 

Let me know if you need further customization or have any questions!