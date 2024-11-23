
# ML Model Drift Monitoring System

This lab provides a comprehensive guide to implementing a Machine Learning Model Drift Monitoring System. The system is designed to detect and visualize drift in machine learning models, ensuring their reliability and performance over time. It focuses on a diamond price prediction model as a case study.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2012/images/Arch-diagram.svg?raw=true)

### Data Drift

Data drift occurs when the statistical properties of the model's input features change over time compared to the training data. For example, if the distribution of diamond carat weights shifts significantly from the original training distribution, this indicates data drift.

### Concept Drift

Concept drift happens when the fundamental relationships between features and the target variable change. For instance, if market conditions cause the relationship between diamond characteristics and prices to shift, this represents concept drift.

## Task Overview

The primary objective of this project is to create a real-time monitoring system that detects both data drift and concept drift in a diamond price prediction model. 

### Key Features:
- Monitors model health by detecting data and concept drift.
- Simulates real data changes to test the model's robustness.
- Visualizes drift metrics in real-time using Grafana.

### Data Flow Diagram

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2012/images/Data-flow.svg?raw=true)

### Deployment Architecture

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2012/images/deploy.svg?raw=true)

## Step-by-Step Solution

### 1. Project Setup

#### 1.1 Directory Structure


Create the following directory structure for the project:

```
ml_model_drift_monitoring/
│
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── data_drift.py
│   ├── concept_drift.py
│   ├── train.py
│
├── Dockerfile
├── docker-compose.yml
├── prometheus.yml
├── requirements.txt
├── README.md
└── .gitignore
```

### 2. Application Code

#### 2.1 Main Application (`src/app.py`)

This file contains the main application logic, including endpoints for predictions and metrics collection.

```python
import os
import joblib
import pandas as pd
import seaborn as sns
import numpy as np

from prometheus_client import start_http_server, Gauge
from prometheus_client import make_wsgi_app
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from data_drift import detect_data_drift
from concept_drift import detect_concept_drift
from train import train_model

app = Flask(__name__)

MODEL_PATH = "/app/model_pipeline.joblib"

# Load the model pipeline
try:
    model_pipeline = joblib.load(MODEL_PATH)
    print(f"Model pipeline loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model pipeline from {MODEL_PATH}: {e}")
    model_pipeline = None

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "endpoints": {
            "predict": "/predict (POST)",
            "metrics": "/metrics (GET)"
        }
    })

@app.route("/predict", methods=["POST"])
def predict():
    if model_pipeline is None:
        return jsonify({"error": "Model pipeline not loaded properly"}), 500

    data = request.json
    df = pd.DataFrame(data, index=[0])
    prediction = model_pipeline.predict(df)
    return jsonify({"prediction": prediction[0]})

# Create Prometheus metrics
data_drift_gauge = Gauge("data_drift", "Data Drift Score")
concept_drift_gauge = Gauge("concept_drift", "Concept Drift Score")

# Load reference data
diamonds = sns.load_dataset("diamonds")
X_reference = diamonds[["carat", "cut", "color", "clarity", "depth", "table"]]
y_reference = diamonds["price"]

DATA_DRIFT_THRESHOLD = 0.15
CONCEPT_DRIFT_THRESHOLD = 0.15

def monitor_drifts():
    global X_reference, y_reference, model_pipeline
    
    try:
        new_diamonds = sns.load_dataset("diamonds").sample(n=1000, replace=True)
        random_factor = np.random.uniform(0.98, 1.02)
        new_diamonds['carat'] = new_diamonds['carat'] * random_factor
        new_diamonds['depth'] = new_diamonds['depth'] * np.random.uniform(0.99, 1.01)
        new_diamonds['table'] = new_diamonds['table'] * np.random.uniform(0.99, 1.01)
        
        price_noise = np.random.normal(0, new_diamonds['price'] * 0.01)
        new_diamonds['price'] = new_diamonds['price'] + price_noise
        
        X_current = new_diamonds[["carat", "cut", "color", "clarity", "depth", "table"]]
        y_current = new_diamonds["price"]

        print("\n=== Drift Monitoring Report ===")
        print(f"Current sample size: {len(X_current)}")
        print(f"Reference sample size: {len(X_reference)}")

        if model_pipeline is None:
            print("Error: Model pipeline is not loaded")
            data_drift_gauge.set(-1)
            concept_drift_gauge.set(-1)
            return

        is_data_drift, drift_scores, data_drift_score = detect_data_drift(
            X_reference, 
            X_current, 
            threshold=DATA_DRIFT_THRESHOLD
        )
        data_drift_gauge.set(data_drift_score)
        print(f"Data Drift Score: {data_drift_score:.4f} (Threshold: {DATA_DRIFT_THRESHOLD})")

        is_concept_drift, concept_drift_score = detect_concept_drift(
            model_pipeline,
            X_reference,
            y_reference,
            X_current,
            y_current,
            threshold=CONCEPT_DRIFT_THRESHOLD
        )
        concept_drift_gauge.set(concept_drift_score)
        print(f"Concept Drift Score: {concept_drift_score:.4f} (Threshold: {CONCEPT_DRIFT_THRESHOLD})")
        
        if is_data_drift or is_concept_drift:
            print("\n!!! Drift Detected !!!")
            if is_data_drift:
                print(f"- Data drift detected (Score: {data_drift_score:.4f})")
                print("Feature-wise drift scores:")
                for feature, score in drift_scores.items():
                    print(f"  - {feature}: {score:.4f}")
            if is_concept_drift:
                print(f"- Concept drift detected (Score: {concept_drift_score:.4f}")
            
            
            X_reference = X_current
            y_reference = y_current
            print("Reference data updated")
        
        print("===========================\n")
        
    except Exception as e:
        print(f"Error in drift monitoring: {e}")

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

if __name__ == "__main__":
    start_http_server(8000)
    scheduler = BackgroundScheduler()
    scheduler.add_job(monitor_drifts, "interval", seconds=5)
    scheduler.start()
    app.run(host="0.0.0.0", port=5000)
```

#### 2.2 Data Drift Detection (`src/data_drift.py`)

This module implements data drift detection using the Kolmogorov-Smirnov (KS) test for numerical features and Jensen-Shannon divergence for categorical features.

```python
# src/data_drift.py
"""
Data Drift Detection Module

This module implements data drift detection using the Kolmogorov-Smirnov (KS) test
for numerical features and Jensen-Shannon divergence for categorical features.
It compares the distribution of features between reference and current datasets
to identify significant changes in data patterns.
"""

import numpy as np
from scipy.stats import ks_2samp
from sklearn.preprocessing import StandardScaler

def detect_data_drift(reference_data, current_data, threshold=0.15):
    """
    Detect data drift between reference and current datasets.

    This function compares the distribution of features between the reference
    and current datasets using the Kolmogorov-Smirnov (KS) test for numerical
    features and Jensen-Shannon divergence for categorical features. It then
    calculates an overall drift score based on the average of feature-wise scores.

    Args:
        reference_data (pd.DataFrame): The baseline dataset used for comparison.
        current_data (pd.DataFrame): The new dataset to check for drift.
        threshold (float): The threshold for determining significant drift (default: 0.15).

    Returns:
        tuple: (is_drift, drift_scores, overall_drift_score)
            - is_drift (bool): Boolean indicating if significant drift was detected.
            - drift_scores (dict): Dictionary of drift scores for each feature.
            - overall_drift_score (float): Average drift score across all features.
    """
    drift_scores = {}
    for column in reference_data.columns:
        if reference_data[column].dtype.name in ['object', 'category']:
            ref_dist = reference_data[column].value_counts(normalize=True)
            curr_dist = current_data[column].value_counts(normalize=True)

            all_categories = list(set(ref_dist.index) | set(curr_dist.index))
            ref_probs = [ref_dist.get(cat, 0) for cat in all_categories]
            curr_probs = [curr_dist.get(cat, 0) for cat in all_categories]

            ref_probs = np.array(ref_probs) / sum(ref_probs)
            curr_probs = np.array(curr_probs) / sum(curr_probs)

            drift_scores[column] = np.sum(ref_probs * np.log(ref_probs / curr_probs))
        else:
            scaler = StandardScaler()
            ref_normalized = scaler.fit_transform(reference_data[column].values.reshape(-1, 1)).ravel()
            curr_normalized = scaler.transform(current_data[column].values.reshape(-1, 1)).ravel()

            ks_statistic, _ = ks_2samp(ref_normalized, curr_normalized)
            drift_scores[column] = ks_statistic

    overall_drift_score = np.mean(list(drift_scores.values()))
    is_drift = overall_drift_score > threshold

    return is_drift, drift_scores, overall_drift_score
```

#### 2.3 Concept Drift Detection (`src/concept_drift.py`)

This module detects concept drift by comparing model performance on reference and current data.

```python
# src/concept_drift.py
from sklearn.metrics import mean_squared_error
import numpy as np

def detect_concept_drift(model_pipeline, X_reference, y_reference, X_current, y_current, threshold=0.15):
    """
    Detect concept drift by comparing model performance on reference and current data.

    This function calculates the mean squared error (MSE) of the model's predictions
    on both the reference and current data. It then determines the relative change
    in performance and flags concept drift if this change exceeds the specified threshold.

    Args:
        model_pipeline: Trained model pipeline.
        X_reference: Reference feature set.
        y_reference: Reference target values.
        X_current: Current feature set.
        y_current: Current target values.
        threshold: Threshold for determining significant drift (default: 0.15).

    Returns:
        tuple: (is_drift, relative_performance_decrease)
            - is_drift: Boolean indicating if concept drift was detected.
            - relative_performance_decrease: Relative change in model performance.
    """
    try:
        y_pred_reference = model_pipeline.predict(X_reference)
        y_pred_current = model_pipeline.predict(X_current)

        mse_reference = mean_squared_error(y_reference, y_pred_reference)
        mse_current = mean_squared_error(y_current, y_pred_current)

        if mse_reference == 0:
            relative_performance_decrease = 0 if mse_current == 0 else 1
        else:
            relative_performance_decrease = (mse_current - mse_reference) / mse_reference

        is_drift = relative_performance_decrease > threshold

        return is_drift, relative_performance_decrease

    except Exception as e:
        print(f"Error in concept drift detection: {e}")
        return False, 0.0
```

#### 2.4 Model Training (`src/train.py`)

This script trains a machine learning pipeline for predicting diamond prices.

```python
# src/train.py
"""
Diamond Price Prediction Model Training Script

This script trains a machine learning pipeline for predicting diamond prices.
The pipeline includes preprocessing steps for both numerical and categorical features,
and uses a Random Forest Regressor as the prediction model.
"""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import pandas as pd
import seaborn as sns
import os

def train_model(new_data=None):
    """
    Trains and saves a machine learning pipeline for diamond price prediction.

    Args:
        new_data (tuple, optional): Tuple of (X, y) containing new training data.
                                    If None, uses the original dataset.

    Returns: None (saves model to disk)
    """
    if new_data is None:
        diamonds = sns.load_dataset("diamonds")
        X = diamonds[["carat", "cut", "color", "clarity", "depth", "table"]]
        y = diamonds["price"]
    else:
        X, y = new_data

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), ["carat", "depth", "table"]),
            ("cat", OneHotEncoder(drop="first", sparse_output=False), ["cut", "color", "clarity"]),
        ]
    )

    model_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42)),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model_pipeline.fit(X_train, y_train)

    y_pred = model_pipeline.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model MSE: {mse}")

    MODEL_PATH = os.path.join("/app", "model_pipeline.joblib")
    joblib.dump(model_pipeline, MODEL_PATH)
    print(f"Model pipeline saved successfully at {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
```

### 3. Docker Configuration

#### 3.1 Dockerfile

The `Dockerfile` sets up the application environment, installs dependencies, and trains the model.

```dockerfile
FROM python:3.9-slim
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Train the model before starting the app
RUN python src/train.py && \
    echo "Model training completed"

# Command to run the application
CMD ["python", "src/app.py"]
```

#### 3.2 Docker Compose

The `docker-compose.yml` file defines the services required for the application, including the app, Prometheus, and Grafana.

```yaml
services:
  app:
    build: .
    ports:
      - "5000:5000"  # Flask app
      - "8000:8000"  # Prometheus metrics
    volumes:
      - ./src:/app/src
    networks:
      - monitoring-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - monitoring-network

  grafana:
    image: grafana/grafana-oss:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_AUTH_ANONYMOUS_ENABLED=true
    volumes:
      - grafana-storage:/var/lib/grafana
    networks:
      - monitoring-network
    depends_on:
      - prometheus

networks:
  monitoring-network:

volumes:
  grafana-storage:
  prometheus_data:
```

### 4. Prometheus Configuration

The `prometheus.yml` file configures Prometheus to scrape metrics from the ML application.

```yaml
# Prometheus Configuration for ML Model Monitoring

global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'ml_monitoring'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
```

### 5. Requirements

The `requirements.txt` file lists the necessary Python packages for the project.

```
scikit-learn>=1.0.0
numpy
pandas
seaborn
flask
apscheduler
prometheus-client
joblib
werkzeug
```

### 6. Running the Application

#### 6.1 Build and Start Services

Run the following command to build and start the services defined in the `docker-compose.yml` file:

```bash
docker-compose up --build
```

#### 6.2 Create load balancer for Model API and Grafana 

Create poridhis load balancer for Model API and Grafana to expose the services. Get the `eth0` IP address using the following command:

```bash
ifconfig
```

Now create the load balancer for Model API using the IP and port `5000`.


Create another load balancer for Grafana using the IP and port `3000`.

![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2012/images/image.png?raw=true)




#### 6.2 Accessing the Services

- **Model API**: 
    
    Open the load balancer for Model API in the browser or send POST requests to the service using `postman` at `/predict` endpoint.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2012/images/image-1.png?raw=true)


- **Grafana**: 

    Open the laod balancer for Grafana in the browser and signin using `admin` as username as well as the password. 

### 7. Setup Grafana

1. **Add Prometheus Data Source**:
   - URL: `http://prometheus:9090`
   - Save & Test

2. **Create Dashboard**:
   - Add panels for:
     - `data_drift`
     - `concept_drift`

    Here is an example for data drift:

    ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2012/images/image-2.png?raw=true)

    You can also create a dashboard using the these as follows:

    ![alt text](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/MLOps%20Lab/Lab%2012/images/image-3.png?raw=true)



### 8. Common Issues

1. **Model Loading Fails**:
   - Check if `model_pipeline.joblib` exists in `/app`.
   - Verify Docker volume mounts.

2. **No Metrics in Grafana**:
   - Confirm Prometheus target is up.
   - Check port 8000 is accessible.

### Conclusion

The ML Model Drift Monitoring System provides a robust framework for ensuring the reliability of machine learning models over time. By implementing real-time monitoring, and visualization through Grafana, this system addresses the challenges posed by model drift effectively. This documentation serves as a comprehensive guide to setting up and utilizing the system, ensuring that users can maintain high model performance in production environments.