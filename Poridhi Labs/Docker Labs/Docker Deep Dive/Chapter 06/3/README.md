# Create own Docker image
Creating and building your own Docker image involves writing a Dockerfile, which is a script that contains a series of instructions to create the image. Here's a step-by-step guide on how to do this:

## Step 1: Install Docker

To install docker, we can do the following steps

1. Update the apt and install vim
```
sudo apt update
sudo apt install vim -y
```
2. Save this install.sh script file

```bash
#!/bin/bash

# Update package database
#!/bin/bash

# Update package database
echo "Updating package database..."
sudo apt update

# Upgrade existing packages
echo "Upgrading existing packages..."
sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker’s official GPG key
echo "Adding Docker’s GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker APT repository
echo "Adding Docker APT repository..."
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package database with Docker packages
echo "Updating package database with Docker packages..."
sudo apt update

# Install Docker
echo "Installing Docker..."
sudo apt install -y docker-ce

# Start Docker manually in the background
echo "Starting Docker manually in the background..."
sudo dockerd > /dev/null 2>&1 &

# Add current user to Docker group
echo "Adding current user to Docker group..."
sudo usermod -aG docker ${USER}

# Apply group changes
echo "Applying group changes..."
newgrp docker

# Set Docker socket permissions
echo "Setting Docker socket permissions..."
sudo chmod 666 /var/run/docker.sock

# Print Docker version
echo "Verifying Docker installation..."
docker --version

# Run hello-world container in the background
echo "Running hello-world container in the background..."
docker run -d hello-world

echo "Docker installation completed successfully."
echo "If you still encounter issues, please try logging out and logging back in."

```
3. Change the permission
```
chmod +x install.sh
```
4. Run the script file. This will install Docker on e ubuntu system.
```
./install.sh
```

Open new terminal to use docker without root permission,or use in terminal 1 with root permission.

## Step 2: Create a Dockerfile
A Dockerfile is a text file that contains commands to assemble an image. Create a new directory for your project and within that directory, create a file named `Dockerfile`.

## Step 3: Write Instructions in the Dockerfile
Here’s a basic example of a Dockerfile for a Python application:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
```

## Step 4: Add Application Files
Add your application files in the same directory as your Dockerfile. For example, you might have:

- `app.py`: Your main application script.
- `requirements.txt`: A file listing the dependencies for your Python application.

## Step 5: Build the Docker Image
Open a terminal and navigate to the directory containing your Dockerfile. Use the `docker build` command to create your image.

```sh
docker build -t my-python-app .
```

The `-t` flag tags your image with a name (`my-python-app`).

## Step 6: Run the Docker Container
Once the image is built, you can run a container based on this image using the `docker run` command.

```sh
docker run -p 4000:80 my-python-app
```

This command maps port 80 in the container to port 4000 on your host machine.

## Example: Complete Project Structure
```
my-python-app/
├── app.py
├── Dockerfile
└── requirements.txt
```
### app.py
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

### requirements.txt
```
flask
```

By following these steps, you can create, build, and share your own Docker images.

---
# Deleting docker images

Deleting a Docker image involves a few simple steps. Below is a step-by-step guide on how to remove Docker images from your system.

### Step 1: List Docker Images
Before deleting an image, you need to know the image's ID or repository name. Use the following command to list all Docker images on your system:

```sh
docker images
```

This command will display a list of all images, including their repository names, tags, and image IDs.

### Step 2: Identify the Image to Delete
From the list of images, identify the image you want to delete by noting its repository name, tag, or image ID. For example, you might see output similar to this:

```sh
REPOSITORY          TAG         IMAGE ID       CREATED         SIZE
my-python-app       latest      d1e1f2b3c4d5   2 days ago      116MB
another-image       v1.0        a5b6c7d8e9f0   4 days ago      200MB
```

### Step 3: Remove the Image
To delete an image, use the `docker rmi` command followed by the image ID or repository name and tag. For example, to remove the image `my-python-app:latest`, you can use either the image ID or the repository name and tag:

```sh
docker rmi d1e1f2b3c4d5
```

or

```sh
docker rmi my-python-app:latest
```

If the image is used by any containers, you will need to remove those containers first or use the `-f` (force) flag to forcefully remove the image:

```sh
docker rmi -f d1e1f2b3c4d5
```

### Step 4: Verify the Image Removal
After removing the image, you can verify that it has been deleted by listing the images again:

```sh
docker images
```

The image you deleted should no longer appear in the list.

### Additional Steps: Remove Dangling Images
Dangling images are those that are not tagged and have the repository name `<none>`. To remove all dangling images, use the following command:

```sh
docker image prune
```

This command will prompt you to confirm the deletion of all dangling images. To remove all unused images (not just dangling ones), add the `-a` flag:

```sh
docker image prune -a
```

By following these steps, you can successfully delete Docker images from your system.