# src/train.py
"""
Diamond Price Prediction Model Training Script

This script trains a machine learning pipeline for predicting diamond prices.
The pipeline includes preprocessing steps for both numerical and categorical features,
and uses a Random Forest Regressor as the prediction model.

Features:
- **Data Loading:** Loads the diamonds dataset from seaborn.
- **Data Preprocessing:**
    - Applies `StandardScaler` to numerical features: 'carat', 'depth', 'table'.
    - Applies `OneHotEncoder` to categorical features: 'cut', 'color', 'clarity'.
- **Model Training:** Trains a `RandomForestRegressor` with 100 estimators.
- **Model Evaluation:** Calculates the Mean Squared Error (MSE) on a held-out test set.
- **Model Serialization:** Saves the trained model pipeline to disk for production use.
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
        # Load the diamonds dataset from seaborn
        diamonds = sns.load_dataset("diamonds")
        X = diamonds[["carat", "cut", "color", "clarity", "depth", "table"]]
        y = diamonds["price"]
    else:
        X, y = new_data

    # Define the preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), ["carat", "depth", "table"]),
            (
                "cat",
                OneHotEncoder(drop="first", sparse_output=False),
                ["cut", "color", "clarity"],
            ),
        ]
    )

    # Create the model pipeline
    model_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(n_estimators=100, random_state=42)),
        ]
    )

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train the model pipeline
    model_pipeline.fit(X_train, y_train)

    # Evaluate the model on the test set
    y_pred = model_pipeline.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model MSE: {mse}")

    # Save the trained model pipeline to disk
    MODEL_PATH = os.path.join("/app", "model_pipeline.joblib")
    joblib.dump(model_pipeline, MODEL_PATH)
    print(f"Model pipeline saved successfully at {MODEL_PATH}")


if __name__ == "__main__":
    train_model()