# Communication Between Containers in a Custom Bridge Network

When working with Docker, containers by default are isolated. However, when containers need to communicate with each other, you can connect them to the same Docker network. A **user-defined bridge network** provides more control over how Docker containers communicate compared to the default bridge network. This guide will walk you through setting up a custom bridge network, launching multiple Nginx containers on that network, and verifying communication between them.

![image](./images/1.png)

## Why Use a User-Defined Bridge Network?

By default, Docker containers can communicate over a built-in network called the "default bridge network." However, using a **user-defined bridge network** provides the following benefits:

- **Name resolution:** Containers connected to the same network can communicate by their container names, making it easier to manage multi-container setups.
- **Isolated environment:** Containers on a user-defined network are isolated from others unless explicitly connected to other networks.
- **Security:** You can control which containers can communicate by connecting them only to specific networks.
  
Now, let's move on to creating the network and launching our containers.


## Creating the User-Defined Bridge Network

The first step is to create a custom bridge network. Docker allows you to create networks of different types, such as `bridge`, `overlay`, and `host`. Here, we'll use the **bridge** driver, which is the default type for local container communication on a single host.

Run the following command to create the network:

```shell
docker network create --driver bridge my-bridge-network
```

This command creates a bridge network named `my-bridge-network`. You can inspect the network details using the command below:

```shell
docker network inspect my-bridge-network
```

This will give you detailed information about the network, including its subnet, gateway, and connected containers.

### Verifying Network Creation

You can list all existing Docker networks by running:

```shell
docker network ls
```

Expected Output:

![image](./images/out-1.png)

The newly created `my-bridge-network` should appear in the list, showing that it uses the `bridge` driver.

## Launching Containers and Connecting to the Network

In this section, we'll launch three containers (`container1`, `container2`, and `container3`), each running the **Nginx** web server, and connect them to our user-defined network.

### Launching Container 1

We use the following command to launch `container1`, and immediately connect it to the `my-bridge-network` network:

```shell
docker run -d --name container1 --network=my-bridge-network nginx
```

This will run the Nginx web server in the background (`-d`) and assign the name `container1` to the instance.

### Launching Container 2

Similarly, to launch `container2`, use:

```shell
docker run -d --name container2 --network=my-bridge-network nginx
```

### Launching Container 3

Finally, to launch `container3`, use:

```shell
docker run -d --name container3 --network=my-bridge-network nginx
```

With all three containers running, they are now connected to the same network, `my-bridge-network`. This enables them to communicate directly with one another.


## Verifying Container Status

To check the status of the running containers, use the command:

```shell
docker ps
```

Expected output:

![image](./images/out-2.png)

Here, you'll see the list of running containers along with their names, statuses, and other details like port mappings. The containers `container1`, `container2`, and `container3` should be listed as running, confirming that Nginx is operational inside each container.


## Verifying Communication Between Containers

Now that the containers are up and running, let's check if they can communicate with each other using their container names.

### Accessing the Shell of Container 1

First, we'll access the shell of `container1` to ping the other containers. Run:

```shell
docker exec -it container1 /bin/bash
```

This opens an interactive shell session inside `container1`. From this session, we can try pinging the other containers by their names.

### Pinging Container 2 from Container 1

To test connectivity from `container1` to `container2`, run:

```shell
ping container2 -c 5
```

This command will send 5 ICMP echo requests to `container2`. A successful ping will indicate that `container1` can communicate with `container2`.

Expected Output:

![image](./images/out-3.png)

### Pinging Container 3 from Container 1

Next, try pinging `container3` from `container1`:

```shell
ping container3 -c 5
```

Expected Output:

![image](./images/out-4.png)

The successful responses confirm that `container1` can reach both `container2` and `container3` within the custom network.

### Accessing the Shell of Container 2

We can repeat the process from another container. Access the shell of `container2` by running:

```shell
docker exec -it container2 /bin/bash
```

Once inside the shell, you can ping `container1` and `container3`.

### Pinging Container 1 from Container 2

```shell
ping container1 -c 5
```

Expected Output:

![image](./images/out-6.png)

### Pinging Container 3 from Container 2

```shell
ping container3 -c 5
```

Expected Output:

![image](./images/out-5.png)

These tests confirm that all the containers can communicate with each other over the custom bridge network.

## Conclusion

By following these steps, we successfully created a user-defined bridge network and launched multiple Nginx containers connected to the network. We verified that they can communicate with each other by pinging container names. This demonstrates how Docker networking facilitates smooth communication between containerized applications, making it easier to manage interconnected services.

**Key Takeaways:**
- User-defined networks offer name resolution, better isolation, and security.
- Docker simplifies inter-container communication without exposing containers to external networks.
- This approach is ideal for building scalable, secure, and efficient microservices architectures.

