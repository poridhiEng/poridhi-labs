# A Deeper Look into Node.js Docker Images

Node.js Docker images come in various flavours, each tailored for specific use cases. Picking the right image for your application can be challenging, as it involves balancing factors such as size, security vulnerabilities, and functionality. This document explores the differences among popular Node.js Docker images, highlighting their pros and cons to help developers make informed choices.

![](./images/banner%20.svg)

## Objective

This documentation aims to:

- Compare various Node.js Docker image variants.
- Analyse their composition and intended use cases.
- Provide recommendations for choosing the right image based on development and production needs.


## Table of Contents

- [Node.js Releases and Selection Criteria](#nodejs-releases-and-selection-criteria)
- [Basic Comparison of Available Images](#basic-comparison-of-available-images)
- [Overview of Each Image](#overview-of-each-image)
  - [Official Docker Images](#official-docker-images)
  - [Bitnami Images](#bitnami-images)
  - [GoogleContainerTools Distroless](#googlecontainertools-distroless)
  - [Chainguard’s Distroless](#chainguards-distroless)
- [Conclusion and Recommendations](#conclusion-and-recommendations)


## Node.js Releases and Selection Criteria

Node.js recommends using Active LTS or Maintenance LTS releases for production applications. Active LTS versions are considered stable and ready for general use, while Maintenance LTS ensures critical bug fixes for an extended period.

![alt text](./images/image.png)

###  Release Lifecycle

- **Current Release:** Supported for six months after release, intended for library authors and early adopters.

- **Active LTS:** Stable and reliable, with extended support for 30 months. Suitable for production.

- **Maintenance LTS:** Focused on critical fixes, suitable for older but still functional production environments.


## Basic Comparison of Available Images

### Official Docker Images

In the official Node.js Docker images, the `node` tag is used to specify the version of Node.js. The `node` tag is followed by the version number, which corresponds to the Node.js release. Here are some examples:

```bash
docker pull node:22
docker pull node:22-slim
docker pull node:22-alpine
```

### Bitnami Images

Bitnami repacks the Node.js binary with additional dependencies and tools. 

```bash
docker pull bitnami/node:22
```

### GoogleContainerTools Distroless

GoogleContainerTools Distroless images are minimalistic images that only contain the Node.js binary and its dependencies. They are designed to be used in production environments where security and size are critical.

```bash
docker pull gcr.io/distroless/nodejs22-debian12
```

### Chainguard’s Distroless

Chainguard’s Distroless images are similar to GoogleContainerTools Distroless images, but they are built on top of the Chainguard base image.

```bash
docker pull cgr.dev/chainguard/node:latest
```

Simply listing the pulled images can already give us some initial food for thought:

```bash
docker images
```

![](./images/image-2.png)

If we observe the images, we can see that the `node:22` image is the largest image with `1.2GB` in size, followed by lower size image `gcr.io/distroless/nodejs22-debian12` with `143MB` in size.

## Overview of Each Images

### `node:22`

If we look at the `node:22` image, we can see that it is the largest image of the lot. It is 1.2GB in size. It has a full-fledged Python installation inside.

If we run the following command, we can see that the Python installation is indeed present.

```bash
docker run --entrypoint bash node:22 -c 'python3 --version'
```

![](./images/image-3.png)

Interesting is that Python is not the only "unexpected" package in this image - for instance, this image also includes the entire GNU Compiler Collection:

```bash
docker run --entrypoint bash node:22 -c 'gcc --version'
```

![](./images/image-4.png)

If we inspect the package list, we can see that the `node:22` image includes a variety of packages

```bash
# Download latest release
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
syft node:22
```
![alt text](./images/images-5.png)

And, of course, with so many packages comes with lot of CVEs. `CVEs` are a list of security vulnerabilities that have been discovered in the software.

```bash
trivy image -q node:22
```

All the packages are not always necessary for the Node.js application to run. That is why we have the `node:22-slim` and `node:22-alpine` images.

### Why `node:22` has so many bloated packages?

The `node:<version>` image has so many bloated packages because it is based on `buildpack-deps`, which includes a wide range of commonly used `Debian` packages. These packages are included to support various development needs, such as `Python`, `GCC`, and other tools required for building or compiling software. While this design reduces the need to install additional packages in derived images, it significantly increases the size of the base image, making it less suitable for lightweight production environments.





