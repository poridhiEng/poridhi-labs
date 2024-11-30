
# **Introduction to Feast**

Feast is an open-source feature store that makes it easy to manage and serve machine learning features for both batch and real-time use cases. It helps you define, store, and retrieve features efficiently, letting you focus on building impactful features for AI/ML models.  

Feast integrates with your existing tools (e.g., databases, analytics) and simplifies feature delivery to production using a Python SDK. It handles the complexity of real-time systems for you. With a centralized catalog, Feast provides a single source of truth for feature definitions. It supports both offline and online data stores, enabling low-latency and batch processing seamlessly.


## FEAST Architecture

![](./images/feast_drawio.svg)

This architecture diagram provides an overview of how Feast manages and serves machine learning features. Here's a simplified explanation:



1. **Data Sources:**
   - **Request Sources:** Data from on-the-fly requests (e.g., user-provided inputs).
   - **Stream Sources:** Continuous streams of data (e.g., from Kafka or Kinesis).
   - **Batch Sources:** Historical data stored in systems like Snowflake, BigQuery, S3, or Parquet files.

2. **Transform:**
   - The data from these sources undergoes transformations to prepare features for machine learning. This can include calculations, aggregations, or data cleaning.

3. **Feast Core Components:**
   - **Register:** Defines and registers feature definitions (metadata about features).
   - **Store:** Saves the features into appropriate storage (offline or online).
   - **Serve:** Fetches the features for use in real-time applications or batch processing.

4. **Outputs:**
   - **Online Features:** Served in real-time to models for predictions (low-latency use cases).
   - **Offline Features:** Used for model training or batch scoring (historical analysis).

This architecture ensures that the same features are consistently available for both model training and inference, reducing discrepancies between development and production environments. Let me know if you'd like further clarifications!



## **Overview**

In this tutorial, you will:
1. Deploy a local feature store with Parquet (offline) and SQLite (online) stores.
2. Build a training dataset using time-series features.
3. Ingest batch and streaming features into the online store.
4. Perform batch scoring and real-time inference.
5. Explore the experimental Feast UI.

### **Note:**
Feast provides both a Python SDK and an optional hosted service for managing feature data. This tutorial will focus on the Python SDK for simplicity.


## **Prerequisites**

- Python (3.9 or above) installed.
- A virtual environment is recommended:

```bash
# Create & activate a virtual environment
python -m venv venv/
source venv/bin/activate
```



## **Step 1: Install Feast**

Install the Feast SDK and CLI:

```bash
pip install feast
```



## **Step 2: Create a Feature Repository**

Bootstrap a new repository using the `feast init` command:

```bash
feast init my_project
cd my_project/feature_repo
```

### **Repository Structure:**
- **`data/`**: Contains raw demo Parquet data.
- **`example_repo.py`**: Contains demo feature definitions.
- **`feature_store.yaml`**: Configures the feature store.
- **`test_workflow.py`**: Demonstrates key Feast operations.

**Example `feature_store.yaml`:**

```yaml
project: my_project
registry: data/registry.db
provider: local
online_store:
  type: sqlite
  path: data/online_store.db
entity_key_serialization_version: 2
```


This configuration sets up a **local Feast feature store** for managing and serving machine learning features. It uses:

1. **SQLite** for storing metadata (registry) and real-time features (online store).
2. Groups everything under the project `my_project`.
3. Uses a modern format for storing entity keys (serialization version 2).

It’s ideal for testing or small-scale ML projects.


## **Step 3: Inspecting Raw Data**

For the upcomming steps, let's create a notebook file `my_script.ipynb` in the `feature_repo` directory. Select kernel as the `venv` we are working on.

In the data directory we have a demo `parquet` file. The demo includes driver statistics in Parquet format. Use the following code to inspect the data:

```python
import pandas as pd
pd.read_parquet("data/driver_stats.parquet")
```

#### Output:

```
	event_timestamp	driver_id	conv_rate	acc_rate	avg_daily_trips	created
0	2024-11-15 06:00:00+00:00	1005	0.592416	0.059949	68	2024-11-30 06:28:27.102
1	2024-11-15 07:00:00+00:00	1005	0.111941	0.554601	784	2024-11-30 06:28:27.102
2	2024-11-15 08:00:00+00:00	1005	0.250323	0.382925	537	2024-11-30 06:28:27.102
3	2024-11-15 09:00:00+00:00	1005	0.280857	0.416810	458	2024-11-30 06:28:27.102
4	2024-11-15 10:00:00+00:00	1005	0.410429	0.605702	792	2024-11-30 06:28:27.102
...	...	...	...	...	...	...
1802	2024-11-30 04:00:00+00:00	1001	0.200015	0.861837	721	2024-11-30 06:28:27.102
1803	2024-11-30 05:00:00+00:00	1001	0.006843	0.854434	26	2024-11-30 06:28:27.102
1804	2021-04-12 07:00:00+00:00	1001	0.823021	0.809314	936	2024-11-30 06:28:27.102
1805	2024-11-22 18:00:00+00:00	1003	0.926658	0.066564	431	2024-11-30 06:28:27.102
1806	2024-11-22 18:00:00+00:00	1003	0.926658	0.066564	431	2024-11-30 06:28:27.102
```


## **Step 4: Run Sample Workflow**

There's an included `test_workflow.py` file which runs through a full sample workflow:

- Register feature definitions through `feast apply`

- Generate a training dataset (using `get_historical_features`)

- Generate features for batch scoring (using `get_historical_features`)

- Ingest batch features into an online store (using `materialize_incremental`)

- Fetch online features to power real time inference (using `get_online_features`)

- Ingest streaming features into offline / online stores (using `push`)

- Verify online features are updated / fresher



## **Step 5: Register Feature Definitions**

Register and deploy your feature store by running:

```bash
feast apply
```

#### Output

![alt text](./images/image.png)



## **Step 6: Generate Training Data**

Generate training data with the following code:

```python
from datetime import datetime
import pandas as pd
from feast import FeatureStore

entity_df = pd.DataFrame.from_dict(
    {
        # entity's join key -> entity values
        "driver_id": [1001, 1002, 1003],
        # "event_timestamp" (reserved key) -> timestamps
        "event_timestamp": [
            datetime(2021, 4, 12, 10, 59, 42),
            datetime(2021, 4, 12, 8, 12, 10),
            datetime(2021, 4, 12, 16, 40, 26),
        ],
        # (optional) label name -> label values. Feast does not process these
        "label_driver_reported_satisfaction": [1, 5, 3],
        # values we're using for an on-demand transformation
        "val_to_add": [1, 2, 3],
        "val_to_add_2": [10, 20, 30],
    }
)

store = FeatureStore(repo_path=".")

training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
        "transformed_conv_rate:conv_rate_plus_val1",
        "transformed_conv_rate:conv_rate_plus_val2",
    ],
).to_df()

print("----- Feature schema -----\n")
print(training_df.info())

print()
print("----- Example features -----\n")
print(training_df.head())
```

#### Output

```
----- Feature schema -----

<class 'pandas.core.frame.DataFrame'>
RangeIndex: 3 entries, 0 to 2
Data columns (total 10 columns):
 #   Column                              Non-Null Count  Dtype              
---  ------                              --------------  -----              
 0   driver_id                           3 non-null      int64              
 1   event_timestamp                     3 non-null      datetime64[ns, UTC]
 2   label_driver_reported_satisfaction  3 non-null      int64              
 3   val_to_add                          3 non-null      int64              
 4   val_to_add_2                        3 non-null      int64              
 5   conv_rate                           3 non-null      float32            
 6   acc_rate                            3 non-null      float32            
 7   avg_daily_trips                     3 non-null      int32              
 8   conv_rate_plus_val1                 3 non-null      float64            
 9   conv_rate_plus_val2                 3 non-null      float64            
dtypes: datetime64[ns, UTC](1), float32(2), float64(2), int32(1), int64(4)
memory usage: 332.0 bytes
None

----- Example features -----

   driver_id           event_timestamp  label_driver_reported_satisfaction  \
0       1001 2021-04-12 10:59:42+00:00                                   1   
...
   conv_rate_plus_val1  conv_rate_plus_val2  
0             1.823021            10.823021  
1             2.179108            20.179108  
2             3.553620            30.553620  
```

## **Step 7: Run offline inference (batch scoring)**

In a new cell, update timestamps in `entity_df` to the current time and regenerate features:

```python
entity_df["event_timestamp"] = pd.to_datetime("now", utc=True)
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
        "transformed_conv_rate:conv_rate_plus_val1",
        "transformed_conv_rate:conv_rate_plus_val2",
    ],
).to_df()

print("\n----- Example features -----\n")
print(training_df.head())
```

#### Output

```
----- Example features -----

   driver_id                  event_timestamp  \
0       1001 2024-11-30 08:02:24.256307+00:00   
1       1002 2024-11-30 08:02:24.256307+00:00   
2       1003 2024-11-30 08:02:24.256307+00:00   

   label_driver_reported_satisfaction  val_to_add  val_to_add_2  conv_rate  \
0                                   1           1            10   0.006843   
1                                   5           2            20   0.753837   
2                                   3           3            30   0.941847   

   acc_rate  avg_daily_trips  conv_rate_plus_val1  conv_rate_plus_val2  
0  0.854434               26             1.006843            10.006843  
1  0.822263              532             2.753837            20.753837  
2  0.340301               78             3.941847            30.941847  
```


## **Step 8: Fetching feature vectors for inference**

```python
from pprint import pprint
from feast import FeatureStore

store = FeatureStore(repo_path=".")

feature_vector = store.get_online_features(
    features=[
        "driver_hourly_stats:conv_rate",
        "driver_hourly_stats:acc_rate",
        "driver_hourly_stats:avg_daily_trips",
    ],
    entity_rows=[
        # {join_key: entity_value}
        {"driver_id": 1004},
        {"driver_id": 1005},
    ],
).to_dict()

pprint(feature_vector)
```

#### Output:

```
{'acc_rate': [0.7695725560188293, 0.9291703701019287],
 'avg_daily_trips': [161, 372],
 'conv_rate': [0.4778262674808502, 0.06225856393575668],
 'driver_id': [1004, 1005]}
```

## **Step 9: Browse your features with the Web UI (experimental)** 
View all registered features, data sources, entities, and feature services with the Web UI.

One of the ways to view this is with the feast ui command:
```
feast ui --host="0.0.0.0"
```

#### Output

```
INFO:     Started server process [66664]
08/17/2022 01:25:49 PM uvicorn.error INFO: Started server process [66664]
INFO:     Waiting for application startup.
08/17/2022 01:25:49 PM uvicorn.error INFO: Waiting for application startup.
INFO:     Application startup complete.
08/17/2022 01:25:49 PM uvicorn.error INFO: Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
08/17/2022 01:25:49 PM uvicorn.error INFO: Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

Now create a poridhi load balancer to expose the UI using the `eth0` IP and port `8888`. Open the Load Balancer URL to see the UI.


## Conclusion

This document provides a comprehensive guide to getting started with Feast, covering installation, repository setup, workflows, and feature generation for both training and inference. 