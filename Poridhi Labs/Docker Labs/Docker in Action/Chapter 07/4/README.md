
# Modifying Docker Image Attributes

This lab aims to deepen your understanding of Docker image attributes and how they can be modified and inherited across different layers of an image. 

By the end of this exercise, you will be familiar with setting environment variables, working directories, exposed ports, volume definitions, container entrypoints, and commands.
## Description


When you use docker container commit, you create a new layer for an image. This layer includes not only a snapshot of the filesystem but also metadata about the execution context. The following parameters, if set for a container, will be carried forward to the new image:

- Environment variables
- Working directory
- Exposed ports
- Volume definitions
- Container entrypoint
- Command and arguments

If these parameters are not explicitly set, they will be inherited from the original image.

This lab will provide you with hands-on experience in modifying these attributes and observing how they are inherited across image layers.

## Task

**Create a Container with Environment Variables**
- Run a Docker container from the `busybox:latest` image, setting two environment variables.
- Commit the running container to a new image.

**Modify the Entrypoint and Command**
- Run a new container from the previously committed image, setting a new entrypoint and command.
- Commit this container to update the image.

**Verify Inheritance of Attributes**
- Run a container from the final image without specifying any command or entrypoint to verify that the environment variables and the entrypoint/command are inherited correctly.

![alt text](./images/image.png)

## Solution Steps

**Create a Container with Environment Variables**

- Run the container:
    ```bash
    docker run --name container1 -e ENV_EXAMPLE1=value1 -e ENV_EXAMPLE2=value2 busybox:latest
    ```

    This command creates a new container named `container1` from the `busybox:latest` image and sets two environment variables, `ENV_EXAMPLE1` and `ENV_EXAMPLE2`.

    Expected output:

    ```
    term@ubuntu-x1brs3-5444b5f5fc-j5xpq:~$ docker run --name container1 -e ENV_EXAMPLE1=value1 -e ENV_EXAMPLE2=value2 busybox:latest

    Unable to find image 'busybox:latest' locally
    latest: Pulling from library/busybox
    ec562eabd705: Pull complete 
    Digest: sha256:9ae97d36d26566ff84e8893c64a6dc4fe8ca6d1144bf5b87b2b85a32def253c7
    Status: Downloaded newer image for busybox:latest
    ```

- Commit the container to a new image:
    ```bash
    docker commit container1 new-image
    ```

    This command commits the `container1` container to a new image named `new-image`.

    Varify the image creation using the following command:

    ```bash
    docker images
    ```

    Expected output:

    ```bash
    term@ubuntu-x1brs3-5444b5f5fc-j5xpq:~$ docker images

    REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
    new-image    latest    7865e738cc85   11 seconds ago   4.26MB
    busybox      latest    65ad0d468eb1   12 months ago    4.26MB
    ```


**Modify the Entrypoint and Command**

- Run a new container with a specific entrypoint and command:
    ```bash
    docker run --name container2 --entrypoint "/bin/sh" new-image -c "echo \$ENV_EXAMPLE1 \$ENV_EXAMPLE2"
    ```

    This command runs a new container named `container2` from the `new-image` image, setting the entrypoint to `/bin/sh` and the command to `-c "echo \$ENV_EXAMPLE1 \$ENV_EXAMPLE2"`. This setup will print the values of the environment variables.

    Expected output:

    ```bash
    term@ubuntu-x1brs3-5444b5f5fc-j5xpq:~$ docker run --name container2 --entrypoint "/bin/sh" new-image -c "echo \$ENV_EXAMPLE1 \$ENV_EXAMPLE2"

    value1 value2
    ```


- Commit this container to update the image:
    ```bash
    docker commit container2 new-image
    ```
    This will commit the container `container2` to the `new-image` image, updating the image with the new entrypoint and command. The updated image will have the entrypoint and the command with it.

- Verify the new image's entrypoint and command settings:
    ```bash
    docker inspect --format '{{ .Config.Entrypoint }}' new-image
    docker inspect --format '{{ .Config.Cmd }}' new-image
    ```

    Expected output:

    ```bash
    term@ubuntu-x1brs3-5444b5f5fc-j5xpq:~$ docker inspect --format '{{ .Config.Entrypoint }}' new-image

    [/bin/sh]

    term@ubuntu-x1brs3-5444b5f5fc-j5xpq:~$ docker inspect --format '{{ .Config.Cmd }}' new-image

    [-c echo $ENV_EXAMPLE1 $ENV_EXAMPLE2]
    ```

**Verify Inheritance of Attributes**

- Run a container from the final image to verify the inherited behavior:
    ```bash
    docker run --rm new-image
    ```

    This command runs a container from the final `new-image` image, verifying that the environment variables and the entrypoint/command are inherited correctly. 

    Expected output:

    ```bash
    term@ubuntu-x1brs3-5444b5f5fc-j5xpq:~$ docker run --rm new-image
    value1 value2
    ```


By completing this lab, we hope, you have a practical understanding of how to modify and verify Docker image attributes, and how these changes are inherited across image layers.