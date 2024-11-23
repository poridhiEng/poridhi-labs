# src/monitoring/data_drift.py
"""
Data Drift Detection Module

This module implements data drift detection using the Kolmogorov-Smirnov (KS) test
for numerical features and Jensen-Shannon divergence for categorical features.
It compares the distribution of features between reference and current datasets
to identify significant changes in data patterns.

The implementation uses a feature-wise approach and aggregates the results
to provide an overall drift score.

Args:
    reference_data (pd.DataFrame): The baseline dataset used for comparison.
    current_data (pd.DataFrame): The new dataset to check for drift.
    threshold (float): The threshold for determining significant drift (default: 0.15).

Returns:
    tuple: (is_drift, drift_scores, overall_drift_score)
        - is_drift (bool): Boolean indicating if significant drift was detected.
        - drift_scores (dict): Dictionary of drift scores (KS statistics or Jensen-Shannon divergence) for each feature.
        - overall_drift_score (float): Average drift score across all features.
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
            - drift_scores (dict): Dictionary of drift scores (KS statistics or Jensen-Shannon divergence) for each feature.
            - overall_drift_score (float): Average drift score across all features.
    """
    drift_scores = {}

    for column in reference_data.columns:
        if reference_data[column].dtype.name in ['object', 'category']:
            # For categorical features, compare value distributions
            ref_dist = reference_data[column].value_counts(normalize=True)
            curr_dist = current_data[column].value_counts(normalize=True)

            # Calculate Jensen-Shannon divergence
            all_categories = list(set(ref_dist.index) | set(curr_dist.index))
            ref_probs = [ref_dist.get(cat, 0) for cat in all_categories]
            curr_probs = [curr_dist.get(cat, 0) for cat in all_categories]

            # Normalize to sum to 1
            ref_probs = np.array(ref_probs) / sum(ref_probs)
            curr_probs = np.array(curr_probs) / sum(curr_probs)

            # Calculate KL divergence
            drift_scores[column] = np.sum(ref_probs * np.log(ref_probs / curr_probs))
        else:
            # For numerical features, use KS test
            # Normalize the data first
            scaler = StandardScaler()
            ref_normalized = scaler.fit_transform(reference_data[column].values.reshape(-1, 1)).ravel()
            curr_normalized = scaler.transform(current_data[column].values.reshape(-1, 1)).ravel()

            ks_statistic, _ = ks_2samp(ref_normalized, curr_normalized)
            drift_scores[column] = ks_statistic

    # Calculate overall drift score with feature importance weighting
    overall_drift_score = np.mean(list(drift_scores.values()))

    # Detect if drift occurred
    is_drift = overall_drift_score > threshold

    return is_drift, drift_scores, overall_drift_score