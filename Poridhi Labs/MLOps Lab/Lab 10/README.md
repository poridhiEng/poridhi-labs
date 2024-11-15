# Saleprice Prediction with XGBoost Regressor and Tracking with MLflow

This project leverages the "House Prices - Advanced Regression Techniques" dataset and implements a saleprice prediction model using XGBoost Regressor. We integrate MLflow for experiment tracking, PostgreSQL for metadata storage, and Amazon S3 for artifact storage.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-28.png)

## Table of Contents
- [Overview](#1-overview)
- [Project Structure](#2-project-structure)
- [Environment Setup](#3-environment-setup)
- [Data Processing & Visualization](#4-data-processing--visualization)
- [Model Training & MLflow Tracking](#5-model-training--mlflow-tracking)
- [Model Prediction](#6-model-prediction)
- [Verification](#7-verification)
- [Conclusion](#8-conclusion)

## 1. Overview

This project implements Saleprice Prediction with XGBoost Regressor while incorporating MLOps best practices:

- Experiment tracking with MLflow
- Model metadata storage in PostgreSQL
- Artifact storage in AWS S3
- Containerized deployment using Docker
- Comparison of multiple models' performance

## 2. Project Structure

```sh
Saleprice-Prediction-with-XGBoost-Regressor/
├── Docker/
│   ├── .env
│   ├── Dockerfile
│   └── docker-compose.yml         
├── Notebooks/
│   ├── saleprice-prediction-with-xgboost-regressor.ipynb    
│   └── house-prices-advanced-regression-techniques/
|       |-- test.csv
|       |-- train.csv
```                     

## 3. Environment Setup

### Configure AWS

```bash
aws configure
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-24.png)

### Kernel Setup

In Poridhi's VSCode server, create a new Jupyter notebook and select the `python` kernel.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-2.png)

### Create S3 Bucket

Create a new S3 bucket with the following command:

```bash
aws s3api create-bucket --bucket <unique-bucket-name> --region ap-southeast-1 --create-bucket-configuration LocationConstraint=ap-southeast-1 

aws s3api put-bucket-versioning --bucket <unique-bucket-name> --versioning-configuration Status=Enabled

aws s3api get-bucket-versioning --bucket <unique-bucket-name>
```
>NOTE: Replace `<unique-bucket-name>` with your own bucket name. Make sure the bucket name is unique across all AWS accounts.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-25.png)

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
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
    networks:
      - mlflow-network

networks:
  mlflow-network:
    driver: bridge

volumes:
  postgres_data:
```

Create a `.env` file in the same directory as `docker-compose.yml` and add the following:

```bash
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_DEFAULT_REGION=<your-region>
```

>NOTE: Replace `<your-access-key-id>`, `<your-secret-access-key>`, and `<your-region>` with your own AWS credentials and region. Make sure to keep the `.env` file private by not pushing it to the remote repository.

**Key Features:**

1. PostgreSQL for metadata storage
2. MLflow server with S3 integration
3. Environment variable management
4. Health checks
5. Data persistence

#### **Dockerfile**

Create a `Dockerfile` with the following content:

```dockerfile
FROM python:3.8-slim-buster

WORKDIR /mlflow

RUN pip install mlflow psycopg2-binary boto3

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "postgresql://mlflow:mlflow@postgres/mlflow", \
     "--default-artifact-root", "s3://saleprice-prediction/mlflow-artifacts"]
```
#### Build and run the containers

```bash
docker-compose up --build -d
```

#### Access the MLflow UI
To access the MLflow UI, goto `PORTS` section and click on the provided link. `Poridhi's VSCode server` will automatically open the MLflow UI in your default browser.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image.png)

After clicking on the link, you will be redirected to the MLflow UI:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-1.png)

## 4. Data Processing & Visualization

### Install required libraries

Create a new Jupyter notebook and install the required libraries:

```bash
pip install numpy pandas matplotlib seaborn plotly imbalanced-learn nbformat ipython xgboost mlflow boto3
```

### Importing Libraries

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from datetime import datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from mlflow.tracking import MlflowClient
```

### Setting up MLflow Tracking

```python
mlflow.set_tracking_uri("http://localhost:5000")  # Replace with your MLflow server URI
mlflow.set_experiment("House Price Prediction lab 10")
```
**Purpose:**

1. Connects the script to an MLflow tracking server where experiment details (e.g., metrics, parameters, and models) will be logged.
2. `http://localhost:5000:` Specifies the URI of the MLflow tracking server running locally. Replace this with the actual server address if using a remote setup.

3. Specifies the experiment name under which runs will be grouped in the MLflow tracking server. If the experiment does not exist, MLflow will create it.

>NOTE: Replace `http://localhost:5000` with your MLflow server URI.

### Download Dataset

First, download the dataset from [here](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques/data) and save it in the `Notebooks` folder.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-3.png)

### Load Dataset

```python
train_data = pd.read_csv('./house-prices-advanced-regression-techniques/train.csv')
train_data.head()
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-4.png)

### Training Data Cleaning and Preprocessing

**Check data information**

```python
train_data.info()
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-5.png)

**Check for missing values**

Count the number of missing (null) values in each column of the train_data DataFrame.

```python
train_data.isnull().sum()
train_data.shape
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-6.png)

Here we can see that `LotFrontage` has 259 missing values.

**Drop unnecessary columns**

```python
train_data.drop(['Alley', 'PoolQC', 'Fence', 'MiscFeature', 'Id', 'GarageYrBlt'], axis=1, inplace = True)
```

This command removes columns deemed irrelevant for the prediction task or those with excessive missing data.

**Fill missing values**

```python
train_data['LotFrontage']=train_data['LotFrontage'].fillna(train_data['LotFrontage'].mode()[0])
train_data['BsmtCond']=train_data['BsmtCond'].fillna(train_data['BsmtCond'].mode()[0])
train_data['BsmtQual']=train_data['BsmtQual'].fillna(train_data['BsmtQual'].mode()[0])
train_data['FireplaceQu']=train_data['FireplaceQu'].fillna(train_data['FireplaceQu'].mode()[0])
train_data['GarageType']=train_data['GarageType'].fillna(train_data['GarageType'].mode()[0])
train_data['GarageFinish']=train_data['GarageFinish'].fillna(train_data['GarageFinish'].mode()[0])
train_data['GarageQual']=train_data['GarageQual'].fillna(train_data['GarageQual'].mode()[0])
train_data['GarageCond']=train_data['GarageCond'].fillna(train_data['GarageCond'].mode()[0])
```

Here we have replaced the missing values with the mode of the column. 

- **Handling Strategy:** Missing values are replaced with the mode (most frequent value) of the column.
- **Reason:** Mode imputation is often used for categorical-like or non-normally distributed continuous data.
- **fillna():** Replaces missing values with the specified value.

- **Similarly handled categorical-like columns:** `BsmtCond`, `BsmtQual`, `FireplaceQu`, `GarageType`, `GarageFinish`, `GarageQual`, `GarageCond`. These columns are filled with their respective modes.


**Check for missing values again**

After filling the missing values, we can see that there are still missing values in the dataset.

```python
train_data.isnull().sum().sum()
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-7.png)

**Visualizing missing values:**

```python
import seaborn as sns
sns.heatmap(train_data.isnull(),yticklabels=False,cbar=False,cmap='coolwarm')
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-8.png)

- **Purpose**: Displays a heatmap to visualize where missing values (`NaN`) exist in the dataset.
  - **`train_data.isnull()`**: Creates a boolean DataFrame where `True` indicates missing values and `False` indicates non-missing values.
  - **`yticklabels=False`**: Hides the row labels (index values) for cleaner visualization.
  - **`cbar=False`**: Hides the color bar to focus solely on the missing value patterns.
  - **`cmap='coolwarm'`**: Sets the color scheme for the heatmap, using the "coolwarm" colormap.

- **Output**:
  - Red areas indicate missing values, while blue areas represent non-missing values.
  - Useful for identifying patterns or clusters of missing data.

**Imputing missing values for additional columns:**

```python
train_data['MasVnrType']=train_data['MasVnrType'].fillna(train_data['MasVnrType'].mode()[0])
train_data['MasVnrArea']=train_data['MasVnrArea'].fillna(train_data['MasVnrArea'].mode()[0])
train_data['BsmtExposure']=train_data['BsmtExposure'].fillna(train_data['BsmtExposure'].mode()[0])
train_data['BsmtFinType2']=train_data['BsmtFinType2'].fillna(train_data['BsmtFinType2'].mode()[0])
```

**Purpose**: Handles missing values in these columns.

**Columns**:
- `MasVnrType`: A categorical-like column indicating the type of masonry veneer.
- `MasVnrArea`: A numerical column representing the area of masonry veneer.
- `BsmtExposure`: A categorical-like column indicating the exposure level of the basement.
- `BsmtFinType2`: A categorical-like column representing the secondary basement finish type.

**Handling Strategy (Mode Imputation)**:

- Most frequent value (mode) of each column is used to fill missing values.
- Suitable for categorical-like columns or skewed numerical data.

#### **3. Visualizing missing values after imputation:**

```python
sns.heatmap(train_data.isnull(), yticklabels=False, cbar=False, cmap='YlGnBu')
train_data.dropna(inplace=True)
```

**Purpose**: Re-visualizes the missing values in the dataset after filling the columns mentioned above.

### Test Data Loading

```python
test_data = pd.read_csv('./house-prices-advanced-regression-techniques/test.csv')
test_data.head()
```

### Test Data Cleaning and Preprocessing

**Check for missing values**

```python
test_data.isnull().sum()
test_data.shape
```

**Dropping Irrelevant Columns**

```python
test_data.drop(['Alley', 'PoolQC', 'Fence', 'MiscFeature', 'Id', 'GarageYrBlt'], axis=1, inplace = True)
```

**Filling Missing Values for Specific Columns**

```python
test_data['LotFrontage']=test_data['LotFrontage'].fillna(test_data['LotFrontage'].mode()[0])
test_data['BsmtCond']=test_data['BsmtCond'].fillna(test_data['BsmtCond'].mode()[0])
test_data['BsmtQual']=test_data['BsmtQual'].fillna(test_data['BsmtQual'].mode()[0])
test_data['FireplaceQu']=test_data['FireplaceQu'].fillna(test_data['FireplaceQu'].mode()[0])
test_data['GarageType']=test_data['GarageType'].fillna(test_data['GarageType'].mode()[0])
test_data['GarageFinish']=test_data['GarageFinish'].fillna(test_data['GarageFinish'].mode()[0])
test_data['GarageQual']=test_data['GarageQual'].fillna(test_data['GarageQual'].mode()[0])
test_data['GarageCond']=test_data['GarageCond'].fillna(test_data['GarageCond'].mode()[0])
test_data['MasVnrType']=test_data['MasVnrType'].fillna(test_data['MasVnrType'].mode()[0])
test_data['MasVnrArea']=test_data['MasVnrArea'].fillna(test_data['MasVnrArea'].mode()[0])
test_data['BsmtExposure']=test_data['BsmtExposure'].fillna(test_data['BsmtExposure'].mode()[0])
test_data['BsmtFinType2']=test_data['BsmtFinType2'].fillna(test_data['BsmtFinType2'].mode()[0])
```
**Explanation:**

- Similar to the training data, we fill the missing values for the columns mentioned above using the mode of the column.

**Checking Remaining Missing Values**

```python
test_data.loc[:, test_data.isnull().any()].head()
```
**Further Imputation**

```python
test_data['Utilities']=test_data['Utilities'].fillna(test_data['Utilities'].mode()[0])
test_data['Exterior1st']=test_data['Exterior1st'].fillna(test_data['Exterior1st'].mode()[0])
test_data['Exterior2nd']=test_data['Exterior2nd'].fillna(test_data['Exterior2nd'].mode()[0])
test_data['BsmtFinType1']=test_data['BsmtFinType1'].fillna(test_data['BsmtFinType1'].mode()[0])
test_data['BsmtFinSF1']=test_data['BsmtFinSF1'].fillna(test_data['BsmtFinSF1'].mean())
test_data['BsmtFinSF2']=test_data['BsmtFinSF2'].fillna(test_data['BsmtFinSF2'].mean())
test_data['BsmtUnfSF']=test_data['BsmtUnfSF'].fillna(test_data['BsmtUnfSF'].mean())
test_data['TotalBsmtSF']=test_data['TotalBsmtSF'].fillna(test_data['TotalBsmtSF'].mean())
test_data['BsmtFullBath']=test_data['BsmtFullBath'].fillna(test_data['BsmtFullBath'].mode()[0])
test_data['BsmtHalfBath']=test_data['BsmtHalfBath'].fillna(test_data['BsmtHalfBath'].mode()[0])
test_data['KitchenQual']=test_data['KitchenQual'].fillna(test_data['KitchenQual'].mode()[0])
test_data['Functional']=test_data['Functional'].fillna(test_data['Functional'].mode()[0])
test_data['GarageCars']=test_data['GarageCars'].fillna(test_data['GarageCars'].mean())
test_data['GarageArea']=test_data['GarageArea'].fillna(test_data['GarageArea'].mean())
test_data['SaleType']=test_data['SaleType'].fillna(test_data['SaleType'].mode()[0])
```

**Checking Data Shape**

Confirms the dimensions of the dataset after all preprocessing steps.

```python
test_data.shape
```

### Handling Categorical Features

Defining a list of categorical columns to be transformed into numerical values.

```python
columns=['MSZoning','Street','LotShape','LandContour','Utilities','LotConfig','LandSlope','Neighborhood',
         'Condition2','BldgType','Condition1','HouseStyle','SaleType',
        'SaleCondition','ExterCond',
         'ExterQual','Foundation','BsmtQual','BsmtCond','BsmtExposure','BsmtFinType1','BsmtFinType2',
        'RoofStyle','RoofMatl','Exterior1st','Exterior2nd','MasVnrType','Heating','HeatingQC',
         'CentralAir',
         'Electrical','KitchenQual','Functional',
         'FireplaceQu','GarageType','GarageFinish','GarageQual','GarageCond','PavedDrive']
```

**Encoding Function:**

```python
def category_onehot_multcols(multcolumns):
    data_final=final_data
    i=0
    for fields in multcolumns:
        
        print(fields)
        df1=pd.get_dummies(final_data[fields],drop_first=True)
        
        final_data.drop([fields],axis=1,inplace=True)
        if i==0:
            data_final=df1.copy()
        else:
            
            data_final=pd.concat([data_final,df1],axis=1)
        i=i+1
       
        
    data_final=pd.concat([final_data,data_final],axis=1)
        
    return data_final
```
**Purpose:**

- Encodes categorical features using one-hot encoding (pd.get_dummies()).
- Drops the original categorical column after encoding to avoid redundancy.

**Copying Train Data**

```python
train_data2 = train_data.copy()
```
Creating a copy of train_data for further preprocessing, ensuring the original dataset remains unaltered.

### Merging Train and Test Data

**1. Combining Training and Test Data**

```python
final_data=pd.concat([train_data,test_data],axis=0)
```

**Purpose**: Combines `train_data` and `test_data` into one DataFrame (`final_data`) to ensure consistent preprocessing for both datasets.

**2. Checking Initial Information**

```python
final_data['SalePrice']
final_data.shape
```

**3. One-Hot Encoding**

```python
final_data=category_onehot_multcols(columns)
```

This converts categorical columns listed in `columns` into numerical format using one-hot encoding.

#### **4. Removing Duplicate Columns**

```python
final_data = final_data.loc[:,~final_data.columns.duplicated()]
```

#### **5. Checking Missing Values**

```python
final_data.isnull().sum().sum()
```

#### **6. Data Type Conversion**

```python
boolean_columns = ['Min1', 'Min2', 'Typ', 'Attchd', 'Basment', 'BuiltIn', 'CarPort', 'Detchd', 'RFn', 'P']
for col in boolean_columns:
    final_data[col] = final_data[col].astype(int)
    final_data[col] = final_data[col].astype(int)

final_data.dtypes
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-10.png)

```python
numeric_columns = final_data.select_dtypes(include=['int64', 'float64']).columns
final_data[numeric_columns] = final_data[numeric_columns].astype(float)

final_data.dtypes
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-9.png)

**Purpose**:
- Converts `boolean_columns` to integer type for consistent numerical representation.
- Ensures all numeric columns are of type `float64`, as some models perform better with floats.

**7. Identifying Columns with Missing Values**

```python
null_values_before = final_data.isnull().sum().sum()
null_columns = final_data.columns[final_data.isnull().any()].tolist()
print("Columns with null values:")
for col in null_columns:
    print(f"{col}: {final_data[col].isnull().sum()} nulls")
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-11.png)

**8. Handling Remaining Missing Values**

```python
for col in null_columns:
    if final_data[col].dtype == 'object':
        # For categorical columns, fill with mode
        final_data[col] = final_data[col].fillna(final_data[col].mode()[0])
    else:
        # For numerical columns, fill with mean
        final_data[col] = final_data[col].fillna(final_data[col].mean())

# Verify all nulls are handled
print("Remaining null values:", final_data.isnull().sum().sum())
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-12.png)

- **Purpose**:
  - Ensures all missing values have been addressed, with `0` nulls expected.

### Logging Data Preprocessing Steps and Metrics using MLflow

MLflow Tracking is a key component of MLflow, designed to manage and track experiments in machine learning projects. The code uses MLflow to track and log key aspects of the data preprocessing pipeline.

```python
with mlflow.start_run(run_name="data_preprocessing") as run:
    # Log dataset info
    mlflow.log_param("dataset_size", len(final_data))
    mlflow.log_param("num_features", final_data.shape[1])
    
    # Log preprocessing steps
    preprocessing_steps = {
        "dropped_columns": ['Alley', 'PoolQC', 'Fence', 'MiscFeature', 'Id', 'GarageYrBlt'],
        "filled_null_columns": ["LotFrontage", "BsmtCond", "BsmtQual", "FireplaceQu", 
                              "GarageType", "GarageFinish", "GarageQual", "GarageCond"]
    }
    mlflow.log_dict(preprocessing_steps, "preprocessing_steps.json")
    
    # Log data quality metrics
    data_quality_metrics = {
        "null_values_before": null_values_before,
        "null_values_after": final_data.isnull().sum().sum()
    }
    mlflow.log_metrics(data_quality_metrics)
```

**Purpose:**

- Logs the dataset's size (number of rows) and number of features (columns) to track dataset characteristics.
- Logs the preprocessing steps and the columns that were dropped and null values that were filled.
- Logs the data quality metrics before and after preprocessing to monitor the effectiveness of the cleaning process.

**MLflow Outputs:**

- Parameters: `dataset_size`, `num_features`
- Metrics: `null_values_before`, `null_values_after`
- Artifacts: `preprocessing_steps.json` (Preprocessing details)

After running the above code, we can see the parameters, metrics and artifacts in the MLflow UI.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-14.png)

### Data set split training and testing

```python
data_train=final_data.iloc[:1422,:]
data_test=final_data.iloc[1422:,:]
```

### Feature and Target Split

```python
X_train=data_train.drop(['SalePrice'],axis=1)
y_train=data_train['SalePrice']
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-15.png)

``X_train:`` This selects all columns except for SalePrice from data_train as features. drop(['SalePrice'], axis=1) removes the target variable (SalePrice) from the DataFrame, leaving only the predictors (features).

`y_train:` This selects the SalePrice column from data_train as the target variable. y_train represents the actual target (SalePrice) values for training.

## 5. Model Training & MLflow Tracking

Now we will train the model using XGBoost. We will follow a structured approach to training an `XGBoost` regression model, performing hyperparameter tuning via `RandomizedSearchCV`, logging metrics, and using MLflow to track the process. 

**Hyperparameter Grid and Search Setup**

The code defines a hyperparameter grid (hyperparameter_grid) that is passed to the RandomizedSearchCV. This grid includes:

- `n_estimators`: Number of boosting rounds (trees).
- `max_depth`: Maximum depth of the tree.
- `learning_rate`: The learning rate for boosting.
- `min_child_weight`: Minimum sum of instance weight (hessian) in a child.
- `booster`: Type of boosting model (either gbtree or gblinear).
- `base_score`: The initial prediction score used in boosting.

```python
import xgboost
regressor=xgboost.XGBRegressor()

booster=['gbtree','gblinear']
base_score=[0.25,0.5,0.75,1]

n_estimators = [100, 500, 900, 1100, 1500]
max_depth = [2, 3, 5, 10, 15]
booster=['gbtree','gblinear']
learning_rate=[0.05,0.1,0.15,0.20]
min_child_weight=[1,2,3,4]

# Define the grid of hyperparameters to search
hyperparameter_grid = {
    'n_estimators': n_estimators,
    'max_depth':max_depth,
    'learning_rate':learning_rate,
    'min_child_weight':min_child_weight,
    'booster':booster,
    'base_score':base_score
    }
```
**Randomized Search with Cross-Validation**

Then we will perform **RandomizedSearchCV**, which will search through a random combination of the hyperparameters defined in `hyperparameter_grid`. This is useful when we want to perform an exhaustive search over a large space but with fewer combinations than GridSearchCV. The search uses 5-fold cross-validation (`cv=5`) and optimizes based on the negative mean absolute error (`scoring='neg_mean_absolute_error'`).

```python
from sklearn.model_selection import RandomizedSearchCV
random_cv = RandomizedSearchCV(estimator=regressor,
            param_distributions=hyperparameter_grid,
            cv=5, n_iter=50,
            scoring = 'neg_mean_absolute_error',n_jobs = 4,
            verbose = 5, 
            return_train_score = True,
            random_state=2)
```

**Model Evaluation**

The evaluation function `evaluate_model()` calculates and returns various regression metrics like Mean Squared Error (MSE), Mean Absolute Error (MAE), R², and Root Mean Squared Error (RMSE).

```python
def evaluate_model(model, X, y):
    predictions = model.predict(X)
    mse = mean_squared_error(y, predictions)
    mae = mean_absolute_error(y, predictions)
    r2 = r2_score(y, predictions)
    return {"mse": mse, "mae": mae, "r2": r2, "rmse": np.sqrt(mse)}
```

**MLflow Tracking**

With MLflow, we are tracking the following:

- `Hyperparameter Grid`: The parameters are logged into a JSON file.
- `Best Parameters`: The best parameters from the randomized search are logged.
- `Cross-Validation Results`: You log results of the cross-validation process, including the mean and standard deviation of train and test scores.
- `Model Evaluation Metrics`: The training set evaluation metrics (MSE, MAE, etc.) for the best model are logged.
- `Feature Importance Plot`: After the model is trained, you generate a plot to visualize the top 10 most important features, based on the model's feature importance values, and log the plot as an image.
- `Best Model`: The best model, identified by the randomized search, is logged in MLflow using mlflow.xgboost.log_model().


```python
with mlflow.start_run(run_name="model_training") as run:
    # Log hyperparameter search space
    mlflow.log_dict(hyperparameter_grid, "hyperparameter_grid.json")
    
    # Perform RandomizedSearchCV
    random_cv.fit(X_train, y_train)
    
    # Log best parameters
    mlflow.log_params(random_cv.best_params_)
    
    # Log cross-validation results
    cv_results = {
        "mean_test_score": random_cv.cv_results_['mean_test_score'],
        "std_test_score": random_cv.cv_results_['std_test_score'],
        "mean_train_score": random_cv.cv_results_['mean_train_score'],
        "std_train_score": random_cv.cv_results_['std_train_score']
    }
    mlflow.log_dict(cv_results, "cv_results.json")
    
    # Log best model metrics
    best_model = random_cv.best_estimator_
    train_metrics = evaluate_model(best_model, X_train, y_train)
    mlflow.log_metrics(train_metrics)
    
    # Log feature importance plot
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    plt.figure(figsize=(10, 6))
    plt.bar(feature_importance['feature'][:10], feature_importance['importance'][:10])
    plt.xticks(rotation=45)
    plt.title('Top 10 Feature Importance')
    plt.tight_layout()
    mlflow.log_figure(plt.gcf(), "feature_importance.png")
    
    # Log the model
    mlflow.xgboost.log_model(best_model, "model",
                            registered_model_name="house_price_prediction_model")

    # Print best score and parameters
    print(f"Best score: {random_cv.best_score_}")
    print(f"Best parameters: {random_cv.best_params_}")
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-26.png)

**MLflow Outputs:**

You will see the best score and parameters in the MLflow UI.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-16.png)

**Pickling the Best Model**

```python
import pickle
best_model = random_cv.best_estimator_
filename = 'finalized_model.pkl'
pickle.dump(best_model, open(filename, 'wb'))
```

## 6. Model Prediction

```python
import os
with mlflow.start_run(run_name="model_prediction") as run:
    # Make predictions
    y_pred = best_model.predict(data_test)
    
    # Log prediction statistics
    prediction_stats = {
        "mean_predicted_price": float(np.mean(y_pred)),
        "median_predicted_price": float(np.median(y_pred)),
        "std_predicted_price": float(np.std(y_pred)),
        "min_predicted_price": float(np.min(y_pred)),
        "max_predicted_price": float(np.max(y_pred))
    }
    mlflow.log_metrics(prediction_stats)
    
    # Create and save predictions to a CSV file
    prediction_df = pd.DataFrame({
        'predicted_price': y_pred
    })
    
    # Save predictions locally
    predictions_path = "predictions.csv"
    prediction_df.to_csv(predictions_path, index=False)
    
    # Log the predictions file
    mlflow.log_artifact(predictions_path)
    
    # Create and log a histogram of predictions
    plt.figure(figsize=(10, 6))
    plt.hist(y_pred, bins=50)
    plt.title('Distribution of Predicted House Prices')
    plt.xlabel('Predicted Price')
    plt.ylabel('Frequency')
    mlflow.log_figure(plt.gcf(), "prediction_distribution.png")
    
    # Log model version and status
    client = MlflowClient()
    try:
        model_version = client.get_latest_versions("house_price_prediction_model", stages=["None"])[0]
        client.transition_model_version_stage(
            name="house_price_prediction_model",
            version=model_version.version,
            stage="Production"
        )
    except Exception as e:
        print(f"Error updating model version: {str(e)}")
    
    # Clean up
    plt.close()
    if os.path.exists(predictions_path):
        os.remove(predictions_path)
```
In this code, we are tracking the following:

1. **Start MLflow Run:** The code begins a new MLflow run to track the experiment's metrics and artifacts.
2. **Make Predictions:** The best model is used to make predictions on the test data.
3. **Log Prediction Stats:** Key statistics (mean, median, std, min, max) of the predicted values are logged to MLflow.
4. **Save Predictions to CSV:** Predicted prices are saved in a CSV file for later use.
5. **Log Predictions File:** The CSV file is logged as an artifact in MLflow.
6. **Log Histogram:** A histogram of predictions is generated and logged as an image in MLflow.
7. **Update Model Version:** The model is transitioned to the "Production" stage in MLflow's model registry.
8. **Cleanup:** Temporary files (e.g., CSV, plots) are deleted after being logged to MLflow.

The code makes predictions, logs metrics and artifacts (CSV, plot), and manages model versioning in MLflow while cleaning up temporary files.

**MLflow Outputs:**

You will see the prediction statistics in the MLflow UI.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-17.png)

### Comparing Different Runs

```python
def compare_runs(experiment_name="House Price Prediction", top_n=5):
    """Compare different runs and their metrics"""
    
    # Start a new MLflow run to track this comparison process
    with mlflow.start_run(run_name="model_comparison"):
        client = MlflowClient()
        experiment = client.get_experiment_by_name(experiment_name)
        
        # Search for runs based on R2 score in descending order
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["metrics.r2 DESC"]
        )
        
        # Create a DataFrame to store the top N runs' performance and parameters
        comparison_df = pd.DataFrame([
            {
                'run_id': run.info.run_id,
                'r2_score': run.data.metrics.get('r2', None),
                'rmse': run.data.metrics.get('rmse', None),
                'mae': run.data.metrics.get('mae', None),
                'parameters': run.data.params
            }
            for run in runs[:top_n]
        ])
        
        # Log comparison DataFrame as an artifact (optional)
        comparison_df_path = "run_comparison.csv"
        comparison_df.to_csv(comparison_df_path, index=False)
        mlflow.log_artifact(comparison_df_path)

        # Optionally, log the best performing run's metrics for tracking
        best_run = runs[0]
        best_run_metrics = {
            "best_r2_score": best_run.data.metrics.get('r2', None),
            "best_rmse": best_run.data.metrics.get('rmse', None),
            "best_mae": best_run.data.metrics.get('mae', None)
        }
        mlflow.log_metrics(best_run_metrics)

        # Print and return the comparison dataframe
        print("Best performing runs:")
        print(comparison_df)

    return comparison_df

# Example usage after model training
best_runs = compare_runs()
```

**MLflow Outputs:**

You will see the best performing runs in the MLflow UI.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-19.png)

### Registering the Best Model

MLflow provides a **model registry** to store, version, and manage machine learning models. Models can be tracked, versioned, and transitioned through different stages like "Staging", "Production", or "Archived".

```python
def register_best_model(experiment_name="House Price Prediction"):
    """Register the best performing model to the model registry"""
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)
    best_run = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.r2 DESC"]
    )[0]
    
    # Register the model from the best run
    model_uri = f"runs:/{best_run.info.run_id}/model"
    mv = mlflow.register_model(model_uri, "house_price_prediction_model")
    
    # Transition the model to production
    client.transition_model_version_stage(
        name="house_price_prediction_model",
        version=mv.version,
        stage="Production"
    )
    
    return mv

# Add after model training
best_model_version = register_best_model()
print(f"Registered model version: {best_model_version.version}")
```

**Model URI:** The model_uri is a reference to the model artifact saved in MLflow, which includes the run ID.

**Transitioning Models:** The model is registered and then transitioned to the "Production" stage using `transition_model_version_stage()`. This makes it the latest active model for production use.

**MLflow Outputs:**

You will see the registered model version in the MLflow UI.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-18.png)

So, we have successfully registered the best model to the model registry and transitioned it to the production stage. We can now use this model for predictions. We can also see the model registry in the MLflow UI. After all the steps, the MLflow UI should look like this showcasing the registered model, experiment, runs, and metrics:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-27.png)

## 7. Verification

### S3 Artifact Verification

As we have used the default S3 bucket, go to AWS Console and navigate to S3 bucket <your-bucket-name> to verify the artifacts.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-20.png)

For each model run, you should see the artifacts in the S3 bucket.

### PostgreSQL Verification

We have used a PostgreSQL database to store the metadata of the experiment, runs, and metrics. We can verify the same using the following steps:

**1. Connect to the PostgreSQL container:**

```bash
docker exec -it <postgres-container-id> /bin/sh
```

**2. Connect to PostgreSQL:**

```sh
psql -h localhost -U mlflow -d mlflow

-- View experiments
SELECT * FROM experiments;
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-21.png)

**3. View the registered models:**

```sh
SELECT * FROM registered_models;
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-22.png)

**4. View runs and metrics:**

```sql
SELECT 
    r.run_uuid,
    r.experiment_id,
    m.key as metric_name,
    m.value as metric_value
FROM runs r
JOIN metrics m ON r.run_uuid = m.run_uuid
WHERE r.experiment_id = '2'
ORDER BY r.start_time DESC;
```
> Replace the experiment_id with the id of the experiment you want to view.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/Lab%2010/images/image-23.png)


## 8. Conclusion

We have successfully implemented the entire MLOps pipeline, from data ingestion to model training, evaluation, and deployment. We have used MLflow to track the experiment, model registry, and S3 artifacts. We have also used PostgreSQL to store the metadata of the experiment, runs, and metrics.
