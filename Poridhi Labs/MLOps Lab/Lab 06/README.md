# MLOps Workflow in Kubernetes with MLflow, and S3 Integration

In this hands-on lab, we will build a complete MLOps environment using Kubernetes, MLflow, and Amazon S3. This environment enables seamless tracking of machine learning experiments, efficient management of models, and scalable deployment using Kubernetes. By integrating MLflow for experiment tracking and S3 for artifact storage, we will create a robust and production-ready MLOps infrastructure. 

![](./images/x1.svg)

The guide will walk you through deploying MLflow on a Kubernetes cluster, configuring S3 as a backend storage, setting up PostgreSQL as a metadata store, and running a sample machine learning experiment. By the end of this lab, you will have a comprehensive understanding of deploying, managing, and scaling machine learning workflows in a containerized environment.

## Objectives

After completing this lab, you will be able to:

- **Deploy MLflow** on a Kubernetes cluster with S3 integration for artifact and model storage.
- **Configure PostgreSQL** as the backend metadata store for MLflow.
- **Create and run automated model training jobs** in Kubernetes.
- **Use MLflow to track experiments**, including metrics, parameters, and artifacts stored in S3.
- **Implement best practices for MLOps** in a cloud-native environment.

## Task Description

This lab involves the following tasks:

1. **Environment Setup**: Prepare the necessary tools and access to Kubernetes, AWS CLI, and Docker.
2. **Create S3 bucket**: Create an S3 bucket using the AWS CLI.
3. **Creating the MLflow Server with S3 Integration**: Build a Docker image for the MLflow server and configure it to use S3 for artifact storage.
4. **Developing the Model Training Script**: Create a script to generate synthetic data and train a machine learning model using the RandomForest algorithm.
5. **Building Docker Images**: Containerize the MLflow server and model training script.
6. **Creating Kubernetes Manifests**: Define the configurations for PostgreSQL, MLflow server, and the model training job in YAML files.
7. **Deploying to Kubernetes**: Deploy PostgreSQL, MLflow server, and model training CronJob to the Kubernetes cluster.
8. **SetUp LoadBalancer for MLflow and Tracking Results**: Access MLflow UI, and view results.
9. **Cleaning Up**: Remove all deployed resources from the Kubernetes cluster.


## Step 1: Environment Setup

1. **Set Up Project Directory**:  
   Create a project directory and subdirectories to organize the project files.

   ```bash
   mkdir k8s-mlops-lab
   cd k8s-mlops-lab
   mkdir mlflow_server model_training k8s_manifests
   ```

2. **Configure AWS CLI**:  
   Install the AWS CLI if not already installed.

    ```bash
    sudo apt update && sudo apt install awscli
    ```

   Set up AWS CLI configuration.

   ```bash
   aws configure
   ```

   Provide your AWS Access Key ID, Secret Access Key, and preferred region.



## Step 2: Creating S3 bucket using AWS CLI

Create an S3 bucket. Replace the `<your-bucket-name>` with your unique bucket name.

```bash
aws s3api create-bucket --bucket <your-bucket-name> --region ap-southeast-1 --create-bucket-configuration LocationConstraint=ap-southeast-1 
```

Enable versioning on the S3 bucket.

```bash
aws s3api put-bucket-versioning --bucket <your-bucket-name> --versioning-configuration Status=Enabled
```

Verify versioning status.

```bash
aws s3api get-bucket-versioning --bucket <your-bucket-name> 
```

![alt text](./images/image-7.png)


## Step 3: Creating the MLflow Server with S3 Integration

Navigate to the `mlflow_server` directory Create a `Dockerfile` for the MLflow server. Add the following content to the `Dockerfile`:

```dockerfile
FROM python:3.8-slim-buster

WORKDIR /mlflow

RUN pip install mlflow psycopg2-binary boto3

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "postgresql://mlflow:mlflow@postgres/mlflow", \
     "--default-artifact-root", "s3://<your-bucket-name>", \
     "--artifacts-destination", "s3://<your-bucket-name>"]
```

Replace `<your-bucket-name>` with your actual S3 bucket name and save the file.

## Step 4: Developing the Model Training Script

Navigate to the `model_training` directory. Create a new file named `train_model.py`. Add the following content to `train_model.py`. Replace `<your-bucket-name>` with your actual S3 bucket name.

```python
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
import json

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("s3://<your-bucket-name>/k8s_synthetic_classification_workflow")

def generate_synthetic_data(n_samples=1000):
    np.random.seed(42)
    X = np.random.randn(n_samples, 10)
    y = (X[:, 0] + X[:, 1] ** 2 + np.sin(X[:, 2]) + np.random.randn(n_samples) > 0).astype(int)

    row_indices = np.random.choice(n_samples, 100)
    col_indices = np.random.choice(10, 100)
    X[row_indices, col_indices] = np.nan

    return pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)]), pd.Series(y, name='target')

def train_model():
    X, y = generate_synthetic_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with mlflow.start_run():
        n_estimators = 100
        max_depth = 5
        min_samples_split = 2

        # Create a pipeline with SimpleImputer and RandomForestClassifier
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('rf', RandomForestClassifier(n_estimators=n_estimators,
                                          max_depth=max_depth,
                                          min_samples_split=min_samples_split,
                                          random_state=42))
        ])

        # Fit the pipeline
        pipeline.fit(X_train, y_train)

        # Make predictions
        predictions = pipeline.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)

        # Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("min_samples_split", min_samples_split)
        mlflow.log_param("imputer_strategy", "mean")

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)

        # Log the model
        mlflow.sklearn.log_model(pipeline, "random_forest_model")

        # Log feature importance
        feature_importance = dict(zip(X.columns, pipeline.named_steps['rf'].feature_importances_))
        with open("feature_importance.json", "w") as f:
            json.dump(feature_importance, f)
        mlflow.log_artifact("feature_importance.json", "feature_importance")

        # Log the dataset
        X.to_csv("synthetic_data.csv", index=False)
        mlflow.log_artifact("synthetic_data.csv", "dataset")

        # Log the code
        mlflow.log_artifact("train_model.py", "code")

    print(f"Model metrics: accuracy={accuracy}, precision={precision}, recall={recall}, f1_score={f1}")
    print("Experiment logged in MLflow")

if __name__ == "__main__":
    train_model()
```


Create a Dockerfile for the model training script in the `model_training` directory. Add the following content:

```dockerfile
FROM python:3.8-slim-buster

WORKDIR /app

COPY train_model.py .

RUN pip install mlflow scikit-learn pandas numpy joblib psycopg2-binary boto3

CMD ["python", "train_model.py"]
```



## Step 5: Building Docker Images

### Navigate to the Root Directory

Return to the root directory of your project where the `mlflow_server` and `model_training` directories are located from the terminal.

### Login to Docker account

Login to docker using the follwing command:

```
docker login
```

Provide `username` and `password` of dockerhub to login.

### Build the MLflow Server Docker Image

Build the Docker image for the MLflow server using the Dockerfile created in the `mlflow_server` directory.

```bash
docker build -t <your-registry>/mlflow-server:latest ./mlflow_server
```

Replace `<your-registry>` with your `username` of dockerhub.


### Build the Model Training Docker Image

Build the Docker image for the model training script using the Dockerfile created in the `model_training` directory.

```bash
docker build -t <your-registry>/model-training:latest ./model_training
```

Replace `<your-registry>` with your `username` of dockerhub.


### Push the Images to a Container Registry

Push the built images to your container registry so they can be used in the Kubernetes cluster.

```bash
docker push <your-registry>/mlflow-server:latest
docker push <your-registry>/model-training:latest
```
Replace `<your-registry>` with your `username` of dockerhub.
This step ensures that Kubernetes can pull the images from the registry when deploying the services.

## Step 6: Creating Kubernetes Manifests

Navigate to the `k8s_manifests` Directory. 


### Create a Manifest for the PostgreSQL Deployment

Create a new file named `postgres-deployment.yaml`. Add the following content to define the PostgreSQL deployment and service:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        env:
        - name: POSTGRES_USER
          value: mlflow
        - name: POSTGRES_PASSWORD
          value: mlflow
        - name: POSTGRES_DB
          value: mlflow
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
```

### Create a Manifest for the MLflow Server Deployment

Create a new file named `mlflow-deployment.yaml`. Add the following content:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mlflow
  template:
    metadata:
      labels:
        app: mlflow
    spec:
      containers:
      - name: mlflow
        image: <your-registry>/mlflow-server:latest
        ports:
        - containerPort: 5000
        env:
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: aws-access-key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: aws-secret-access-key
        - name: AWS_DEFAULT_REGION
          value: "ap-southeast-1"

---
apiVersion: v1
kind: Service
metadata:
  name: mlflow
spec:
  type: NodePort
  selector:
    app: mlflow  
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
      nodePort: 30080
```

   Replace `<your-registry>` with your docker `username`.

### Create a Manifest for the Model Training Job

Create a new file named `model-training-job.yaml. Add the following content:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: model-training
spec:
  template:
    spec:
      containers:
      - name: model-training
        image: <your-registry>/model-training:latest
        env:
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: aws-access-key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: aws-secret-access-key
        - name: AWS_DEFAULT_REGION
          value: "ap-southeast-1"
      restartPolicy: OnFailure
  backoffLimit: 4
```

Replace `<your-registry>` with the respective value.

## Step 7: Deploying to Kubernetes

### Create a Kubernetes Secret for AWS Credentials

Store your AWS credentials as a Kubernetes secret for secure access.

```bash
kubectl create secret generic aws-credentials \
    --from-literal=aws-access-key-id=YOUR_AWS_ACCESS_KEY_ID \
    --from-literal=aws-secret-access-key=YOUR_AWS_SECRET_ACCESS_KEY
```

Replace `YOUR_AWS_ACCESS_KEY_ID` and `YOUR_AWS_SECRET_ACCESS_KEY` with your actual AWS credentials.

### Deploy PostgreSQL, MLflow Server, and Model Training Job

Apply each of the Kubernetes manifests to deploy the resources. Wait for one deployment to get to the `running` state before applying the next one to avoid any issues.

```bash
kubectl apply -f postgres-deployment.yaml
kubectl apply -f mlflow-deployment.yaml
kubectl apply -f model-training-job.yaml
```

### Verify the Deployments and Services

Check if the deployments and services are running successfully. Also check the Job for the model training.

```bash
kubectl get all
```

Expected output:

![alt text](./images/image.png)

## Step 8: Expose MLflow and Check Tracking Results

### Setup Load balancer for the MLflow UI

Get the Internal Node-IP of the kubernetes cluster using the following command:

```bash
kubectl get nodes -o wide
```

Expected output:

![alt text](./images/image-2.png)

Now Create a load balancer from poridhi labs with these `nodeIP` and `nodeport` 30080.

![alt text](./images/image-3.png)

Now open the load balancer url in you browser to see the MLflow UI.

![alt text](./images/image-4.png)




### Explore Logged Experiments in the MLflow UI

View the logged metrics, parameters, and artifacts in the MLflow UI, which include:

- **Metrics**: `accuracy`, `precision`, `recall`, `f1_score`.
- **Parameters**: `n_estimators`, `max_depth`, `min_samples_split`.

    ![alt text](./images/image-5.png)

- **Artifacts**: `random_forest_model`, `feature_importance.json`, `synthetic_data.csv`, `train_model.py`.

    ![alt text](./images/image-6.png)

### Verify Artifact Storage in S3

Confirm that the model and data artifacts are stored in the specified S3 bucket using AWS console.

![alt text](./images/image-1.png)



## Step 9: Cleaning Up

### Delete the Kubernetes Resources

Remove all the deployed resources from the Kubernetes cluster.

```bash
kubectl delete -f postgres-deployment.yaml
kubectl delete -f mlflow-deployment.yaml
kubectl delete -f model-training-job.yaml
kubectl delete secret aws-credentials
```

### Verify that All Resources are Deleted

Check that no resources are left running in the cluster:

```bash
kubectl get all
```

   This command should show that no resources (deployments, services, Jobs) are active.

## Conclusion

In this lab, you successfully built and deployed a complete MLOps environment using Kubernetes, MLflow, and S3 integration. You learned how to set up a scalable and manageable machine learning workflow that tracks experiments and stores artifacts in a cloud-native setup. By following these steps, you can now confidently deploy MLOps pipelines in production environments and further optimize your workflows as your machine learning projects scale.

