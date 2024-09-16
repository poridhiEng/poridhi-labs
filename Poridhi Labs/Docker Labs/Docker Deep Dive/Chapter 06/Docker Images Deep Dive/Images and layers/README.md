# Docker Images and Layers

Docker images consist of loosely-connected read-only `layers`, where each layer represents a filesystem change (e.g., adding a file or installing a package). Once created, images are `immutable`, meaning they do not change.

![alt text](./images/layers.png)

## Inspecting Layers

There are several ways to inspect the layers that make up an image. For instance, you can see layer details during image pulls.

```sh
$ docker pull ubuntu:latest
latest: Pulling from library/ubuntu
952132ac251a: Pull complete
82659f8f1b76: Pull complete
c19118ca682d: Pull complete
8296858250fe: Pull complete
24e0251a0e2c: Pull complete
Digest: sha256:f4691c96e6bbaa99d...28ae95a60369c506dd6e6f6ab
Status: Downloaded newer image for ubuntu:latest
docker.io/ubuntu:latest
```

Each line ending with “Pull complete” represents a layer in the image that was pulled.

You can also inspect the image with the `docker inspect` command to see the image layers. Here's an example inspecting the `ubuntu:latest` image:

```sh
$ docker inspect ubuntu:latest
[
    {
        "Id": "sha256:bd3d4369ae.......fa2645f5699037d7d8c6b415a10",
        "RepoTags": [
            "ubuntu:latest"
        ],
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:c8a75145fc...894129005e461a43875a094b93412",
                "sha256:c6f2b330b6...7214ed6aac305dd03f70b95cdc610",
                "sha256:055757a193...3a9565d78962c7f368d5ac5984998",
                "sha256:4837348061...12695f548406ea77feb5074e195e3",
                "sha256:0cad5e07ba...4bae4cfc66b376265e16c32a0aae9"
            ]
        }
    }
]
```

The output shows the layers using their `SHA256` hashes.

The `docker history` command is another way to inspect an image and see its build history, although it does not provide a strict list of layers in the final image.

### Layer Stacking and Combination

When additional layers are added to an image, they are stacked on top of each other in the order they were added. For instance, in the figure 01, there are two layers, each containing three files. As a result, the overall image combines all files from both layers, resulting in six files in total.

![](./images/file1.png)

In more complex scenarios, like the three-layer image depicted in Figure 2, files from higher layers can obscure those from lower layers. For example, if a file in the top layer is an updated version of a file in a lower layer, the updated version takes precedence. This mechanism allows for the addition of updated files as new layers to the image. 

### Docker Storage Drivers

Docker employs storage drivers to manage the stacking and presentation of layers as a single unified filesystem/image. These drivers, such as `overlay2`, `devicemapper`, `btrfs`, and `zfs`, are based on Linux filesystem or block-device technologies, each with its unique performance characteristics.

![](./images/file2.png)

Regardless of the storage driver used, the user experience remains consistent, with Docker presenting a unified view of the stacked layers. Figure 03 illustrates how a three-layer image appears as a single merged entity to the system.

## Example use case

### Creating a Simplified Python Application

Let's walk through an example of building a simple Python application Docker image, starting with a base image of `Ubuntu 22.04` and adding layers for `Python` and the application `source code`. This example will demonstrate how layers are built on top of each other.


### Step 1: Create a Dockerfile

Create a file named `Dockerfile` with the following content:

```Dockerfile
# Use the official Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set environment variables to avoid user prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python (adds a new layer)
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy application source code to the image (adds a new layer)
COPY app /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Run the Python application
CMD ["python3", "app.py"]
```

### Step 2: Add Application Source Code

Create a directory named `app` and add your Python application files. For example, create a simple `app.py` file:

```python
# app/app.py

print("Hello, World!")
```
The directory structure should look like this:

```sh
/path/to/your/project
└── app
    └── app.py
```

### Step 3: Build the Docker Image

Open a terminal, navigate to the directory containing your Dockerfile and the `app` directory, and run the following command:

```sh
docker build -t my-python-app .
```

![](./images/pythonimage.png)

This command will build the Docker image and tag it as `my-python-app`.

### Step 4: Verify the Image

Run a container from the newly created image to verify it works:

```sh
docker run my-python-app
```
We should get this output:

![](./images/output.png)

### Explanation of Layers

1. **Base Layer**: `FROM ubuntu:22.04` - This is the starting layer, which includes the official Ubuntu 22.04 image.
2. **Python Layer**: `RUN apt-get update && apt-get install -y python3 python3-pip` - This adds Python and pip to the image.
3. **Application Code Layer**: `COPY app /usr/src/app` - This adds the application source code to the image.

We can inspect the image layer using docker inspect command.
```sh
$ docker inspect my-python-app
```

![](./images/imagelayers.png)

Here is the diagram of the image layers:

![](./images/ore.png)


<!-- ## Sharing Image Layers

Multiple Docker images can share layers, leading to efficiencies in both space and performance. Here’s an example demonstrating this concept:

```sh
$ docker pull <repository> -a
```

This command downloads all images in a repository, but it has limitations. It may fail if the repository contains images for multiple platforms and architectures such as Linux and Windows, or `amd64` and `arm64`.

Notice the lines ending in "Already exists." These indicate that Docker recognizes when it already has a local copy of an image layer. For example, if you pull an image tagged as `latest` first, then pull `v1` and `v2`, Docker will reuse the shared layers, as these images are nearly identical except for the top layer.

Docker on Linux supports various storage drivers, each implementing image layering, layer sharing, and copy-on-write (CoW) behavior differently. However, the user experience remains consistent across all storage drivers.

### Pulling Images by Digest

Pulling images using their name (tag) is the most common method, but tags are mutable and can cause issues if misused. For example, tagging a fixed image with the same tag as a vulnerable image can lead to confusion about which image is being used in production.

Docker supports a content-addressable storage model where all images get a cryptographic content hash called a digest. Digests are immutable, meaning any change in the image content results in a new unique digest.

#### Viewing Digests

When you pull an image, Docker provides its digest. You can also view the digests of images in your local repository:

```sh
$ docker pull alpine
Using default tag: latest
latest: Pulling from library/alpine
08409d417260: Pull complete
Digest: sha256:02bb6f42...44c9b11
Status: Downloaded newer image for alpine:latest
docker.io/library/alpine:latest

$ docker images --digests alpine
REPOSITORY   TAG       DIGEST                        IMAGE ID       CREATED      SIZE
alpine       latest    sha256:02bb6f42...44c9b11     44dd6f223004   9 days ago   7.73MB
```

### Pulling by Digest

To ensure you get the exact image you expect, use the digest to pull the image:

```sh
$ docker rmi alpine:latest
Untagged: alpine:latest
Untagged: alpine@sha256:02bb6f428431fbc2809c5d1b41eab5a68350194fb508869a33cb1af4444c9b11
Deleted: sha256:44dd6f2230041eede4ee5e792728313e43921b3e46c1809399391535c0c0183b
Deleted: sha256:94dd7d531fa5695c0c033dcb69f213c2b4c3b5a3ae6e497252ba88da87169c3f

$ docker pull alpine@sha256:02bb6f42...44c9b11
docker.io/library/alpine@sha256:02bb6f42...44c9b11: Pulling from library/alpine
08409d417260: Pull complete
Digest: sha256:02bb6f428431...9a33cb1af4444c9b11
Status: Downloaded newer image for alpine@sha256:02bb6f428431...9a33cb1af4444c9b11
docker.io/library/alpine@sha256:02bb6f428431...9a33cb1af4444c9b11
```

### Image Hashes (Digests)

Images are collections of independent layers, with each layer identified by a cryptographic hash of its content. Changing the image or any layer changes the associated hashes, ensuring immutability.

When images are pushed or pulled, layers are compressed to save bandwidth and storage space. However, compressed content hashes differ from uncompressed ones, which can cause hash verification issues. To solve this, Docker uses distribution hashes for the compressed versions of layers. This ensures that layers arriving at a registry haven't been tampered with.

This guide provides an overview of handling Docker images, including sharing image layers, pulling images by digest, and understanding image hashes. By following these practices, you can manage Docker images more effectively and ensure consistency across your deployments. -->