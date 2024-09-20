# Dockerize React & Node.js App with Makefile & Github Action 

In this lab, we will guide you through the creation of a basic full-stack application where,

- The **frontend** is built using React.
- The **backend** is built using Node.js with Express.
- Both the frontend and backend are `dockerized` using Docker.
- The `Images` are built and pushed to DockerHub using a `Makefile`.
- Github action to automate image build and push procedure.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/workflow3.drawio.svg)

## Full Stack Architecture

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/arch2.drawio.svg)

Overall Project directory:

```sh
Full-stack-app
|- .github
|   |- workflows
|       |- backend-build-push.yml
|       |- frontend-build-push.yml
|- backend
|   |- index.js
|   |- package.json
|   |- Dockerfile
|   .
|
|- frontend
|   |- public
|   |- src
|   |- package.json
|   |- Dockerfile
|      
|- Makefile
```

Let's break it down step by step.

---

## Step 1: Setting Up the Backend (Node.js with Express)

### 1.1. Create a Directory for the Backend

```bash
mkdir Full-stack-app
cd Full-stack-app
mkdir backend
cd backend
```

### 1.2. Initialize the Node.js Project
```bash
npm init -y
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/image.png)

This will create a `package.json` file.

### 1.3. Install Dependencies
Install `express` to handle server routing.

```bash
npm install express cors
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/image-1.png)

### 1.4. Create `index.js` for the Backend

In the `backend` directory, create a file called `index.js`:

```bash
touch index.js
```

Edit `index.js` with the following content:

```javascript
const express = require('express');
const os = require('os');
const cors = require('cors');

const app = express();
const PORT = 4000;

app.use(cors()); // Enable CORS for all routes

app.get("/", (req, res) => {
    const message = "Hello world from the backend! 🚀";
    console.log(message);
    res.json({ message });
});

app.listen(PORT, () => {
    console.log(`Server Running at port ${PORT}`);
});
```

### 1.5. Create a Dockerfile for the Backend
In the `backend` directory, create a `Dockerfile`:

```bash
touch Dockerfile
```

Add the following content to the `Dockerfile`:

```Dockerfile
# Use the official Node.js image from the Docker Hub
FROM node:14

# Create and set the working directory inside the container
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app files
COPY . .

# Expose the port that your app will run on
EXPOSE 4000

# Start the server
CMD ["node", "index.js"]
```
---

## Step 2: Setting Up the Frontend (React)

### 2.1. Create a Directory for the Frontend

```bash
cd ..
npx create-react-app frontend
```

### 2.2. Modify the React App

Navigate to `frontend/src/App.js` and replace the content with the following code:

```javascript
import React, { useState, useEffect } from 'react';

function App() {
  const [data, setData] = useState('Loading...');

  const callAPI = async () => {
    try {
      const res = await fetch("http://localhost:4000/");
      const data = await res.json();
      setData(data.message);
    } catch (error) {
      console.log('Error:', error);
    }
  };

  useEffect(() => {
    callAPI();
  }, []);

  return (
    <div className="App">
      <h1>Backend Response:</h1>
      <p>{data}</p>
    </div>
  );
}

export default App;
```

This fetches the message from the backend and displays it on the frontend.

### 2.3. Create a Dockerfile for the Frontend
In the `frontend` directory, create a `Dockerfile`:

```bash
touch Dockerfile
```

Add the following content:

```Dockerfile
# Stage 1: Build the React app
FROM node:16-alpine AS build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the code
COPY . .

# Build the React app for production
RUN npm run build

# Stage 2: Serve the React app
FROM nginx:alpine

# Copy the built app to the NGINX container
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 to access the React app
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]
```

This Dockerfile uses a multi-stage build. The first stage builds the React app, and the second stage uses Nginx to serve the static files.

---

## Step 3: The `Makefile`

Let's create a `Makefile` to build and push the Docker images. In the root directory, create a `Makefile`:

```bash
touch Makefile
```

### Edit the Makefile with these content

```Makefile
# Variables
DOCKER_USERNAME = your-dockerhub-username
FRONTEND_IMAGE_NAME = react-frontend
FRONTEND_TAG = latest
BACKEND_IMAGE_NAME = nodejs-backend
BACKEND_TAG = latest

build-frontend:
    docker build -t $(FRONTEND_IMAGE_NAME) ./frontend

tag-frontend:
    docker tag $(FRONTEND_IMAGE_NAME):$(FRONTEND_TAG) $(DOCKER_USERNAME)/$(FRONTEND_IMAGE_NAME):$(FRONTEND_TAG)

push-frontend:
    docker push $(DOCKER_USERNAME)/$(FRONTEND_IMAGE_NAME):$(FRONTEND_TAG)

all-frontend: build-frontend tag-frontend push-frontend

build-backend:
    docker build -t $(BACKEND_IMAGE_NAME) ./backend

tag-backend:
    docker tag $(BACKEND_IMAGE_NAME):$(BACKEND_TAG) $(DOCKER_USERNAME)/$(BACKEND_IMAGE_NAME):$(BACKEND_TAG)

push-backend:
    docker push $(DOCKER_USERNAME)/$(BACKEND_IMAGE_NAME):$(BACKEND_TAG)

all-backend: build-backend tag-backend push-backend

clean: clean-frontend clean-backend

all: frontend backend

.PHONY: build-frontend tag-frontend push-frontend all-frontend clean-frontend \
        build-backend tag-backend push-backend all-backend clean-backend clean all
```
Modify the `DOCKER_USERNAME`, `Image_Name` variable with your DockerHub username and image name for actual deployment.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/image-2.png)

## Step 4: Write Github action

Create a `.github/workflows` directory in the root of your repository (if it doesn't already exist).

**Workflow 1:** Inside the workflows directory, create a file called `frontend-build-push.yml` (you can name it anything descriptive) to build the frontend image and push it to docker hub. Add the following content to the file:

```yaml
name: Frontend Docker Build and Push

on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'
  pull_request:
    branches:
      - main
    paths:
      - 'frontend/**'

jobs:
  build-and-push-frontend:
    runs-on: ubuntu-latest
    env:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and Push Frontend Docker Image
        run: |
          echo "Building and pushing frontend Docker image"
          make all-frontend
```

> This workflow will trigger, when there is a change in the `frontend` directory. Update the `paths` entry according to your directory structure.

**Workflow 2:** Inside the workflows directory, create a file called `backend-build-push.yml` (you can name it anything descriptive) to build the backend image and push it to docker hub. Add the following content to the file:

```yaml
name: Backend Docker Build and Push

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'
  pull_request:
    branches:
      - main
    paths:
      - 'backend/**'

jobs:
  build-and-push-backend:
    runs-on: ubuntu-latest
    env:
      DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
      DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and Push Backend Docker Image
        run: |
          echo "Building and pushing backend Docker image"
          make all-backend
```

> This workflow will trigger, when there is a change in the `backend` directory. Update the `paths` entry according to your directory structure.

### Store the secrets

**1. Store your Docker Hub username and password as GitHub Secrets:**
- Go to **Settings** > **Secrets** > **Actions** in your GitHub repository.
- Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/image-15.png)

**2. Push the `.github/workflows/*` file to your repository.**

- This will enable the automation of building and pushing Docker images based on changes in the `frontend` and `backend` directories.

This two workflow now efficiently handles the automation of Docker image builds and pushes based on directory-specific changes!

### Check out the workflow status

Go to your github repository, and check the status of the two workflow.

**Workflow1:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/image-12.png)

**Workflow2:**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/image-13.png)

Here, we can see the successfull completion of our workflows. 

## Step 5: Running the Application

Now that we have Docker images for both the frontend and backend in docker hub, let's run the entire application using Docker.

### Run the Backend Server

Run the backend image:

```bash
docker run -p 4000:4000 your-dockerhub-username/<backend-image-name>
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/image-5.png)

This will run the backend server on port 4000.

### Run the Frontend
Run the frontend image:

```bash
docker run -p 80:80 your-dockerhub-username/<frontend-image-name>
```

This will run the frontend on port 80. Go to this url and check if everything works fine or not!

```sh
http:localhost:80
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Full-stack-app/Docker%20Image%20using%20Github%20Action/images/image-14.png)

## Conclusion

You've successfully created a full-stack application using React for the frontend and Node.js with Express for the backend. Both applications were dockerized, and the images were built and pushed to DockerHub using a Makefile.

### Summary of Concepts:
- **Docker**: Used to containerize the application.
- **Makefile**: Automates the build and push processes.
- **Docker Hub**: Used to store and manage Docker images.
- **GitHub Actions**: Used to automate the build and push processes based on directory-specific changes.
- **React**: Frontend library.
- **Node.js/Express**: Backend server for handling API requests.

Now you can further develop your app, enhance the features, and scale it using these building blocks!