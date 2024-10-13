# **Containerizing MLFlow Tracking Server with Docker**

In modern machine learning (ML) workflows, managing and tracking experiments, models, and their parameters can become complex. MLflow is an open-source platform that helps manage this complexity by providing tools for tracking experiments, packaging code, and deploying models. One effective way to scale and manage MLflow in an isolated environment is through containerization, which allows you to package and run the MLflow tracking server along with other dependencies in a Docker container.


![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/1684a1a1a84b7218a35a3f43acc6619e3d2d74af/Poridhi%20Labs/MLOps%20Lab/Lab%2007/images/MLOpsLab7.svg)


In this lab, you will learn how to containerize an MLflow Tracking Server using Docker. This environment is suitable for tracking machine learning experiments, and it provides an easy-to-use interface for logging metrics, storing artifacts, and analyzing model results. 


Containerizing the MLflow server enables you to encapsulate the entire environment in a Docker container. This ensures consistency, portability, and reproducibility of your ML environment across different stages of the model's lifecycle, whether you're working locally or deploying it in production.


## Task Description

This lab outlines the step-by-step process of setting up a Docker container with MLflow and a simple machine learning model training script.

### Key Steps:
1. **Setting Up the Project Structure**: Creating a directory for your Docker and Python files.
2. **Creating the Dockerfile**: Setting up a Dockerfile to install Python dependencies, configure MLflow, and prepare the container.
3. **Createing requirements.txt**: A text file containing the requirements.
4. **Developing the Model Training Script**: Writing a Python script that logs model training experiments to MLflow.
5. **Building and Running the Docker Container**: Building the Docker image and running the container with MLflow.
6. **Accessing MLflow UI and Analyzing Results**: Viewing logged experiments, metrics, and artifacts through the MLflow UI.




## Step 1: Setting Up the Project Structure

First, create the directory structure for your project. This structure will contain a folder for MLflow data, a Dockerfile, and a Python script for training the machine learning model.

```bash
mkdir docker-mlops-lab
cd docker-mlops-lab
mkdir mlflow_data
touch Dockerfile
touch requirements.txt
touch train_model.py
```

- `docker-mlops-lab`: The main directory for the project.
- `mlflow_data`: A directory to store MLflow tracking data.
- `Dockerfile`: A file to define how the Docker container will be built.
- `requirements.txt`: A text file containing the required libraries/ packages.
- `train_model.py`: A Python script for training a machine learning model.



## Step 2: Creating the Dockerfile

A Dockerfile defines the environment where the application will run. It contains instructions for setting up the Python environment, installing dependencies, and running the MLflow server.


### Add the following content to the Dockerfile:

```Dockerfile
FROM python:3.8-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the training script
COPY train_model.py .

# Set up MLflow
ENV MLFLOW_TRACKING_URI=/mlflow

# Create a startup script
RUN echo '#!/bin/bash\n\
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri /mlflow_data &\n\
sleep 5\n\
python train_model.py\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]
```

Here’s a concise explanation of the Dockerfile:

### Explanation:

1. **Base Image**:  
   It uses `python:3.8-slim-buster` as a lightweight base image for Python applications.

2. **Working Directory**:  
   The working directory is set to `/app`, where all commands will be executed.

3. **Install System Dependencies**:  
   Essential packages like `gcc` and `libpq-dev` are installed to support compiling Python libraries.

4. **Install Python Dependencies**:  
   The `requirements.txt` file is copied, and the listed dependencies are installed using `pip`.

5. **Copy Training Script**:  
   The `train_model.py` script is copied into the container to execute model training.

6. **Set MLflow Environment**:  
   The environment variable `MLFLOW_TRACKING_URI` is set to `/mlflow`, indicating where MLflow will store tracking data.

7. **Startup Script Creation**:  
   A startup script is created to launch the MLflow server on port 5000 and run the training script. It waits 5 seconds to ensure the server is up before starting the training process.

8. **Run Command**:  
   The container executes the startup script, initiating both the MLflow server and the model training.

## Step 3: Create the `requirements.txt` file

Add the following content to `requirements.txt`:

```
mlflow==1.30.0
scikit-learn==1.0.2
pandas==1.3.5
numpy==1.21.5
matplotlib==3.5.2
seaborn==0.11.2
```

Here’s a concise description of each package:

1. **MLflow**: A platform for managing the machine learning lifecycle, enabling experiment tracking and model deployment.

2. **scikit-learn**: A library for machine learning that provides simple tools for classification, regression, clustering, and more.

3. **pandas**: A data manipulation and analysis library that offers data structures like DataFrames for handling structured data.

4. **numpy**: A foundational library for numerical computing in Python, supporting multi-dimensional arrays and mathematical functions.

5. **matplotlib**: A library for creating static and interactive visualizations in Python, useful for plotting data.

6. **seaborn**: A statistical data visualization library that simplifies the creation of attractive and informative graphics.


## Step 4: Developing the Model Training Script

Now, you will write a Python script that generates synthetic data, trains a model using Scikit-learn, and logs the results to MLflow.

### Open the `train_model.py` file and add the following code:

```python
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def generate_synthetic_data(n_samples=1000):
    np.random.seed(42)
    X = np.random.randn(n_samples, 5)
    y = (X[:, 0] + X[:, 1] ** 2 + np.random.randn(n_samples) > 0).astype(int)
    return pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)]), pd.Series(y, name='target')

def create_pipeline():
    return Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(random_state=42))
    ])

def train_model():
    mlflow.set_tracking_uri("/mlflow_data")
    mlflow.set_experiment("docker_synthetic_classification")

    X, y = generate_synthetic_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = create_pipeline()

    param_grid = {
        'classifier__n_estimators': [100, 200],
        'classifier__max_depth': [5, 10]
    }

    with mlflow.start_run(run_name=f"model_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        print("Starting model training")

        mlflow.log_param("dataset_shape", X.shape)
        mlflow.log_param("dataset_classes", np.unique(y).tolist())

        grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='f1', n_jobs=-1)
        grid_search.fit(X_train, y_train)

        best_params = grid_search.best_params_
        for param, value in best_params.items():
            mlflow.log_param(param, value)

        y_pred = grid_search.predict(X_test)
        y_prob = grid_search.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("roc_auc", roc_auc)

        mlflow.sklearn.log_model(grid_search.best_estimator_, "random_forest_model")

        feature_importance = grid_search.best_estimator_.named_steps['classifier'].feature_importances_
        importance_df = pd.DataFrame({'feature': X.columns, 'importance': feature_importance})
        importance_df = importance_df.sort_values('importance', ascending=False)
        importance_df.to_csv("feature_importance.csv", index=False)
        mlflow.log_artifact("feature_importance.csv", "feature_importance")

        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.savefig("confusion_matrix.png")
        mlflow.log_artifact("confusion_matrix.png", "evaluation")

        fpr, tpr, _ = roc_curve(y_test, y_prob)
        plt.figure(figsize=(10, 8))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend()
        plt.savefig("roc_curve.png")
        mlflow.log_artifact("roc_curve.png", "evaluation")

        print(f"Model metrics: accuracy={accuracy:.4f}, precision={precision:.4f}, "
              f"recall={recall:.4f}, f1_score={f1:.4f}, roc_auc={roc_auc:.4f}")
        print("Experiment logged in MLflow")

if __name__ == "__main__":
    train_model()
```

Here's a concise explanation of the code:

1. **Imports**: The code imports libraries for machine learning, data manipulation, and visualization, including `MLflow` for tracking experiments.

2. **Data Generation**: It generates synthetic data for a binary classification problem with random features.

3. **Pipeline Creation**: A machine learning pipeline is created, which includes feature scaling and a random forest classifier.

4. **Model Training**: The `train_model` function:
   - Sets up MLflow and logs parameters.
   - Splits the data into training and testing sets.
   - Uses `GridSearchCV` to tune hyperparameters and trains the model.
   - Logs metrics like accuracy and precision.
   - Saves the trained model and feature importance.
   - Plots and saves the confusion matrix and ROC curve as artifacts in MLflow.

5. **Execution**: The script runs the `train_model` function when executed, managing the entire machine learning workflow.


## Step 5: Building and Running the Docker Container

1. Build the Docker image:

```bash
docker build -t mlops-lab .
```

2. Run the Docker container, exposing port 5000 for the MLflow UI and mounting the `mlflow_data` directory to persist data:

```bash
docker run -p 5000:5000 -v $(pwd)/mlflow_data:/mlflow mlops-lab
```



## Step 6: Accessing MLflow UI and Analyzing Results
The MLFlow UI is available at `localhost:5000`. But to access the MLflow UI you need to set up a Load Balancer from your Poridhi Lab. 

1. Get IP address using the following command:
    
    ```bash
    hostname -I
    ```

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/1684a1a1a84b7218a35a3f43acc6619e3d2d74af/Poridhi%20Labs/MLOps%20Lab/Lab%2007/images/image.png)
    

2. Create a new Load Balancer with the `IP` from step 1 and `Port` 5000.

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/1684a1a1a84b7218a35a3f43acc6619e3d2d74af/Poridhi%20Labs/MLOps%20Lab/Lab%2007/images/image-1.png)

3. Open the load balancer url in your web browser to access the MLflow UI.

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/1684a1a1a84b7218a35a3f43acc6619e3d2d74af/Poridhi%20Labs/MLOps%20Lab/Lab%2007/images/image-3.png)

4. In the UI, you will see the experiment run that logged the metrics and model.

5. Click on the experiment to explore the logged parameters, metrics, and the trained model.



## **Conclusion**

You have successfully containerized an MLflow tracking server with Docker, built a simple machine learning experiment, and logged results to MLflow. This workflow is fundamental in MLOps practices, and containerization helps ensure the reproducibility of the experiment environment, which is crucial in any machine learning workflow. You can now easily scale, modify, or integrate this setup into your broader machine learning pipeline in production or collaborative environments.