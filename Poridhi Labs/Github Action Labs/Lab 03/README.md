# **GitHub Actions with Docker and Nginx**

<!-- ## **Docker with Nginx Lab** -->

This lab demonstrates how to build, test, and push Docker images using GitHub Actions. The example uses Nginx as a web server, illustrating an end-to-end CI/CD pipeline.


## **Task Description**

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/Lab%2003/images/lab-03.svg)



- Build, test, and push Docker images using GitHub Actions.
- Configure Nginx as a web server to serve static content.
- Set up a CI/CD pipeline triggered by GitHub pull request events.
- Test the Docker image locally and during the workflow.
- Push the final image to Docker Hub.


## Create and Configure GitHub Repository

1. Go to your GitHub and create a new repository called `github-actions-lab` with a `README.md` file. Now clone it in the Poridhis VM. 

2. Setup githubs default account:

    ```bash
    git config user.email "<your-email>"
    git config user.name "<Your Name>"
    ```

    Replace `<your-email>` and `<your-name>` with your github email address and username.



## **Lab Structure**

The repository structure is described as follows:

```plaintext
github-actions-lab/
├── .github/
│   └── workflows/
│       └── docker.yml
├── html/
│   └── index.html
├── nginx.conf
└── Dockerfile
```


You can create the structure using the following commands:

```bash
# Create the directory structure
mkdir -p github-actions-lab/.github/workflows github-actions-lab/html

# Create placeholder files
touch github-actions-lab/.github/workflows/docker.yml
touch github-actions-lab/html/index.html
touch github-actions-lab/nginx.conf
touch github-actions-lab/Dockerfile
```


## **Configure Nginx**

### **Step 1: Create `html/index.html`**
This file contains the web page content served by Nginx.

```html
<!DOCTYPE html>
<html>
<head>
    <title>GitHub Actions Docker Lab</title>
</head>
<body>
    <h1>Hello from GitHub Actions!</h1>
    <p>This is a Docker lab using Nginx.</p>
</body>
</html>
```

### **Step 2: Create `nginx.conf`**
This configuration file defines how Nginx serves content.

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }
}
```

The provided code defines an Nginx server configuration. It sets up a server to listen on port 80, specifying `localhost` as the server name. The root directory for serving files is `/usr/share/nginx/html`, and `index.html` is the default file served when accessing the root path (`/`). This configuration is commonly used to serve static web pages using Nginx.


## **Create the Dockerfile**

The `Dockerfile` defines the instructions to build a Docker image for serving a static website with Nginx:

`Dockerfile`:

```Dockerfile
FROM nginx:alpine
COPY html/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```








## **Create Workflow File**

#### **Create `.github/workflows/docker.yml`**
This workflow automates building, testing, and pushing Docker images.

```yaml
name: Docker Nginx Lab

on:
  pull_request:
    types: [closed]
    branches:
      - main

jobs:
  docker:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      # Checkout code
      - name: Checkout code
        uses: actions/checkout@v4

      # Login to DockerHub
      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      # Build Image
      - name: Build Docker image
        run: docker build -t mynginx:test .

      # Test Image
      - name: Test Docker image
        run: |
          docker run -d -p 8080:80 --name test-nginx mynginx:test
          sleep 5
          curl http://localhost:8080 | grep "Hello from GitHub Actions"
          docker stop test-nginx

      # Push Image
      - name: Push to DockerHub
        run: |
          docker tag mynginx:test ${{ secrets.DOCKER_USERNAME }}/mynginx:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/mynginx:latest
```



### **Detailed Explanations**

#### **Trigger Condition**

```yaml
on:
  pull_request:
    types: [closed]
    branches:
      - main
```
The workflow triggers when a pull request is merged into the `main` branch.

#### **Docker Login**

```yaml
- name: Login to DockerHub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}
```
- This step uses the `docker/login-action` to authenticate with Docker Hub.
- Credentials are securely retrieved from GitHub Secrets.

#### **Build and Test Image**

```yaml
- name: Build Docker image
  run: docker build -t mynginx:test .

- name: Test Docker image
  run: |
    docker run -d -p 8080:80 --name test-nginx mynginx:test
    sleep 5
    curl http://localhost:8080 | grep "Hello from GitHub Actions"
    docker stop test-nginx
```
1. **Build Docker Image:** Creates an image named `mynginx:test` from the `Dockerfile`.
2. **Test Docker Image:**
   - Runs the container on port 8080.
   - Verifies the web server output using `curl`.
   - Stops the container after testing.

#### **Push Image to Docker Hub**

```yaml
- name: Push to DockerHub
  run: |
    docker tag mynginx:test ${{ secrets.DOCKER_USERNAME }}/mynginx:latest
    docker push ${{ secrets.DOCKER_USERNAME }}/mynginx:latest
```
- Tags the image with your Docker Hub repository and the `latest` tag.
- Pushes the tagged image to Docker Hub.



### **Testing Locally**

#### **Build the Image Locally**
Run the following command:

```bash
docker build -t mynginx:test .
```

#### **Run the Container Locally**
Run the container to test it:

```bash
docker run -d -p 8000:80 mynginx:test
```

#### **Verify the Website**
Check the website using `curl`:

```bash
curl http://localhost:8000
```

Expected result:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/Lab%2003/images/image.png)

## **Required Secrets**
Add Secrets to Your Repository by following the following steps:

1. Navigate to **Settings** in your repository.
2. Go to **Secrets and variables > Actions**.
3. Add the following secrets:
   - **DOCKER_USERNAME**: Your Docker Hub username
   - **DOCKER_PASSWORD**: Your Docker Hub password/token


##  Test Workflow

### Create a branch

Create a new branch and checkout to the branch:

```bash
git checkout -b nginx-configured
```


### Push codes to the branch

```bash
git add .
git commit -m "Updated repository"
git push origin nginx-configured
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/Lab%2003/images/image-1.png)


### Run the workflow

1. Create a pull request.
2. Merge the pull request into the `main` branch.
3. Navigate to the **Actions** tab to monitor the workflow progress.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/Lab%2003/images/image-2.png)





## **Troubleshooting**

### **Common Issues**

1. **Docker Login Fails**
   - Verify Docker Hub credentials.
   - Ensure secrets are correctly configured.

   

2. **Build Fails**
   - Check the `Dockerfile` for syntax errors.
   - Run a no-cache build to troubleshoot:
     ```bash
     docker build --no-cache -t mynginx:test .
     ```
   - Check file permissions:
     ```bash
     ls -la html/ nginx.conf
     ```

3. **Test Fails**
   - Check container logs:
     ```bash
     docker logs test-nginx
     ```
   - Verify container status:
     ```bash
     docker ps -a
     ```



### **Practice Exercises**

1. **Add Health Check**
Ensure container health:

```yaml
- name: Health check
  run: |
    curl -f http://localhost:8080 || exit 1
```

2. **Add Version Tag**
Include a versioned tag:

```yaml
- name: Tag version
  run: |
    docker tag mynginx:test ${{ secrets.DOCKER_USERNAME }}/mynginx:${{ github.sha }}
```



### **Tips**
- Use specific base image tags to avoid unexpected changes.
- Implement health checks to ensure reliability.
- Use minimal images to reduce size.
- Test locally before pushing images.

## **Conclusion**

With these detailed instructions and explanations, you can confidently set up and manage a CI/CD pipeline with Docker and Nginx using GitHub Actions.

