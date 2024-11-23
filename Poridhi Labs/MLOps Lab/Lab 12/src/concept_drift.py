# src/monitoring/concept_drift.py
from sklearn.metrics import mean_squared_error
import numpy as np


def detect_concept_drift(
    model_pipeline, X_reference, y_reference, X_current, y_current, threshold=0.15
):
    """
    Detect concept drift by comparing model performance on reference and current data.

    This function calculates the mean squared error (MSE) of the model's predictions
    on both the reference and current data. It then determines the relative change
    in performance (relative performance decrease) and flags concept drift if this
    change exceeds the specified threshold.

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
        # Calculate predictions
        y_pred_reference = model_pipeline.predict(X_reference)
        y_pred_current = model_pipeline.predict(X_current)

        # Calculate normalized MSE to handle different scales
        mse_reference = mean_squared_error(y_reference, y_pred_reference)
        mse_current = mean_squared_error(y_current, y_pred_current)

        # Avoid division by zero
        if mse_reference == 0:
            relative_performance_decrease = 0 if mse_current == 0 else 1
        else:
            relative_performance_decrease = (mse_current - mse_reference) / mse_reference

        # Detect drift
        is_drift = relative_performance_decrease > threshold

        print(f"Debug - MSE Reference: {mse_reference:.4f}")
        print(f"Debug - MSE Current: {mse_current:.4f}")
        print(f"Debug - Relative Decrease: {relative_performance_decrease:.4f}")

        return is_drift, relative_performance_decrease

    except Exception as e:
        print(f"Error in concept drift detection: {e}")
        return False, 0.0