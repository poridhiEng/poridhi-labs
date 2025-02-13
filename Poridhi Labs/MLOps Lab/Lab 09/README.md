# Customer Churn Prediction Tracking with MLflow
This project implements a comprehensive customer churn prediction system using seven different machine learning models. The project uses telco customer churn data to predict whether a customer will discontinue their service. We integrate MLflow for experiment tracking, PostgreSQL for metadata storage, and Amazon S3 for artifact storage.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/3265abfa3be556d1dcbfa3b2e8c9240bd6a065d9/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/mlops-lab-09.svg)

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Environment Setup](#environment-setup)
- [Data Processing & Visualization](#data-processing--visualization)
- [Model Training & MLflow Tracking](#model-training--mlflow-tracking)
- [Verification](#verification)
- [Conclusion](#conclusion)

## Overview
This project implements churn prediction using 7 different ML models, for each model we will track various parameters, metrics, and artifacts with best practices of MLOps. In this project we will use:
- Experiment tracking with MLflow
- Model metadata storage in PostgreSQL
- Artifact storage in AWS S3
- Containerized deployment using Docker
- Comparison of multiple models' performance

## Project Structure
```
customer-churn-mlops/
├── Dockerfile                  
├── docker-compose.yml         
├── Dataset/
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
├── churn_prediction.ipynb
```                  

## Environment Setup

### Configure AWS
```bash
aws configure
```
![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/aws.png?raw=true)

### Create S3 Bucket
```bash
aws s3api create-bucket --bucket <unique-bucket-name> --region ap-southeast-1 --create-bucket-configuration LocationConstraint=ap-southeast-1 

aws s3api put-bucket-versioning --bucket <unique-bucket-name> --versioning-configuration Status=Enabled

aws s3api get-bucket-versioning --bucket <unique-bucket-name>
```

`<unique-bucket-name>` replace with your unique bucket name.

### Kernel Setup

In Poridhi's VSCode server, create a new Jupyter notebook and select on right top corner of the screen `select kernal` and choose `python`.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/kernal.png?raw=true)

### Docker Configuration

With the help of `docker-compose.yml` file, we will create a PostgreSQL database and MLflow server.
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    container_name: mlflow-postgres
    environment:
      - POSTGRES_USER=mlflow
      - POSTGRES_PASSWORD=mlflow
      - POSTGRES_DB=mlflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - mlflow-network
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "mlflow"]
      interval: 5s
      timeout: 5s
      retries: 5

  mlflow:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mlflow-server
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "5000:5000"
    volumes:
      - ./mlflow_data:/mlflow
    environment:
      - AWS_ACCESS_KEY_ID=<your-access-key-id>
      - AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
      - AWS_DEFAULT_REGION=ap-southeast-1
    networks:
      - mlflow-network

networks:
  mlflow-network:
    driver: bridge

volumes:
  postgres_data:
```

`<your-access-key-id>` and `<your-secret-access-key>` replace with your AWS access key ID and secret access key.

#### Dockerfile
```dockerfile
FROM python:3.8-slim-buster

WORKDIR /mlflow

RUN pip install mlflow psycopg2-binary boto3

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "postgresql://mlflow:mlflow@postgres/mlflow", \
     "--default-artifact-root", "s3://<unique-bucket-name>", \
     "--artifacts-destination", "s3://<unique-bucket-name>"]
```

`<unique-bucket-name>` replace with your unique bucket name.
#### Build and run the containers
```bash
docker-compose up --build -d
```

#### Access the MLflow UI
To access the MLflow UI with poridhi's Loadbalancer, use the following steps:

- Find the `eth0` IP address for the `Poridhi's VM` currently you are running by using the command:

  ```bash
  ifconfig
  ```
  ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2005/images/lab-59.png?raw=true)
    
- Go to Poridhi's `LoadBalancer`and Create a `LoadBalancer` with the `eht0` IP and port `5000`.

  ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/lb.png?raw=true)

- By using the Provided `URL` by `LoadBalancer`, you can access the MLflow UI from any browser.

   ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/mlflow.png?raw=true)

## Data Processing & Visualization

### Install required libraries
```bash
pip install numpy pandas matplotlib seaborn plotly imbalanced-learn nbformat ipython xgboost mlflow boto3 kagglehub 
```

### Import libraries
Imports required libraries for data processing, ML training, and MLflow tracking.

```python
# Basic data processing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import kagglehub
import os
import shutil
# Machine Learning
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score,
    recall_score, f1_score,
    classification_report, confusion_matrix
)

# MLflow tracking
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
``` 


### Configure MLflow
```python
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Customer Churn Prediction")
```

### About Dataset

Download the dataset from Kaggle using kagglehub.

```bash
path = kagglehub.dataset_download('blastchar/telco-customer-churn', force_download=True)
destination_path = '/root/code/Dataset'
shutil.copytree(path, destination_path, dirs_exist_ok=True)
```

After running the above code cell, you should see a new folder named `Dataset` in the project directory. Which contains the downloaded dataset `WA_Fn-UseC_-Telco-Customer-Churn.csv`.

**Context**: Predict behavior to retain customers. You can analyze all relevant customer data and develop focused customer retention programs.

**Content**: Each row represents a customer, each column contains customer’s attributes described on the column Metadata.

![](https://images.squarespace-cdn.com/content/v1/588f9607bebafbc786f8c5f8/1607924812500-Y1JR8L6XP5NKF2YPHDUX/image6.png?format=1000w")

The data set includes information about:

- Customers who left within the last month – the column is called Churn
- Services that each customer has signed up for – phone, multiple lines, internet, online security, online backup, device protection, tech support, and streaming TV and movies
- Customer account information – how long they’ve been a customer, contract, payment method, paperless billing, monthly charges, and total charges
- Demographic info about customers – gender, age range, and if they have partners and dependent

### Data Preprocessing & Initial Visualization
Loads the dataset, explores basic information, and creates a correlation heatmap to visualize relationships between numeric features.

```python
# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from plotly.offline import plot, iplot, init_notebook_mode
init_notebook_mode(connected=True)
import plotly.express as px
import plotly.graph_objects as go
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# Load dataset and check basic information
main_df = pd.read_csv("./Dataset/WA_Fn-UseC_-Telco-Customer-Churn.csv")
df = main_df.copy()

# Show basic dataset information
print("Dataset Shape:", df.shape)
print("\nColumns:", df.columns)
df.info()
df.nunique()
df.describe()

# Visualize initial data distribution and correlations
# 1. Correlation Heatmap
plt.figure(figsize=(12, 8))
numeric_df = df.select_dtypes(include=[np.number])
sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
plt.title("Initial Correlation Matrix")
plt.show()
```

### Data Cleaning & Feature Engineering
Cleans the dataset by dropping unnecessary columns, handling missing values, and visualizing relationships between key features.

```python
# Drop unnecessary columns and handle missing values
df = df.drop('customerID', axis=1)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors="coerce")

# Check and visualize missing values
plt.figure(figsize=(10, 6))
sns.heatmap(df.isnull())
plt.title("Null Values Heatmap")
plt.show()

print("Missing Values Count:")
print(df.isnull().sum())

# Handle missing values
df.drop(df[df['TotalCharges'].isnull()].index, inplace=True)
df.reset_index(drop=True, inplace=True)

# Visualize relationships between key features
# 1. Total Charges by Churn
plt.figure(figsize=(5, 5))
sns.barplot(data=df, y="TotalCharges", x="Churn")
plt.title("Total Charges by Churn Status")
plt.show()

# 2. Tenure vs Churn
plt.figure(figsize=(8, 5))
sns.barplot(data=df, x="tenure", y="Churn")
plt.title("Tenure vs Churn")
plt.show()

# 3. Total Charges vs Tenure
fig = px.scatter(df, y="TotalCharges", x="tenure")
fig.update_layout(title="Total Charges vs Tenure")
fig.show()
```

### Data Preprocessing for Categorical Features
Handles categorical value replacements and transformations

```python
# Replace categorical values
df.replace('No internet service', 'No', inplace=True)
df.replace('No phone service', 'No', inplace=True)

# Display unique values in categorical columns
for i in df.columns:
    if df[i].dtypes=="object":
        print(f'{i} : {df[i].unique()}')
        print("****************************************************")

# Convert gender to numeric
df['gender'].replace({'Female':1,'Male':0}, inplace=True)
```

### Churn Analysis Visualizations
Focuses on visualizing churn patterns

```python
# Churn distribution by Senior Citizen status
diag = px.histogram(df, x="Churn", color="SeniorCitizen")
diag.update_layout(width=750, height=550, title="Churn Distribution by Senior Citizen Status")
diag.show()

# Total Charges distribution by Churn
diag = px.pie(df, values='TotalCharges', names='Churn', hole=0.5)
diag.update_layout(title="Total Charges Distribution by Churn")
diag.show()
```

### Service and Contract Analysis Visualizations
Shows distribution of various service features through pie charts. Each chart is a separate pie chart.

```python
# 1. Multiple Lines Distribution
labels = df['MultipleLines'].unique()
values = df['MultipleLines'].value_counts()
diag = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0.1, 0.2])])
diag.update_layout(
    title="Multiple Lines Distribution",
    width=600, height=400
)
diag.show()

# 2. Internet Service Distribution
labels = df['InternetService'].unique()
values = df['InternetService'].value_counts()
diag = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0.2, 0.3])])
diag.update_layout(
    title="Internet Service Distribution",
    width=600, height=400
)
diag.show()

# 3. Payment Method Distribution
labels = df['PaymentMethod'].unique()
values = df['PaymentMethod'].value_counts()
diag = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0, 0.2, 0])])
diag.update_layout(
    title="Payment Method Distribution",
    width=600, height=400
)
diag.show()

# 4. Contract Type Distribution
labels = df['Contract'].unique()
values = df['Contract'].value_counts()
diag = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0.2, 0.3])])
diag.update_layout(
    title="Contract Type Distribution",
    width=600, height=400
)
diag.show()
```

### Feature Engineering
Performs one-hot encoding for multi-category variables and scales numerical features. One-hot encoding is used to convert categorical variables into numerical format, which is necessary for machine learning algorithms.

```python
# One-hot encoding for multi-category variables
# Handle variables with more than 2 categories
more_than_2 = ['InternetService' ,'Contract' ,'PaymentMethod']
df = pd.get_dummies(data=df, columns=more_than_2)

# Feature scaling for numerical columns
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

# Scale continuous variables
large_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
df[large_cols] = scaler.fit_transform(df[large_cols])

# Convert binary categories to numeric
two_cate = ['Partner', 'Dependents', 'PhoneService', 'MultipleLines', 
            'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 
            'TechSupport', 'StreamingTV', 'StreamingMovies', 
            'PaperlessBilling', 'Churn']
for i in two_cate:
    df[i].replace({"No":0, "Yes":1}, inplace=True)
```

### Final Data Processing and Analysis
Visualizes final correlations after feature engineering and splits the data into features and target.

```python
# Visualize final correlations after feature engineering
plt.figure(figsize=(15, 10))
sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Final Correlation Matrix After Preprocessing")
plt.show()

# Split features and target
print("Preparing features and target...")
X = df.drop('Churn', axis=1)
y = df['Churn']

print("\nFeature set shape:", X.shape)
print("Target shape:", y.shape)

# Split data into training and testing sets
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.33, 
    random_state=42
)

print("\nTraining set shape:", X_train.shape)
print("Testing set shape:", X_test.shape)
```

## Model Training & MLflow Tracking

For training the Customer Churn Prediction model, we will use 7 different ML models. For each model we will track various parameters, metrics, and artifacts with best practices of MLOps.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/752b0f1d4da0f7e8b6ecd2088bc27cb47b3accc7/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/models.svg)

### Logistic Regression  
 
Implements logistic regression for binary classification. Tracks parameters, metrics, and artifacts using MLflow.

**MLflow Tracking:**  
- **Parameters:** `max_iter`, `random_state`, `n_jobs`  
- **Metrics:** Accuracy, Precision, Recall, F1 Score  
- **Artifacts:** Confusion Matrix, Classification Report, Trained Model  

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import mlflow
from mlflow.models import infer_signature

with mlflow.start_run(run_name="logistic_regression"):
    # Create and train model
    model_lg = LogisticRegression(max_iter=120, random_state=0, n_jobs=20)
    
    # Log parameters
    mlflow.log_params({
        "max_iter": 120,
        "random_state": 0,
        "n_jobs": 20
    })
    
    # Train model
    model_lg.fit(X_train, y_train)
    
    # Make predictions
    pred_lg = model_lg.predict(X_test)
    
    # Calculate and log accuracy
    lg = round(accuracy_score(y_test, pred_lg) * 100, 2)
    mlflow.log_metric("accuracy", lg)
    
    # Log classification report
    clf_report = classification_report(y_test, pred_lg)
    with open("lg_classification_report.txt", "w") as f:
        f.write(clf_report)
    mlflow.log_artifact("lg_classification_report.txt")
    
    # Create and log confusion matrix
    plt.figure(figsize=(8, 6))
    cm1 = confusion_matrix(y_test, pred_lg)
    sns.heatmap(cm1 / np.sum(cm1), annot=True, fmt='.2%', cmap="Reds")
    plt.title("Logistic Regression Confusion Matrix")
    plt.savefig("lg_confusion_matrix.png")
    plt.close()
    mlflow.log_artifact("lg_confusion_matrix.png")
    
    # Calculate and log additional metrics
    precision = precision_score(y_test, pred_lg)
    recall = recall_score(y_test, pred_lg)
    f1 = f1_score(y_test, pred_lg)
    mlflow.log_metrics({
        "precision": precision,
        "recall": recall,
        "f1": f1
    })
    
    # Log the model
    signature = infer_signature(X_train, pred_lg)
    mlflow.sklearn.log_model(model_lg, "logistic_regression_model", signature=signature)

print(f"Logistic Regression Accuracy: {lg}%")
print("\nClassification Report:")
print(clf_report)
```
### Decision Tree  

Trains a decision tree classifier for binary classification. Tracks parameters, metrics, and artifacts using MLflow.

**MLflow Tracking:**  
- **Parameters:** `max_depth`, `random_state`  
- **Metrics:** Accuracy, Precision, Recall, F1 Score  
- **Artifacts:** Confusion Matrix, Classification Report, Trained Model  

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import mlflow
from mlflow.models import infer_signature

with mlflow.start_run(run_name="decision_tree"):
    # Create and train model
    model_dt = DecisionTreeClassifier(max_depth=4, random_state=42)
    
    # Log parameters
    mlflow.log_params({
        "max_depth": 4,
        "random_state": 42
    })
    
    # Train model
    model_dt.fit(X_train, y_train)
    
    # Make predictions
    pred_dt = model_dt.predict(X_test)
    
    # Calculate and log accuracy
    dt = round(accuracy_score(y_test, pred_dt) * 100, 2)
    mlflow.log_metric("accuracy", dt)
    
    # Log classification report
    clf_report = classification_report(y_test, pred_dt)
    with open("dt_classification_report.txt", "w") as f:
        f.write(clf_report)
    mlflow.log_artifact("dt_classification_report.txt")
    
    # Create and log confusion matrix
    plt.figure(figsize=(8, 6))
    cm2 = confusion_matrix(y_test, pred_dt)
    sns.heatmap(cm2 / np.sum(cm2), annot=True, fmt='.2%', cmap="Reds")
    plt.title("Decision Tree Classifier Confusion Matrix")
    plt.savefig("dt_confusion_matrix.png")
    plt.close()
    mlflow.log_artifact("dt_confusion_matrix.png")
    
    # Calculate and log additional metrics
    precision = precision_score(y_test, pred_dt, average="weighted")
    recall = recall_score(y_test, pred_dt, average="weighted")
    f1 = f1_score(y_test, pred_dt, average="weighted")
    mlflow.log_metrics({
        "precision": precision,
        "recall": recall,
        "f1": f1
    })
    
    # Log the model
    signature = infer_signature(X_train, pred_dt)
    mlflow.sklearn.log_model(model_dt, "decision_tree_model", signature=signature)

print(f"Decision Tree Accuracy: {dt}%")
print("\nClassification Report:")
print(clf_report)
```

### Random Forest  

Trains a random forest classifier for binary classification. Tracks parameters, metrics, and artifacts using MLflow.

**MLflow Tracking:**  
- **Parameters:** `n_estimators`, `min_samples_leaf`, `random_state`  
- **Metrics:** Accuracy, Precision, Recall, F1 Score  
- **Artifacts:** Confusion Matrix, Classification Report, Feature Importance, Trained Model

```python
from sklearn.ensemble import RandomForestClassifier

with mlflow.start_run(run_name="random_forest"):
    # Create and train model
    model_rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=0.16, random_state=42)
    
    # Log parameters
    mlflow.log_params({
        "n_estimators": 300,
        "min_samples_leaf": 0.16,
        "random_state": 42
    })
    
    # Train model
    model_rf.fit(X_train, y_train)
    
    # Make predictions
    pred_rf = model_rf.predict(X_test)
    
    # Calculate and log accuracy
    rf = round(accuracy_score(y_test, pred_rf) * 100, 2)
    mlflow.log_metric("accuracy", rf)
    
    # Log classification report
    clf_report = classification_report(y_test, pred_rf)
    with open("rf_classification_report.txt", "w") as f:
        f.write(clf_report)
    mlflow.log_artifact("rf_classification_report.txt")
    
    # Create and log confusion matrix
    plt.figure(figsize=(8, 6))
    cm3 = confusion_matrix(y_test, pred_rf)
    sns.heatmap(cm3 / np.sum(cm3), annot=True, fmt='.2%', cmap="Reds")
    plt.title("Random Forest Confusion Matrix")
    plt.savefig("rf_confusion_matrix.png")
    plt.close()
    mlflow.log_artifact("rf_confusion_matrix.png")
    
    # Calculate and log additional metrics
    precision = precision_score(y_test, pred_rf, average="weighted")
    recall = recall_score(y_test, pred_rf, average="weighted")
    f1 = f1_score(y_test, pred_rf, average="weighted")
    mlflow.log_metrics({
        "precision": precision,
        "recall": recall,
        "f1": f1
    })
    
    # Log feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model_rf.feature_importances_
    }).sort_values('importance', ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(x='importance', y='feature', data=feature_importance.head(10))
    plt.title("Top 10 Feature Importance - Random Forest")
    plt.savefig("rf_feature_importance.png")
    plt.close()
    mlflow.log_artifact("rf_feature_importance.png")
    
    # Log the model
    signature = infer_signature(X_train, pred_rf)
    mlflow.sklearn.log_model(model_rf, "random_forest_model", signature=signature)

print(f"Random Forest Metrics: Accuracy={rf}%, Precision={precision}, Recall={recall}, F1={f1}")
```

### XGBoost  

Trains an XGBoost classifier for binary classification. Tracks parameters, metrics, and artifacts using MLflow.

**MLflow Tracking:**  
- **Parameters:** `max_depth`, `n_estimators`, `learning_rate`, `random_state`, `n_jobs`  
- **Metrics:** Accuracy, Precision, Recall, F1 Score  
- **Artifacts:** Confusion Matrix, Classification Report, Trained Model  

```python
from xgboost import XGBClassifier

with mlflow.start_run(run_name="xgboost"):
    # Create and train model
    model_xgb = XGBClassifier(max_depth=8, n_estimators=125, random_state=0, 
                              learning_rate=0.03, n_jobs=5)
    
    # Log parameters
    mlflow.log_params({
        "max_depth": 8,
        "n_estimators": 125,
        "learning_rate": 0.03,
        "random_state": 0,
        "n_jobs": 5
    })
    
    # Train model
    model_xgb.fit(X_train, y_train)
    
    # Make predictions
    pred_xgb = model_xgb.predict(X_test)
    
    # Calculate and log accuracy
    xgb = round(accuracy_score(y_test, pred_xgb) * 100, 2)
    mlflow.log_metric("accuracy", xgb)
    
    # Log classification report
    clf_report = classification_report(y_test, pred_xgb)
    with open("xgb_classification_report.txt", "w") as f:
        f.write(clf_report)
    mlflow.log_artifact("xgb_classification_report.txt")
    
    # Log confusion matrix
    plt.figure(figsize=(8, 6))
    cm4 = confusion_matrix(y_test, pred_xgb)
    sns.heatmap(cm4 / np.sum(cm4), annot=True, fmt='.2%', cmap="Reds")
    plt.title("XGBoost Confusion Matrix")
    plt.savefig("xgb_confusion_matrix.png")
    plt.close()
    mlflow.log_artifact("xgb_confusion_matrix.png")
    
    # Log model
    signature = infer_signature(X_train, pred_xgb)
    mlflow.sklearn.log_model(model_xgb, "xgboost_model", signature=signature)

print(f"XGBoost Metrics: Accuracy={xgb}%, Precision={precision}, Recall={recall}, F1={f1}")
```
### KNeighborsClassifier  

Trains a KNeighbors classifier for binary classification. Tracks parameters, metrics, and artifacts using MLflow.

**MLflow Tracking:**  
- **Parameters:** `n_neighbors`, `leaf_size`  
- **Metrics:** Accuracy, Precision, Recall, F1 Score  
- **Artifacts:** Confusion Matrix, Classification Report, Trained Model  

```python
from sklearn.neighbors import KNeighborsClassifier

with mlflow.start_run(run_name="kneighbors"):
    # Create model
    model_kn = KNeighborsClassifier(n_neighbors=9, leaf_size=20)
    
    # Log parameters
    mlflow.log_params({
        "n_neighbors": 9,
        "leaf_size": 20
    })
    
    # Train model
    model_kn.fit(X_train, y_train)
    
    # Make predictions
    pred_kn = model_kn.predict(X_test)
    
    # Calculate and log accuracy
    kn = round(accuracy_score(y_test, pred_kn) * 100, 2)
    mlflow.log_metric("accuracy", kn)
    
    # Log classification report
    clf_report = classification_report(y_test, pred_kn)
    with open("kn_classification_report.txt", "w") as f:
        f.write(clf_report)
    mlflow.log_artifact("kn_classification_report.txt")
    
    # Log confusion matrix
    plt.figure(figsize=(8, 6))
    cm5 = confusion_matrix(y_test, pred_kn)
    sns.heatmap(cm5 / np.sum(cm5), annot=True, fmt='.2%', cmap="Reds")
    plt.title("KNeighbors Confusion Matrix")
    plt.savefig("kn_confusion_matrix.png")
    plt.close()
    mlflow.log_artifact("kn_confusion_matrix.png")
    
    # Log model
    signature = infer_signature(X_train, pred_kn)
    mlflow.sklearn.log_model(model_kn, "kneighbors_model", signature=signature)

print(f"KNeighbors Metrics: Accuracy={kn}%, Precision={precision}, Recall={recall}, F1={f1}")
```
### SVM  

Trains a Support Vector Machine (SVM) classifier using the RBF kernel for binary classification. Tracks parameters, metrics, and artifacts with MLflow.

**MLflow Tracking:**  
- **Parameters:** `kernel`, `random_state`  
- **Metrics:** Accuracy, Precision, Recall, F1 Score  
- **Artifacts:** Confusion Matrix, Classification Report, Trained Model  

```python
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import mlflow
from mlflow.models import infer_signature

with mlflow.start_run(run_name="svm_classifier"):
    # Create and train model
    model_svm = SVC(kernel='rbf', random_state=42)
    
    # Log parameters
    mlflow.log_params({
        "kernel": "rbf",
        "random_state": 42
    })
    
    # Train model
    model_svm.fit(X_train, y_train)
    
    # Make predictions
    pred_svm = model_svm.predict(X_test)
    
    # Calculate and log accuracy
    sv = round(accuracy_score(y_test, pred_svm)*100, 2)
    mlflow.log_metric("accuracy", sv)
    
    # Log classification report
    clf_report = classification_report(y_test, pred_svm)
    with open("svm_classification_report.txt", "w") as f:
        f.write(clf_report)
    mlflow.log_artifact("svm_classification_report.txt")
    
    # Create and log confusion matrix
    plt.figure(figsize=(8, 6))
    cm6 = confusion_matrix(y_test, pred_svm)
    sns.heatmap(cm6/np.sum(cm6), annot=True, fmt='0.2%', cmap="Reds")
    plt.title("SVM Classifier Confusion Matrix")
    plt.savefig("svm_confusion_matrix.png")
    plt.close()
    mlflow.log_artifact("svm_confusion_matrix.png")
    
    # Log additional metrics
    mlflow.log_metrics({
        "precision": precision_score(y_test, pred_svm),
        "recall": recall_score(y_test, pred_svm),
        "f1": f1_score(y_test, pred_svm)
    })
    
    # Log the model
    signature = infer_signature(X_train, pred_svm)
    mlflow.sklearn.log_model(model_svm, "svm_model", signature=signature)

print(f"SVM Classifier Accuracy: {sv}%")
print("\nClassification Report:")
print(classification_report(y_test, pred_svm))
```
### AdaBoost Classifier  

Trains an AdaBoost classifier for binary classification. Tracks parameters, metrics, and artifacts with MLflow.

**MLflow Tracking:**  
- **Parameters:** `learning_rate`, `n_estimators`, `random_state`  
- **Metrics:** Accuracy, Precision, Recall, F1 Score  
- **Artifacts:** Confusion Matrix, Classification Report, Feature Importance, Trained Model  

```python
from sklearn.ensemble import AdaBoostClassifier

with mlflow.start_run(run_name="adaboost"):
    # Create model
    model_ada = AdaBoostClassifier(
        learning_rate=0.002,
        n_estimators=205,
        random_state=42
    )
    
    # Log parameters
    mlflow.log_params({
        "learning_rate": 0.002,
        "n_estimators": 205,
        "random_state": 42
    })
    
    # Train model
    model_ada.fit(X_train, y_train)
    
    # Make predictions
    pred_ada = model_ada.predict(X_test)
    
    # Calculate and log accuracy
    ada = round(accuracy_score(y_test, pred_ada) * 100, 2)
    mlflow.log_metric("accuracy", ada)
    
    # Log classification report
    clf_report = classification_report(y_test, pred_ada)
    with open("ada_classification_report.txt", "w") as f:
        f.write(clf_report)
    mlflow.log_artifact("ada_classification_report.txt")
    
    # Log confusion matrix
    plt.figure(figsize=(8, 6))
    cm7 = confusion_matrix(y_test, pred_ada)
    sns.heatmap(cm7 / np.sum(cm7), annot=True, fmt='.2%', cmap="Reds")
    plt.title("AdaBoost Confusion Matrix")
    plt.savefig("ada_confusion_matrix.png")
    plt.close()
    mlflow.log_artifact("ada_confusion_matrix.png")
    
    # Log feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model_ada.feature_importances_
    }).sort_values('importance', ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(x='importance', y='feature', data=feature_importance.head(10))
    plt.title("Top 10 Feature Importance - AdaBoost")
    plt.savefig("ada_feature_importance.png")
    plt.close()
    mlflow.log_artifact("ada_feature_importance.png")
    
    # Log model
    signature = infer_signature(X_train, pred_ada)
    mlflow.sklearn.log_model(model_ada, "adaboost_model", signature=signature)

print(f"AdaBoost Metrics: Accuracy={ada}%, Precision={precision}, Recall={recall}, F1={f1}")
```

### Model Comparison

To compare the performance of different models, we will create a bar plot visualization and CSV files with accuracy metrics. For this we will use the accuracy scores of each model.

```python
# Create and log model comparison visualization in MLflow
with mlflow.start_run(run_name="model_comparison"):
    # Create DataFrame with model performances
    models = pd.DataFrame({
        'Model': ['Logistic Regression', 'Decision Tree', 'Random Forest', 
                'XGBoost', 'KNN', 'SVM', 'AdaBoost'],
        'Accuracy': [lg, dt, rf, xgb, kn, sv, ada]
    })
    
    # Create comparison plot
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Accuracy', y='Model', data=models)
    plt.title('Model Performance Comparison')
    plt.xlabel('Accuracy Score (%)')
    plt.ylabel('Models')
    
    # Save plot
    plt.savefig("model_comparison.png")
    plt.close()
    
    # Log the comparison plot
    mlflow.log_artifact("model_comparison.png")
    
    # Log individual model accuracies
    for model, accuracy in zip(models['Model'], models['Accuracy']):
        mlflow.log_metric(f"{model.lower().replace(' ', '_')}_accuracy", accuracy)
    
    # Log the comparison table as CSV
    models.to_csv("model_comparison.csv", index=False)
    mlflow.log_artifact("model_comparison.csv")
    
    # Create and log sorted accuracies table
    sorted_models = models.sort_values(by='Accuracy', ascending=False)
    print("\nModel Accuracies Ranked:")
    print(sorted_models)
    
    # Save sorted results
    sorted_models.to_csv("sorted_model_comparison.csv", index=False)
    mlflow.log_artifact("sorted_model_comparison.csv")
```

### Register Best Model

To register the best model, we will use the `MlflowClient` to search for the best run based on accuracy and then register the model from the best run to the model registry and transition it to the 'Production' stage.

```python
from mlflow.tracking import MlflowClient

def register_best_model(experiment_name="Customer Churn Prediction"):
    """
    Registers the best-performing model from the MLflow experiment
    to the model registry and transitions it to the 'Production' stage.
    """
    client = MlflowClient()
    
    # Retrieve experiment details
    experiment = client.get_experiment_by_name(experiment_name)
    if not experiment:
        raise ValueError(f"Experiment '{experiment_name}' not found.")
    
    # Identify the best run based on a key metric (e.g., accuracy)
    best_run = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.accuracy DESC"]
    )[0]
    
    # Register the model from the best run
    model_uri = f"runs:/{best_run.info.run_id}/model"
    model_name = "customer_churn_prediction_model"
    model_version = mlflow.register_model(model_uri, model_name)
    
    # Transition the model to the 'Production' stage
    client.transition_model_version_stage(
        name=model_name,
        version=model_version.version,
        stage="Production"
    )
    
    print(f"Model {model_name} version {model_version.version} is now in 'Production' stage.")
    return model_version

# Call the function after model training and comparison
best_model_version = register_best_model()
print(f"Registered model version: {best_model_version.version}")
```

## Verification 

### Model Tracking Verification in MLflow
1. Navigate to the MLflow UI with url provided by the `Poridhi's Loadbalancer`.
2. Navigate to "Experiments" tab and select "Customer Churn Prediction-lab-01"

    ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/1.png?raw=true)

3. For each model run, verify the parameters, metrics, and artifacts.For example we can see the overview, metrics & artifacts for `SVM`:

    **Overview of `SVM`**:

    ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/svm-1.png?raw=true)

    **Model Metrics**:

    ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/svm-2.png?raw=true)

    **Artifacts**:

    ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/svm-3.png?raw=true)

    By following the above steps, you can verify the parameters, metrics, and artifacts for other models as well.

### Model Comparison Verification

In the MLflow UI, navigate to "Model Comparison" experiment and verify the comparison plot and CSV files with accuracy metrics.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/image.png?raw=true)

### Register Best Model Verification

In the MLflow UI, navigate to "Model Registry" and verify the registered model and its version in the "Production" stage.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/bestmodel.png?raw=true)

### S3 Artifact Verification

Go to AWS Console and navigate to S3 bucket `<your-bucket-name>` to verify the artifacts.

![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/s3.png?raw=true)

For each model run, you should see the artifacts in the S3 bucket.

### PostgreSQL Verification

1. Connect to the PostgreSQL container:
    ```sh
    docker exec -it <postgres-container-id> /bin/sh
    ```

2. Connect to PostgreSQL:
    ```sql
    psql -h localhost -U mlflow -d mlflow

    -- View experiments
    SELECT * FROM experiments;
    ```

    ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/psql.png?raw=true)

3. View runs and metrics:
    ```sql
    SELECT 
        r.run_uuid,
        r.experiment_id,
        m.key as metric_name,
        m.value as metric_value
    FROM runs r
    JOIN metrics m ON r.run_uuid = m.run_uuid
    WHERE r.experiment_id = '1'
    ORDER BY r.start_time DESC;
    ```

    ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2009/images/psql-2.png?raw=true)


## Conclusion
In this lab, we implemented a complete MLOps pipeline for a customer churn prediction problem. We used MLflow for model tracking, S3 for artifact storage, and PostgreSQL for metadata storage for each model run. The visualization analysis revealed important insights about customer churn patterns, particularly its relationship with service usage, payment methods, and contract types.
