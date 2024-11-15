# Market Value Prediction Tracking with MLflow

This project implements a comprehensive player market value prediction system using XGBoost Regressor. The project uses football/soccer player data to predict player market values. We integrate MLflow for experiment tracking, PostgreSQL for metadata storage, and Amazon S3 for artifact storage.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/d69c7f66cd31eaae413123799dc1c7b44c2357bc/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/Arch-diagram-11.svg)

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Environment Setup](#environment-setup)
4. [Data Processing & Visualization](#data-processing--visualization)
5. [Model Training & MLflow Tracking](#model-training--mlflow-tracking)
6. [Model lifecycle management](#model-lifecycle-management)
6. [Verification](#verification)
7. [Conclusion](#conclusion)

## Overview

This project implements player market value prediction using XGBoost Regressor while incorporating MLOps best practices:

- Experiment tracking with MLflow
- Model metadata storage in PostgreSQL
- Artifact storage in AWS S3
- Comprehensive data visualization and preprocessing
- Feature importance analysis
- Model performance evaluation

## Project Structure

```
market-value-prediction/
├── Dataset/
│   └── top5_leagues_player.csv
├── mlflow_data/
├── mlruns/
├── docker-compose.yml
├── Dockerfile
├── feature_importance.png
├── grid_search_results.png
├── prediction_scatter.png
└── market-value.ipynb
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

Change the `<unique-bucket-name>` to your own bucket name.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/image.png)

### Kernel Setup

In Poridhi's VSCode server, create a new Jupyter notebook. Open notebook and select the `Python 3.8.10` kernel to run the code.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/5.png)

### Docker Configuration

Create `docker-compose.yml` file:
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

Change the `<your-access-key-id>` and `<your-secret-access-key>` to your own AWS credentials provided in the lab.

Key Features:
1. PostgreSQL for metadata storage
2. MLflow server with S3 integration
3. Environment variable management
4. Health checks
5. Data persistence

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

Change the `<unique-bucket-name>` to your own bucket name.

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

## Data Processing & Visualization

### Dataset Overview

The dataset contains information about football players including:

- Basic information (age, height, position)
- Contract details (expiration, club)
- Market value (target variable)
- League information
- Physical attributes
- Agent and outfitter information

### Data Preprocessing Steps

#### 1. Install necessary libraries

```python
pip install numpy pandas matplotlib xgboost seaborn mlflow boto3 kagglehub
```

#### 2. Import libraries

```python
import numpy as np 
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import xgboost 
from sklearn.model_selection import GridSearchCV
import mlflow
import mlflow.xgboost
from mlflow.models import infer_signature
from datetime import datetime
```

#### 3. Load player data from Kaggle

```python
import kagglehub
import os
import shutil
path = kagglehub.dataset_download('oles04/top-leagues-player', force_download=True)
destination_path = '/root/code/market-value-prediction/Dataset'
shutil.copytree(path, destination_path, dirs_exist_ok=True)

df_players = pd.read_csv('./Dataset/top5_leagues_player.csv', index_col = [0])
df_players.head()
```

#### 4. Dataset description

```python
df_players.describe()
```

Generates a statistical summary of the numerical columns in the df_players DataFrame, including mean, standard deviation, and percentiles.

```python
df_players.info()
```

Displays a concise summary of the df_players DataFrame, including column names, data types, non-null counts, and memory usage.

#### 5. NAN value handling

Replace excessive NaN values in two columns with the string 'none', making it easier to drop rows with remaining NaN values.

```python
# filter columns with empty values
empty_cols = df_players.columns[df_players.isna().any()].tolist()

# create separate df only with columns which consist empty values
df_isnull = df_players[empty_cols]

print(df_isnull.isnull().sum())
```

This small table shows that there are three columns to handle. The remaining amount is too small, so we can drop it. These three columns can also be reduced because the full name is unnecessary for predictions. At least the columns 'player_agent' and 'outfitter' need to be handled.

```python
df_players = df_players.dropna(subset=['contract_expires', 'foot', 'height', 'foot', 'price', 'max_price'])
df_players.shape
```

Create a heatmap to visually represent missing values (NaN) in the df_isnull DataFrame, where missing values are highlighted for easy identification.

```python
sns.heatmap(df_isnull.isnull())
```

### Feature Engineering

#### 1. Look into the critical columns

```python
plt.figure(figsize=(8,5))

outfitter_counts = df_isnull['outfitter'].value_counts()


# Convert outfitter_counts to a DataFrame
outfitter_counts_df = outfitter_counts.reset_index()
outfitter_counts_df.columns = ['outfitter', 'count']  # Rename columns for clarity

# Plot using the new DataFrame
sns.barplot(data=outfitter_counts_df, x='outfitter', y='count')

# Rotate the x-axis labels by 90 degrees
ax = plt.gca()
ax.tick_params(axis='x', labelrotation=90)
```

#### 2. For the 'player_agent' only the top 10 and the bottom 10 

```python
plt.figure(figsize=(8,8))

# Get only top 10 and last 10 counts
outfitter_counts = df_isnull['player_agent'].value_counts()
top_10 = outfitter_counts.head(10)
last_10 = outfitter_counts.tail(10)
plot_data = pd.concat([top_10, last_10]).reset_index()

# Rename columns for clarity
plot_data.columns = ['player_agent', 'count']

# Plot using the new DataFrame
sns.barplot(data=plot_data, x='count', y='player_agent')

# Rotate the y-axis labels by 90 degrees, if desired
plt.xticks(rotation=90)
plt.show()
```

```python
# should be valid because only 'player_agent' and 'outfitter' have nan values
df_players = df_players.replace(np.nan, 'unknown')
```

```python
df_players.head()
```

#### 3. Feature tracking

```python
def plotting(df, feature):
    df_mean = df.groupby(feature)['price'].mean().reset_index()
    sns.barplot(data=df_mean, x=feature, y='price')

    # Rotate the x-axis labels by 90 degrees
    ax = plt.gca()
    ax.tick_params(axis='x', labelrotation=90)
    plt.ylabel('mean price in million')
    plt.show()

def plottingLine(df, feature):
    sns.lineplot(data=df, x=feature, y='price')
    plt.ylabel('mean price in million')
    plt.show()
    

feature_list = ['league', 'foot', 'position', 'contract_expires', 'outfitter']

numarical_features = ['age', 'height', 'shirt_nr']

for feature in numarical_features:
    plottingLine(df_players, feature)

for feature in feature_list:
    plotting(df_players, feature)	
```

```python
# Select only numeric columns for correlation
numeric_df = df_players.select_dtypes(include='number')

# Plot the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(numeric_df.corr(), annot=True, linewidth=5)
plt.show()
```

#### 4. Variable Usefulness for Predicting Price

```python
df_target = df_players[['price']]
df_features = df_players[['age', 'height', 'league','foot', 'position', 'club',
                        'contract_expires', 'joined_club', 'player_agent', 'outfitter', 'nationality']]
```

#### 5. One Hot Encoding

```python
for column in df_features.columns:
    unique_values = df_features[column].unique()
    print(f"Unique values in column '{column}': {unique_values}")
```

```python
columns_to_encode = ['league' ,'foot', 'position', 'club', 'contract_expires', 'joined_club', 'player_agent', 'outfitter', 'nationality']

ct = ColumnTransformer(transformers=[('encoder', OneHotEncoder(), columns_to_encode)], remainder='passthrough')

df_features_encoded = ct.fit_transform(df_features)

df_features_encoded.shape
```

#### 6. Train and Test Split

```python
x_train, x_test, y_train, y_test = train_test_split(df_features_encoded, df_target, test_size = 0.3, random_state=22)

y_train = y_train.values.ravel()
y_test = y_test.values.ravel()

print(f'x_train: {x_train.shape}')
print(f'x_test: {x_test.shape}')
print(f'y_train: {y_train.shape}')
print(f'y_test: {y_test.shape}')
```

## Model Training & MLflow Tracking

### Set MLflow configuration

```python
# Set MLflow tracking URI
mlflow.set_tracking_uri("http://localhost:5000")
# Set experiment name
mlflow.set_experiment("market_value_prediction")
```

### Hyperparameter tuning

```python
param_grid = {'nthread':[4], 
              'objective':['reg:squarederror'],
              'learning_rate': [0.03, 0.05],
              'max_depth': [4, 7],
              'min_child_weight': [2,3,4],
              'subsample': [0.5, 0.3],
              'colsample_bytree': [0.7],
              'n_estimators': [300]}

param_grid
```

### MLflow run for grid search

- Performs hyperparameter tuning using GridSearchCV
- Tests multiple combinations of parameters for XGBoost model
- Tracks parameter combinations and their performance
- Creates visualization of parameter search results
- Finds and saves best performing parameters


```python
with mlflow.start_run(run_name=f"grid_search_{datetime.now().strftime('%Y%m%d_%H%M')}"):
    # Log the search space
    mlflow.log_params({"search_space": str(param_grid)})
    
    xgb = xgboost.XGBRegressor(objective='reg:linear')
    grid_search = GridSearchCV(
        estimator=xgb, 
        param_grid=param_grid, 
        scoring='neg_root_mean_squared_error', 
        cv=4
    )
    
    grid_search.fit(x_train, y_train)
    
    # Log best parameters
    mlflow.log_params(grid_search.best_params_)
    
    # Log best score
    mlflow.log_metric("best_cv_score", -grid_search.best_score_)
    
    # Create and save parameter comparison plot
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(grid_search.cv_results_['mean_test_score'])), 
            grid_search.cv_results_['mean_test_score'], 
            marker='o')
    plt.xlabel('Parameter Combination')
    plt.ylabel('Negative Root Mean Squared Error')
    plt.title('Grid Search Results')
    plt.xticks(range(len(grid_search.cv_results_['params'])), 
              grid_search.cv_results_['params'], 
              rotation=90)
    
    # Save plot as artifact
    plt.savefig("grid_search_results.png")
    mlflow.log_artifact("grid_search_results.png")
    plt.show()

best_params = grid_search.best_params_
```

MLflow in this code is tracking and logging the hyperparameter tuning process for future reference and reproducibility. When conducting grid search to find optimal hyperparameters for the XGBoost model, MLflow records the entire parameter search space, the best parameters found, and the corresponding performance metrics. It also stores visualizations showing how different parameter combinations performed. This automated logging creates a comprehensive record that helps compare different experiments, reproduce successful results, and understand which parameters worked best.

### MLflow run for model training and evaluation

- Uses best parameters from grid search to train final model
- Records training data characteristics
- Tracks model performance metrics on both train/test sets
- Creates visualizations for feature importance and predictions
- Registers final model with input/output signature for deployment
- Saves model artifacts and metrics for future reference

```python

with mlflow.start_run(run_name=f"model_training_{datetime.now().strftime('%Y%m%d_%H%M')}"):
    # Log training dataset info
    mlflow.log_param("training_samples", x_train.shape[0])
    mlflow.log_param("features_count", x_train.shape[1])
    
    # Log best parameters again in this run
    mlflow.log_params(best_params)
    
    # Create and train model
    best_xgb = xgboost.XGBRegressor(**best_params)
    best_xgb.fit(x_train, y_train)
    
    # Make predictions
    train_predictions = best_xgb.predict(x_train)
    test_predictions = best_xgb.predict(x_test)
    
    # Calculate and log metrics
    metrics = {
        "train_mae": mean_absolute_error(y_train, train_predictions),
        "test_mae": mean_absolute_error(y_test, test_predictions),
        "train_mse": mean_squared_error(y_train, train_predictions),
        "test_mse": mean_squared_error(y_test, test_predictions),
        "train_rmse": np.sqrt(mean_squared_error(y_train, train_predictions)),
        "test_rmse": np.sqrt(mean_squared_error(y_test, test_predictions))
    }
    
    mlflow.log_metrics(metrics)
    
    # Feature importance plot
    plt.figure(figsize=(10, 6))
    xgboost.plot_importance(best_xgb, max_num_features=20)
    plt.title("Feature Importance")
    plt.tight_layout()
    plt.savefig("feature_importance.png")
    mlflow.log_artifact("feature_importance.png")
    plt.show()
    
    # Prediction scatter plot
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, test_predictions, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.title("Prediction vs Actual")
    plt.savefig("prediction_scatter.png")
    mlflow.log_artifact("prediction_scatter.png")
    plt.show()
    
    # Log the model
    signature = infer_signature(x_train, train_predictions)
    mlflow.xgboost.log_model(
        best_xgb, 
        "market_value_model",
        signature=signature,
        registered_model_name="MarketValuePredictor"
    )
```

MLflow in this code is tracking the actual model training process after hyperparameter tuning. It logs training data information (sample size, feature count), the chosen hyperparameters, and multiple performance metrics (MAE, MSE, RMSE) for both training and test sets. It also stores visualizations of feature importance and prediction accuracy. Finally, MLflow registers the trained model with a signature that specifies input/output formats, making it ready for deployment. This comprehensive logging creates a complete record of the model's training process and performance, which is crucial for model governance, reproducibility, and deployment tracking.

## Model lifecycle management

### 1. Transition model to a new stage

```python
def transition_model_stage(model_name, version, stage):
    client = mlflow.tracking.MlflowClient()
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage
    )
```

This function manages model lifecycle stages in MLflow's registry:

- Takes model name, version number, and desired stage as inputs
- Uses MLflowClient to transition model between stages (None -> Staging -> Production -> Archived)
- Helps control which model version is actively deployed
- Enables testing models in staging before promoting to production
- Maintains history by archiving older versions

### 2. Loading production model

```python
def load_production_model():
    model = mlflow.pyfunc.load_model(
        model_uri=f"models:/MarketValuePredictor/Production"
    )
    return model
```

This function simply retrieves the current production model from MLflow's registry:

- Uses mlflow.pyfunc.load_model() to load model from registry
- The URI format models:/ModelName/Stage specifies which model version to load
- Returns loaded model ready for making predictions
- Useful when deploying model for inference/predictions

### 3. Look into evaluation metrics

```python
print("Model evaluation metrics:")
for metric_name, metric_value in metrics.items():
    print(f"{metric_name}: {metric_value:.4f}")
```

### 4. Example usage: Transition model to staging

```python
transition_model_stage("MarketValuePredictor", 1, "Staging")
```

Here, `1` denotes the version of the registered model.

### 5. Example usage: Transition model to production

```python
transition_model_stage("MarketValuePredictor", 1, "Production")
```

Here, `1` denotes the version of the registered model.

### 6. Get the production model

```python
model = load_production_model()
model
```

## Verification 

### Model Tracking Verification in MLflow

1. Navigate to the MLflow UI with url provided by the `Poridhi's Loadbalancer`.
2. Navigate to "Experiments" tab and select "market_value_prediction"

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/image-1.png)

3. For each model run, verify the parameters, metrics, and artifacts. For example we can see the overview, metrics & artifacts for `model_training_20241115_11`:

    **Overview of `model_training_20241115_11`**:

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/image-2.png)

    **Model Metrics**:

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/image-3.png)

    **Artifacts**:

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/image-4.png)

By following the above steps, you can verify the parameters, metrics, and artifacts for `grid_search_20241115_1907` as well.

### Register Model Verification

In the MLflow UI, navigate to "Model Registry" and verify the registered model and its version in the "Production" stage.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/image-5.png)

### S3 Artifact Verification

Go to AWS Console and navigate to S3 bucket `<your-bucket-name>` to verify the artifacts.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/image-6.png)

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

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/image-7.png)

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

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/Lab%2011/images/image-8.png)


## Conclusion

This project demonstrates a complete MLOps pipeline for player market value prediction, incorporating comprehensive data preprocessing and analysis, feature engineering and selection, model training with hyperparameter tuning, and experiment tracking using MLflow. It also includes model versioning and a deployment pipeline, providing a scalable and maintainable solution for predicting player market values while following MLOps best practices.