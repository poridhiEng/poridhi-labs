import os
import boto3
import ray
import pandas as pd
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from ray import train
from ray.train import ScalingConfig
from ray.train.xgboost import XGBoostTrainer
import mlflow
from ray.air.integrations.mlflow import MLflowLoggerCallback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up S3 client
s3_client = boto3.client(
    service_name='s3',
    region_name='ap-southeast-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Download file from S3
bucket_name = os.getenv('S3_BUCKET_NAME')
file_key = os.getenv('S3_FILE_KEY')
version_id = os.getenv('S3_VERSION_ID')
local_file_path = "3-training-data/training_features.csv"
s3_client.download_file(bucket_name, file_key, local_file_path, ExtraArgs={"VersionId": version_id})

# Load data
df_lagged = pd.read_csv(local_file_path)

# Prepare data for training
X = df_lagged.drop(['PowerConsumption_Zone1_sum', 'PowerConsumption_Zone2_sum', 'PowerConsumption_Zone3_sum'], axis=1)
y1 = df_lagged['PowerConsumption_Zone1_sum']
df_combined = X.copy()
df_combined['label'] = y1 
df_train, df_valid = train_test_split(df_combined, test_size=0.2, random_state=42)
train_dataset = ray.data.from_pandas(df_train)
valid_dataset = ray.data.from_pandas(df_valid)

# XGBoost parameters
xgb_params = {
    "objective": "reg:squarederror",
    "eval_metric": ["rmse", "mae"],
}

# Ray trainer configuration
scaling_config = ScalingConfig(num_workers=2, use_gpu=False)
mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI')

trainer = XGBoostTrainer(
    scaling_config=scaling_config,
    label_column="label",
    params=xgb_params,
    datasets={"train": train_dataset, "valid": valid_dataset},
    run_config=train.RunConfig(
        storage_path=os.getenv('MODEL_STORAGE_PATH'),
        name="Training_Electricity_Consumption",
        callbacks=[
            MLflowLoggerCallback(
                tracking_uri=mlflow_tracking_uri,
                experiment_name="mlflow_callback_ray",
                save_artifact=True,
            )
        ],
    )
)
result = trainer.fit()

model = trainer.get_model(result.checkpoint)

# Log model with MLflow
mlflow.set_tracking_uri(mlflow_tracking_uri)
mlflow.set_experiment("mlflow_callback_ray")

mlflow.xgboost.log_model(
    xgb_model=model,
    artifact_path="electricity-consumption-prediction",
    registered_model_name="xgboost-raytrain-electricity-consumption-prediction",
)

# Save model locally
import pickle
with open('latest-model.pkl', 'wb') as file:
    pickle.dump(model, file)

# Log dataset info
import tempfile
import json

def log_dataset_info(train_dataset, valid_dataset, experiment_name="mlflow_callback_ray"):
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    train_df = train_dataset.to_pandas()
    valid_df = valid_dataset.to_pandas()
    
    train_stats = {
        'num_samples': len(train_df),
        'feature_columns': list(train_df.columns),
    }
    valid_stats = {
        'num_samples': len(valid_df),
        'feature_columns': list(valid_df.columns),
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        json.dump(train_stats, tmp)
        mlflow.log_artifact(tmp.name, "train_dataset_info")
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
        json.dump(valid_stats, tmp)
        mlflow.log_artifact(tmp.name, "valid_dataset_info")

    sample_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv").name
    train_df.head(100).to_csv(sample_file)
    mlflow.log_artifact(sample_file, "dataset_samples")

log_dataset_info(train_dataset, valid_dataset)

# Sample prediction
sample_request_input = {
    "Year": 2020,
    "Month": 7,
    "Day": 14,
    "Hour": 15,
    "Temperature_mean": 25.5,
    "Humidity_mean": 30,
    "WindSpeed_mean": 5,
    "GeneralDiffuseFlows_mean": 200,
    "DiffuseFlows_mean": 180,
    "Weekday_first": 1,
    "IsWeekend_first": 0,
    "TimeOfDay_Afternoon_first": 1,
    "TimeOfDay_Evening_first": 0,
    "TimeOfDay_Morning_first": 0,
    "TimeOfDay_Night_first": 0,
    "Season_Autumn_first": 0,
    "Season_Spring_first": 0,
    "Season_Summer_first": 1,
    "Season_Winter_first": 0,
    "Temperature_mean_lag4": 25.0,
    "Temperature_mean_lag8": 24.5,
    "Temperature_mean_lag12": 24.0,
    "Temperature_mean_lag24": 23.5,
    "Temperature_mean_lag48": 23.0,
    "Humidity_mean_lag4": 35,
    "Humidity_mean_lag8": 40,
    "Humidity_mean_lag12": 45,
    "Humidity_mean_lag24": 50,
    "Humidity_mean_lag48": 55,
    "WindSpeed_mean_lag4": 4,
    "WindSpeed_mean_lag8": 4.5,
    "WindSpeed_mean_lag12": 5,
    "WindSpeed_mean_lag24": 5.5,
    "WindSpeed_mean_lag48": 6,
    "GeneralDiffuseFlows_mean_lag4": 190,
    "GeneralDiffuseFlows_mean_lag8": 180,
    "GeneralDiffuseFlows_mean_lag12": 170,
    "GeneralDiffuseFlows_mean_lag24": 160,
    "GeneralDiffuseFlows_mean_lag48": 150,
    "DiffuseFlows_mean_lag4": 170,
    "DiffuseFlows_mean_lag8": 160,
    "DiffuseFlows_mean_lag12": 150,
    "DiffuseFlows_mean_lag24": 140,
    "DiffuseFlows_mean_lag48": 130,
    "PowerConsumption_Zone1_sum_lag4": 1000,
    "PowerConsumption_Zone1_sum_lag8": 1050,
    "PowerConsumption_Zone1_sum_lag12": 1100,
    "PowerConsumption_Zone1_sum_lag24": 1150,
    "PowerConsumption_Zone1_sum_lag48": 1200,
    "PowerConsumption_Zone2_sum_lag4": 2000,
    "PowerConsumption_Zone2_sum_lag8": 2050,
    "PowerConsumption_Zone2_sum_lag12": 2100,
    "PowerConsumption_Zone2_sum_lag24": 2150,
    "PowerConsumption_Zone2_sum_lag48": 2200,
    "PowerConsumption_Zone3_sum_lag4": 3000,
    "PowerConsumption_Zone3_sum_lag8": 3050,
    "PowerConsumption_Zone3_sum_lag12": 3100,
    "PowerConsumption_Zone3_sum_lag24": 3150,
    "PowerConsumption_Zone3_sum_lag48": 3200,
}
sample_df = pd.DataFrame.from_dict([sample_request_input])
sample_df.shape
data_dmatrix = xgb.DMatrix(sample_df)
predictions = model.predict(data=data_dmatrix)

# Print predictions
print(predictions)

# Predictions on test data
prediction_dataframe = pd.read_csv("./3-training-data/training_features.csv")

prediction_dataframe_dropped = prediction_dataframe.drop(['PowerConsumption_Zone1_sum', 'PowerConsumption_Zone2_sum', 'PowerConsumption_Zone3_sum'], axis=1)
df_valid_features = df_valid.drop('label', axis=1)
data_dmatrix = xgb.DMatrix(df_valid_features)
predictions = model.predict(data=data_dmatrix)

# Print test data predictions
print(predictions)