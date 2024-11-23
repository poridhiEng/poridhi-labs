# src/app.py
"""
Model Monitoring Service with Drift Detection

This service provides real-time monitoring of machine learning model performance,
including data drift and concept drift detection. It exposes endpoints for
predictions and metrics collection via Prometheus.

Features:
- Real-time model predictions via REST API
- Automated drift detection every 5 seconds
- Prometheus metrics integration
- Background scheduling of monitoring tasks
- Model retraining upon drift detection
"""

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

# Change the model loading path to absolute path
MODEL_PATH = "/app/model_pipeline.joblib"

# Load the model pipeline
try:
    model_pipeline = joblib.load(MODEL_PATH)
    print(f"Model pipeline loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model pipeline from {MODEL_PATH}: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    model_pipeline = None

@app.route("/", methods=["GET"])
def home():
    """
    Root endpoint providing API documentation.

    Returns:
        JSON: A dictionary containing the service status and available endpoints.
    """
    return jsonify({
        "status": "running",
        "endpoints": {
            "predict": "/predict (POST)",
            "metrics": "/metrics (GET)"
        }
    })

@app.route("/predict", methods=["POST"])
def predict():
    """
    Make predictions using the loaded model.

    Expects:
        JSON: A dictionary containing diamond features.

    Returns:
        JSON: A dictionary containing the prediction.
    """
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

# Update threshold constants to be more sensitive
DATA_DRIFT_THRESHOLD = 0.15    # Threshold for data drift detection
CONCEPT_DRIFT_THRESHOLD = 0.15 # Threshold for concept drift detection

# Add new Prometheus metrics for retraining
retraining_counter = Gauge("model_retraining_count", "Number of times model has been retrained")

def retrain_model():
    """
    Retrain the model with new data and update the global model pipeline.

    This function loads the latest data, retrains the model, and updates the
    global `model_pipeline` variable. It also increments the retraining counter.
    """
    global model_pipeline
    print("Retraining model with new data...")
    train_model()
    
    try:
        model_pipeline = joblib.load(MODEL_PATH)
        print("Model successfully retrained and reloaded")
        retraining_counter.inc()  # Increment the retraining counter
    except Exception as e:
        print(f"Error reloading model after retraining: {e}")

def monitor_drifts():
    """
    Periodic monitoring function that checks for data and concept drift.

    This function simulates real-time data changes by introducing small random
    variations to the diamond features. It then compares the current data
    distribution and model performance to the reference data and model,
    detecting drift if thresholds are exceeded. If drift is detected, the model
    is retrained and the reference data is updated.
    """
    global X_reference, y_reference, model_pipeline
    
    try:
        # Get base data
        new_diamonds = sns.load_dataset("diamonds").sample(n=1000, replace=True)
        
        # Introduce very small, realistic random variations to numerical features
        random_factor = np.random.uniform(0.98, 1.02)  # Reduced to ±2% variation
        new_diamonds['carat'] = new_diamonds['carat'] * random_factor
        new_diamonds['depth'] = new_diamonds['depth'] * np.random.uniform(0.99, 1.01)  # ±1% variation
        new_diamonds['table'] = new_diamonds['table'] * np.random.uniform(0.99, 1.01)  # ±1% variation
        
        # Add very small random noise to prices (1% standard deviation)
        price_noise = np.random.normal(0, new_diamonds['price'] * 0.01)  # Reduced to 1% standard deviation
        new_diamonds['price'] = new_diamonds['price'] + price_noise
        
        X_current = new_diamonds[["carat", "cut", "color", "clarity", "depth", "table"]]
        y_current = new_diamonds["price"]

        print("\n=== Drift Monitoring Report ===")
        print(f"Current sample size: {len(X_current)}")
        print(f"Reference sample size: {len(X_reference)}")

        # Verify model is loaded
        if model_pipeline is None:
            print("Error: Model pipeline is not loaded")
            data_drift_gauge.set(-1)
            concept_drift_gauge.set(-1)
            return

        # Data drift detection
        is_data_drift, drift_scores, data_drift_score = detect_data_drift(
            X_reference, 
            X_current, 
            threshold=DATA_DRIFT_THRESHOLD
        )
        data_drift_gauge.set(data_drift_score)
        print(f"Data Drift Score: {data_drift_score:.4f} (Threshold: {DATA_DRIFT_THRESHOLD})")

        # Concept drift detection
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
                print(f"- Concept drift detected (Score: {concept_drift_score:.4f})")
            
            print("Initiating model retraining...")
            retrain_model()
            
            # Update reference data after successful retraining
            X_reference = X_current
            y_reference = y_current
            print("Reference data updated")
        
        print("===========================\n")
        
    except Exception as e:
        print(f"Error in drift monitoring: {e}")
        import traceback
        traceback.print_exc()
        data_drift_gauge.set(-1)
        concept_drift_gauge.set(-1)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8000)

    # Schedule drift monitoring every 5 seconds instead of 10
    scheduler = BackgroundScheduler()
    scheduler.add_job(monitor_drifts, "interval", seconds=5)  # Changed from 10 to 5 seconds
    scheduler.start()

    # Run Flask app
    app.run(host="0.0.0.0", port=5000)