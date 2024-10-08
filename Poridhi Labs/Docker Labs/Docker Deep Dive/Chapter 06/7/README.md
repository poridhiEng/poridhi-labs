# Searching Docker Hub from the CLI

The `docker search` command allows us to search `Docker Hub` directly from the command line interface (CLI). While its capabilities are somewhat limited, as it primarily searches against strings in the **“NAME”** field, you can still filter the output based on other columns returned by the search.

## Basic Usage

In its most basic form, `docker search` looks for repositories that contain a specified string in their `“NAME”` field. For example, the following command searches for repositories that include the string `“nigelpoulton”`:

```sh
$ docker search nigelpoulton
NAME                                 DESCRIPTION                                     STARS     OFFICIAL
nigelpoulton/pluralsight-docker-ci   Simple web app used in my Pluralsight video …   27        
nigelpoulton/k8sbook                 Simple web app used for demos in The Kuberne…   5         
nigelpoulton/tu-demo                 Voting web server used for various Pluralsig…   16        
nigelpoulton/getting-started-k8s     Node.js web app                                 12        
nigelpoulton/gsd                     Getting Started with Docker -- Pluralsight v…   9         
nigelpoulton/acg-web                 Simple web app for A Cloud Guru Kubernetes D…   0         
nigelpoulton/qsk-book                Images for use in *Quick Start Kubernetes* b…   3         
nigelpoulton/vote                    Fork of dockersamples Voting App for *Docker…   1            3
```

The “NAME” field refers to the repository name, which includes the Docker ID or organization name for unofficial repositories. This will display all repositories created by or associated with `Nigel Poulton`.

## Searching for Specific Terms

We can also search for repositories that include specific keywords. For example, to search for repositories with "alpine" in the name, you would use:

```sh
$ docker search alpine
NAME                               DESCRIPTION                                     STARS     OFFICIAL
alpine                             A minimal Docker image based on Alpine Linux…   10863     [OK]
alpinelinux/docker-cli             Simple and lightweight Alpine Linux image wi…   11        
alpinelinux/alpine-gitlab-ci       Build Alpine Linux packages with Gitlab CI      3         
alpinelinux/gitlab-runner-helper   Helper image container gitlab-runner-helper …   7         
alpinelinux/unbound                                                                12        
alpinelinux/rsyncd                                                                 2         
alpinelinux/alpine-drone-ci        Build Alpine Linux packages with drone CI       0         
alpinelinux/ansible                Ansible in docker                               19  
```

Here, we can see both official and unofficial repositories.

### Filtering Official Repositories

To filter the search results and display only official repositories, you can use the `--filter` option with the `is-official` parameter:

```sh
$ docker search alpine --filter "is-official=true"
NAME      DESCRIPTION                                     STARS     OFFICIAL
alpine    A minimal Docker image based on Alpine Linux…   10863     [OK]
```

### Example Scenario

Suppose, we are managing a production environment and need to ensure that only trusted and verified images are used. We can filter for official images to ensure compliance with security policies:

```sh
$ docker search alpine --filter "is-official=true"
```

This command will help us to find only the official Alpine images, which are more likely to be secure and maintained.

## Limiting Results

By default, `docker search` will return up to `25` results. If we need more, we can use the `--limit` flag to increase this number, up to a maximum of `100` results:

```sh
$ docker search alpine --limit 50
```

### Example Scenario

Suppose you are conducting a comprehensive review of available Alpine images for a project and need more than the default 25 results, increasing the limit can provide a broader view of available options:

```sh
$ docker search alpine --limit 50
```

## Advanced Filtering

In addition to filtering for official images, Docker search supports other filters, such as the number of `stars` or whether the image is `automated`. For example, to find automated images with “alpine” in the name, you could use:

```sh
$ docker search alpine --filter "is-automated=true"
```

The "is-automated" filter is deprecated by the way, and searching for "is-automated=true" will not yield any results in future but for now is ok.

### Example Scenario

If you prefer to use automated builds because they often include continuous integration and delivery (CI/CD) practices, you can filter for these types of images:

```sh
$ docker search alpine --filter "is-automated=true"
```

This helps you identify images that are automatically built and potentially more reliable for use in your workflows.

By leveraging these search and filter capabilities, you can efficiently locate and utilize the Docker images that best meet your needs, whether for development, testing, or production environments.