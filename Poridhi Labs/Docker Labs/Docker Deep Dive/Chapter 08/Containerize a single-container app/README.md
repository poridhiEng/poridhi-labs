# Containerize a Single-Container App

In this guide, we will walk through the process of containerizing a simple Node.js application. Containerization involves packaging an application and all its dependencies, libraries, and configurations into a single package known as a container. This ensures the app runs consistently across different environments, whether it's your local machine, a server, or the cloud.

Docker is the tool we'll use for containerization. It allows developers to automate the deployment of applications inside lightweight, portable containers. We’ll also explore how Docker layers work and their significance in the containerization process.

![](./images/image-1.png)

### Creating the Application Code

First, let's create a basic Node.js application. We will begin by creating a directory for the app and navigating into it:

```bash
mkdir my-node-app
cd my-node-app
```

Next, create a file named `app.js` with the following content:

```javascript
// app.js
const http = require('http');

const hostname = '0.0.0.0';
const port = 8080;

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello, World!\n');
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});
```

This is a simple HTTP server that responds with "Hello, World!".

### Creating the Dockerfile

A Dockerfile is a script that contains instructions for Docker to build your container image. Create a Dockerfile in the same directory with the following content:

```Dockerfile
# Use an official Node.js runtime as the base image
FROM node:14-alpine

# Set the working directory
WORKDIR /usr/src/app

# Copy the application code
COPY app.js .

# Install the necessary Node.js package
RUN npm install http@0.0.1-security

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the app
CMD ["node", "app.js"]
```

- **FROM**: Specifies the base image (Node.js with Alpine Linux, a lightweight version of Linux).
- **WORKDIR**: Sets the working directory inside the container.
- **COPY**: Copies `app.js` from the local machine to the container.
- **RUN**: Installs the necessary Node.js package.
- **EXPOSE**: Informs Docker the container listens on port 8080.
- **CMD**: Defines the command to run the app.


### Containerizing the App / Building the Image

Now that the Dockerfile is ready, we can build the Docker image. In your terminal, run:

```bash
docker build -t my-node-app:1.0 .
```

This command tells Docker to build an image named `my-node-app` with the version `1.0` using the current directory.

To verify that the image was created, use the following command:

```bash
docker images
```

![](./images/11.png)

This will display a list of available images.


### Pushing the Image (Optional)

If you'd like to share your image, you can push it to Docker Hub. Follow these steps:

1. Log in to Docker Hub:

    ```bash
    docker login
    ```

2. Tag the image with your Docker ID:

    ```bash
    docker tag my-node-app:1.0 <docker-id>/my-node-app:1.0
    ```

3. Push the image:

    ```bash
    docker push <docker-id>/my-node-app:1.0
    ```

This will make the image available for others to pull and use.

### Running the App

To run the containerized app, execute the following command:

```bash
docker run -d --name my-node-app-container -p 80:8080 my-node-app:1.0
```

- `-d`: Runs the container in detached mode (in the background).
- `--name`: Assigns a name to the running container.
- `-p 80:8080`: Maps port 8080 inside the container to port 80 on your machine.

Check that the container is running by typing:

```bash
docker ps
```

![](./images/12.png)

This will list all active containers.


### Testing the App

To test the app, you can use the `curl` command or open a browser and go to `http://localhost`. Using `curl`, run:

```bash
curl http://localhost:80
```

![](./images/13.png)

### Docker Layers and Efficiency

Each instruction in the Dockerfile creates a layer. These layers are cached and reused during subsequent builds if the content doesn’t change, which improves build speed and reduces storage space. For example:

- **FROM** creates a base layer.
- **COPY** adds a new layer with the application files.
- **RUN** installs dependencies in a separate layer.

You can inspect the layers of your image by running:

```bash
docker history my-node-app:1.0
```

![](./images/14.png)

This command displays each command from the Dockerfile and the corresponding layer it created.


### Optimizing Docker Images: Multi-Stage Builds

To reduce image size, you can use multi-stage builds, especially for production environments. In multi-stage builds, unnecessary files (such as development dependencies) are not included in the final image.

Here’s an example of a multi-stage Dockerfile:

```Dockerfile
# Stage 1: Build
FROM node:14-alpine AS builder
WORKDIR /usr/src/app
COPY app.js .
RUN npm install http@0.0.1-security

# Stage 2: Production
FROM node:14-alpine
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app .
EXPOSE 8080
CMD ["node", "app.js"]
```

In this setup, the first stage builds the app, and the second stage creates a minimal image without including the build tools, reducing the final image size.

### Container Management and Best Practices

#### Restart Policies

You can ensure that containers automatically restart if they crash or your system reboots. Add the `--restart` flag when running your container:

```bash
docker run -d --name my-node-app-container --restart always -p 80:8080 my-node-app:1.0
```

#### Environment Variables

Environment variables allow you to pass dynamic configurations into your container at runtime. For example:

```bash
docker run -d -e NODE_ENV=production -p 80:8080 my-node-app:1.0
```

### Security Considerations

- **Use Official Base Images**: Always start with trusted base images to reduce security risks.
- **Scan for Vulnerabilities**: Regularly scan your images for known vulnerabilities using tools like **Trivy** or **Docker Scan**.
- **Limit Privileges**: Run containers with the least privileges needed by using Docker’s security options.

### Conclusion

Containerizing applications with Docker ensures consistency, portability, and ease of deployment across various environments. By following best practices like using official base images, optimizing Docker layers, and employing security measures, you can create efficient and secure containerized applications.

This guide provides a clear step-by-step process for containerizing a Node.js app while explaining Docker's functionality, Dockerfile instructions, and optimization strategies. Happy containerizing!