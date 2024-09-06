import os
import boto3
import pandas as pd
from dotenv import load_dotenv
import ray
from sklearn.preprocessing import MinMaxScaler

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
source_bucket_name = os.getenv('SOURCE_BUCKET_NAME')
destination_bucket_name = os.getenv('DESTINATION_BUCKET_NAME')
local_file_path = os.getenv('LOCAL_FILE_PATH')
file_key = 'staging-directory/raw-dataset.csv'

# Ensure the variables are correctly set
if not all([aws_access_key_id, aws_secret_access_key, aws_region, source_bucket_name, destination_bucket_name, local_file_path]):
    raise ValueError("One or more environment variables are not set correctly.")

# Create an S3 resource
s3_client = boto3.resource(
    service_name='s3',
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Upload file to S3
print(f"Uploading file {local_file_path} to bucket {source_bucket_name} with key {file_key}...")
s3_client.meta.client.upload_file(local_file_path, source_bucket_name, file_key)

# List all objects in the bucket
print(f"Objects in bucket {source_bucket_name}:")
for obj in s3_client.Bucket(source_bucket_name).objects.all():
    print(obj.key)

# Read dataset from S3
ds = ray.data.read_csv(f"s3://{source_bucket_name}/{file_key}")
ds.show(limit=5)
df = ds.to_pandas()

# Define batch transformer
class BatchTransformer:
    def __init__(self):
        pass

    @staticmethod
    def categorize_time_of_day(hour):
        if 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        elif 18 <= hour < 24:
            return 'Evening'
        else:
            return 'Night'

    @staticmethod
    def categorize_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Autumn'

    def transform(self, batch):
        batch['Datetime'] = pd.to_datetime(batch['Datetime'])
        batch['Year'] = batch['Datetime'].dt.year
        batch['Month'] = batch['Datetime'].dt.month
        batch['Day'] = batch['Datetime'].dt.day
        batch['Hour'] = batch['Datetime'].dt.hour
        batch['TimeOfDay'] = batch['Hour'].apply(self.categorize_time_of_day)
        batch['Weekday'] = batch['Datetime'].dt.weekday
        batch['IsWeekend'] = batch['Weekday'].apply(lambda x: 1 if x >= 5 else 0)
        batch['Season'] = batch['Month'].apply(self.categorize_season)
        batch['Year'] = batch['Year'].astype(int)
        batch['Weekday'] = batch['Weekday'].astype(int)
        batch['IsWeekend'] = batch['IsWeekend'].astype(int)
        return batch

# Instantiate the transformer and apply it to the dataset
transformer = BatchTransformer()
transformed_ds = ds.map_batches(transformer.transform, batch_format="pandas")
transformed_ds.to_pandas()

# Drop unnecessary columns
ds_updated = transformed_ds.drop_columns(["Datetime"])
df_updated = ds_updated.to_pandas()

# Define function to encode categorical columns
def encode_categorical_columns(batch):
    categorical_columns = ['TimeOfDay', 'Season']
    batch_encoded = pd.get_dummies(batch, columns=categorical_columns)
    batch_encoded = batch_encoded.astype(int)
    return batch_encoded

# Apply one-hot encoding
ds_encoded = ds_updated.map_batches(encode_categorical_columns, batch_format="pandas")
df_encoded = ds_encoded.to_pandas()

# Define aggregation functions and perform grouping
aggregation_functions = {
    'Temperature': ['mean'],
    'Humidity': ['mean'],
    'WindSpeed': ['mean'],
    'GeneralDiffuseFlows': ['mean'],
    'DiffuseFlows': ['mean'],
    'PowerConsumption_Zone1': ['sum'],
    'PowerConsumption_Zone2': ['sum'],
    'PowerConsumption_Zone3': ['sum'],
    'Weekday': ['first'],
    'IsWeekend': ['first'],
    'TimeOfDay_Afternoon': ['first'],
    'TimeOfDay_Evening': ['first'],
    'TimeOfDay_Morning': ['first'],
    'TimeOfDay_Night': ['first'],
    'Season_Autumn': ['first'],
    'Season_Spring': ['first'],
    'Season_Summer': ['first'],
    'Season_Winter': ['first']
}

df_grouped = df_encoded.groupby(['Year', 'Month', 'Day', 'Hour']).agg(aggregation_functions)
df_grouped.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df_grouped.columns]
df_grouped = df_grouped.reset_index()

# Create lag features
columns_to_lag = [
    'Temperature_mean', 'Humidity_mean', 'WindSpeed_mean', 'GeneralDiffuseFlows_mean',
    'DiffuseFlows_mean', 'PowerConsumption_Zone1_sum', 'PowerConsumption_Zone2_sum',
    'PowerConsumption_Zone3_sum'
]

lags = [4, 8, 12, 24, 48]
df_lagged = df_grouped.copy()

for col in columns_to_lag:
    for lag in lags:
        df_lagged[f'{col}_lag{lag}'] = df_grouped[col].shift(lag)

df_lagged.fillna(0, inplace=True)
df_lagged = df_lagged.dropna()

# Convert to Ray Dataset and scale
feature_ds = ray.data.from_pandas(df_lagged)
cols_to_scale = [
    "Temperature_mean", "Humidity_mean", "WindSpeed_mean",
    "GeneralDiffuseFlows_mean", "DiffuseFlows_mean", "PowerConsumption_Zone1_sum", 
    "PowerConsumption_Zone2_sum", "PowerConsumption_Zone3_sum",
    "Temperature_mean_lag4", "Temperature_mean_lag8", "Temperature_mean_lag12", "Temperature_mean_lag24", "Temperature_mean_lag48",
    "Humidity_mean_lag4", "Humidity_mean_lag8", "Humidity_mean_lag12", "Humidity_mean_lag24", "Humidity_mean_lag48",
    "WindSpeed_mean_lag4", "WindSpeed_mean_lag8", "WindSpeed_mean_lag12", "WindSpeed_mean_lag24", "WindSpeed_mean_lag48",
    "GeneralDiffuseFlows_mean_lag4", "GeneralDiffuseFlows_mean_lag8", "GeneralDiffuseFlows_mean_lag12", "GeneralDiffuseFlows_mean_lag24", "GeneralDiffuseFlows_mean_lag48",
    "DiffuseFlows_mean_lag4", "DiffuseFlows_mean_lag8", "DiffuseFlows_mean_lag12", "DiffuseFlows_mean_lag24", "DiffuseFlows_mean_lag48",
    "PowerConsumption_Zone1_sum_lag4", "PowerConsumption_Zone1_sum_lag8", "PowerConsumption_Zone1_sum_lag12", "PowerConsumption_Zone1_sum_lag24", "PowerConsumption_Zone1_sum_lag48",
    "PowerConsumption_Zone2_sum_lag4", "PowerConsumption_Zone2_sum_lag8", "PowerConsumption_Zone2_sum_lag12", "PowerConsumption_Zone2_sum_lag24", "PowerConsumption_Zone2_sum_lag48",
    "PowerConsumption_Zone3_sum_lag4", "PowerConsumption_Zone3_sum_lag8", "PowerConsumption_Zone3_sum_lag12", "PowerConsumption_Zone3_sum_lag24", "PowerConsumption_Zone3_sum_lag48"
]

def scale_partition(df, cols_to_scale):
    scaler = MinMaxScaler()
    df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
    return df

scaled_ds = feature_ds.map_batches(lambda batch: scale_partition(batch, cols_to_scale), batch_format="pandas")
scaled_df = scaled_ds.to_pandas()

# Save transformed data to CSV and upload to S3
scaled_df.to_csv('2-transformed-data/transformed_features.csv', index=False)
scaled_ds.write_csv(f"s3://{destination_bucket_name}/feature_data.csv")

print("Data processing and upload complete.")