
# **Hands-On Lab: Introduction to FEAST**

### **1. Introduction to FEAST**
FEAST (Feature Store) is an open-source framework for managing and serving machine learning features. It bridges the gap between data engineering and machine learning workflows by:
- **Standardizing feature storage** for training and inference.
- Enabling **real-time feature retrieval** from an online store.
- Ensuring consistency between training and serving datasets.

In this lab, we'll use FEAST to:
1. Manage features in a **Customer Churn Dataset**.
2. Perform **real-time and batch data retrieval**.
3. Understand FEAST concepts like **entities**, **feature views**, **online/offline stores**, and more.



### **2. How to Install FEAST**

#### **Prerequisites**
- Python 3.7 or later.
- Virtual environment tool (e.g., `venv` or `conda`).

#### **Installation Steps**
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv feast-env
   source feast-env/bin/activate  # On Windows: feast-env\Scripts\activate
   ```

2. Install FEAST:
   ```bash
   pip install feast
   ```

3. Verify installation:
   ```bash
   feast --version
   ```



### **3. Setting Up the FEAST Repo**

1. **Create a FEAST project**:
   ```bash
   feast init customer_churn_project
   cd customer_churn_project
   ```

2. **Directory structure**:
   - `feature_store.yaml`: Configuration for FEAST.
   - `data/`: Folder to store dataset files.
   - `features/`: Python code defining entities and feature views.



### **4. Converting the Dataset to Parquet Format**

#### **Why Parquet?**
FEAST requires data in Parquet format for efficient storage and processing.

#### **Conversion Steps**
1. Install pandas and pyarrow for conversion:
   ```bash
   pip install pandas pyarrow
   ```

2. Convert the CSV file to Parquet:
   ```python
   import pandas as pd

   # Load the CSV dataset
   csv_file = "customer_churn.csv"
   df = pd.read_csv(csv_file)

   # Save as Parquet
   parquet_file = "customer_churn.parquet"
   df.to_parquet(parquet_file, engine="pyarrow")
   print(f"Dataset converted to {parquet_file}")
   ```

3. Move the Parquet file to the `data/` folder:
   ```bash
   mv customer_churn.parquet data/
   ```



### **5. Understanding Entities in FEAST**

#### **Defining an Entity**
In this dataset, `customerID` uniquely identifies each customer. We'll define it as an entity in FEAST.

1. Create the file `features/entities.py`:
   ```python
   from feast import Entity, ValueType

   # Define customer entity
   customer = Entity(
       name="customer_id",  # Unique entity name
       value_type=ValueType.STRING,  # Data type
       description="Unique ID for a customer"  # Description
   )
   ```



### **6. Understanding Feature View in FEAST**

#### **Defining a Feature View**
Features like `tenure`, `MonthlyCharges`, and `TotalCharges` are useful for ML models. We'll define a feature view for these features.

1. Create the file `features/feature_views.py`:
   ```python
   from feast import FeatureView, Feature, ValueType
   from feast.data_source import FileSource

   # Define the data source (Parquet file)
   customer_data_source = FileSource(
       path="data/customer_churn.parquet",
       event_timestamp_column="tenure"  # Treat tenure as a timestamp for simplicity
   )

   # Define feature view
   customer_feature_view = FeatureView(
       name="customer_features",
       entities=["customer_id"],  # Link features to customer_id
       ttl=None,  # No TTL for now
       schema=[
           Feature(name="MonthlyCharges", dtype=ValueType.FLOAT),
           Feature(name="TotalCharges", dtype=ValueType.FLOAT),
           Feature(name="tenure", dtype=ValueType.INT32),
       ],
       online=True,
       batch_source=customer_data_source,
   )
   ```



### **7. Understanding FEAST Architecture**

#### **How It Works**
1. **Offline Store**: Historical features for training.
2. **Online Store**: Real-time features for inference.

#### **Architecture Overview**
1. Features are ingested into the **offline store**.
2. Features are materialized to the **online store**.
3. ML models query features for predictions.



### **8. Online Store and Offline Store**

1. **Configuration**: Update `feature_store.yaml`:
   ```yaml
   project: customer_churn_project
   registry: data/registry.db
   provider: local

   offline_store:
       type: file

   online_store:
       type: redis
       connection_string: "localhost:6379"
   ```

2. **Start Redis** (for online store):
   ```bash
   docker run -d -p 6379:6379 redis
   ```



### **9. Data Retrieval in FEAST**

#### **Retrieve Training Data**
```python
from feast import FeatureStore

# Initialize feature store
fs = FeatureStore(repo_path=".")

# Retrieve training data
training_df = fs.get_historical_features(
    entity_df="SELECT customerID as customer_id FROM data/customer_churn.parquet",
    feature_refs=["customer_features:MonthlyCharges", "customer_features:TotalCharges"],
).to_df()

print(training_df)
```

#### **Retrieve Real-Time Data**
```python
# Fetch features for a specific customer
online_features = fs.get_online_features(
    entity_rows=[{"customer_id": "7590-VHVEG"}],  # Customer ID
    feature_refs=["customer_features:MonthlyCharges", "customer_features:TotalCharges"],
).to_dict()

print(online_features)
```



### **10. Different Commands in FEAST**

1. **Materialize Features**:
   ```bash
   feast materialize $(date -u -d "7 days ago" '+%Y-%m-%dT%H:%M:%S') $(date -u '+%Y-%m-%dT%H:%M:%S')
   ```

2. **Validate Feature Store**:
   ```bash
   feast validate
   ```

3. **List Features**:
   ```bash
   feast list features
   ```

4. **Apply Changes**:
   ```bash
   feast apply
   ```



### **Conclusion**
This lab introduced FEAST concepts using a customer churn dataset. You learned:
- How to define **entities** and **feature views**.
- The role of **offline** and **online** stores.
- How to retrieve data for training and inference.
- Useful FEAST commands for managing features.

You now have a basic understanding of how FEAST operates, and you can expand this knowledge for more complex workflows. Let me know if you need further assistance or an advanced lab!