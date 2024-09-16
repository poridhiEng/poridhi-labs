# Lab: Exploring Docker Image Layers and Size Management

Docker images are built from layers, where each layer represents a set of filesystem changes. The size of an image on disk is the sum of the sizes of its component layers. Docker allows you to commit changes to a running container, creating new image layers. 

This lab will guide you through these concepts with hands-on practices, focusing on creating and modifying a Docker image with ubuntu as the base image. You will install and remove software within containers, observe the changes in image sizes, and understand the impact of Docker's Union File System (UFS) on image size. 

![alt text](./images/image.png)

## Task: Building and Modifying Docker Images
Here, you will create a Docker image from the official Ubuntu image, install Git within a container, and commit the changes to create a new image. You will then modify this image by removing Git and observe how Docker manages image layers and size. 

## Steps:
**Pull the Ubuntu Image:**

Pull the `ubuntu` image from Docker Hub.
```sh
docker pull ubuntu
```
This command fetches the latest `ubuntu` image from Docker Hub and stores it in your local Docker repository.

**Create a Container and Install Git:**

Create a container from the `ubuntu` image and install Git.
```sh
docker run -d --name ubuntu-git-container ubuntu sleep infinity
docker exec -it ubuntu-git-container apt-get update
docker exec -it ubuntu-git-container apt-get install -y git
```
These commands run a container named `ubuntu-git-container` from the `ubuntu` image and install Git inside the container. The `sleep infinity` command keeps the container running. The `apt-get update` and `apt-get install -y git` commands update the package list and install Git, respectively.

**Commit the Changes to Create a New Image:**

Commit the container to create a new image with Git installed.
```sh
docker commit ubuntu-git-container ubuntu-git:1.0
docker tag ubuntu-git:1.0 ubuntu-git:latest
```
These commands commit the current state of the `ubuntu-git-container` container to a new image named `ubuntu-git` with a tag `1.0`, and then tag this image as `latest`.


**Check Image Sizes:**

Check the sizes of all the images created.
```sh
docker images
```

Expected output:

```bash
term@ubuntu-71gmcp-db867df5c-4ddm9:~$ docker images
REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
ubuntu-git   1.0       2c0f3da09652   6 seconds ago   198MB
ubuntu-git   latest    2c0f3da09652   6 seconds ago   198MB
ubuntu       latest    17c0145030df   7 days ago      76.2MB
```

**Remove Git:**

Create a new container from the `ubuntu-git` image and remove Git.
```sh
docker run --name ubuntu-git-remove --entrypoint /bin/bash ubuntu-git:latest -c "apt-get remove -y git"
```
This command runs a container named `ubuntu-git-remove` from the `ubuntu-git:latest` image with an entrypoint set to `/bin/bash`, and removes Git from the container.

**Commit the Changes to Create a New Image with Git Removed:**

Commit the container to create a new image with Git removed.
```sh
docker commit ubuntu-git-remove ubuntu-git:2.0
docker tag ubuntu-git:2.0 ubuntu-git:latest
```
These commands commit the current state of the `ubuntu-git-remove` container to a new image named `ubuntu-git:removed` and reassign the `latest` tag to this new image.


**Check Image Sizes:**

Check the sizes of all the images created.
```sh
docker images
```

Expected output:

```bash
term@ubuntu-71gmcp-db867df5c-4ddm9:~$ docker images
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
ubuntu-git   2.0       6acdc1e0df8e   7 seconds ago    198MB
ubuntu-git   latest    6acdc1e0df8e   7 seconds ago    198MB
ubuntu-git   1.0       2c0f3da09652   51 seconds ago   198MB
ubuntu       latest    17c0145030df   7 days ago       76.2MB
```



Notice that even though you removed Git, the image actually same in size.
 Although you could examine the specific changes with `docker diff`, you should be
 quick to realize that the reason for the increase has to do with the union file system.

 Remember, UFS will mark a file as deleted by actually adding a file to the top layer.
 The original file and any copies that existed in other layers will still be present in the
 image.  When a file is deleted, a delete record is written to the top layer, which overshadows
 any versions of that file on lower layers.
 
 It’s important to minimize image size for the sake of the people and systems
 that will be consuming your images. If you can avoid causing long download times and
 significant disk usage with smart image creation, then your consumers will benefit.
