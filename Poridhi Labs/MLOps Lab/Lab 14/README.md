### **Model Monitoring with Grafana and Prometheus**

Machine learning projects require **continuous monitoring** post-deployment to ensure the model's performance doesn’t degrade. Tools like **Grafana** allow data scientists and ML engineers to monitor and visualize production models in real-time, enabling timely actions when performance drops.

In this lab, we will:

- Build a regression model to predict diamond prices.
- Create a REST API to serve predictions and expose monitoring metrics.
- Detect data drift and concept drift in real-time.
- Visualize metrics using Grafana and monitor them using Prometheus.
- Set up the system in Docker for easy deployment.


### **Why Monitoring Is Necessary**
ML models degrade in production due to:
1. **Data Drift**: Changes in input data distributions compared to training data.
   - **Example**: A robot trained to sort red apples might fail when faced with green apples.
   - **Impact**: Poor predictions due to outdated input patterns.
2. **Concept Drift**: Changes in the relationship between input features and the target variable.
   - **Example**: A preference shift to underripe apples changes the model's logic.
   - **Impact**: Model assumptions become invalid, requiring updates.

### **Why It Matters**
Monitoring detects drift early, enabling:
- Timely retraining.
- Feature engineering adjustments.
- Model updates to maintain reliability.



### **Required Tools**
- **Grafana**: Visualization dashboards and alerting.
- **Prometheus**: Metrics collection and storage.
- **Flask**: REST API for predictions and metrics.
- **Scikit-learn**: Model building and preprocessing.
- **SciPy**: Statistical tests for drift detection.
- **Docker and Docker Compose**: Containerization and deployment.
- **APScheduler**: Scheduling drift checks.


### **Project Structure**
```
grafana_model_monitoring/
├── src/
│   ├── app.py               # Flask API for model serving and metrics
│   ├── train.py             # Model training and pipeline creation
│   ├── monitoring/
│       ├── data_drift.py    # Data drift detection
│       ├── concept_drift.py # Concept drift detection
├── prometheus.yml           # Prometheus configuration
├── Dockerfile               # Docker configuration for the app
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
```

### Setting up the environment

Run the following command to create a virtual environment named `venv` and `activate` it:
```bash
python -m venv venv
source venv/bin/activate
```

Create a file named `requirements.txt` and save the following dependencies:
```
scikit-learn
numpy
pandas
seaborn
flask
apscheduler
prometheus-client
joblib
werkzeug
```

Install the dependencies
```bash
pip install requirements.txt
```

### Create the project structure
We create a working directory called `grafana_model_monitoring` and populate it with folders and initial files:
```bash
mkdir grafana_model_monitoring; cd grafana_model_monitoring
mkdir src  # To store python scripts
touch src/{app.py,concept_drift.py,data_drift.py,train.py}  # Scripts
touch Dockerfile docker-compose.yml prometheus.yml  # Configuration
```



#### **Setup the Model**
As an example, we will use the `Diamonds` dataset from the `Seaborn` library to predict diamond prices. This dataset includes both numerical and categorical features, necessitating pre-processing before model training.

**`src/train.py`**
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import pandas as pd
import seaborn as sns

def train_model():
    # Load the diamonds dataset
    diamonds = sns.load_dataset("diamonds")

    # Separate features and target
    X = diamonds[["carat", "cut", "color", "clarity", "depth", "table"]]
    y = diamonds["price"]

    # Create preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), ["carat", "depth", "table"]),
            ("cat", OneHotEncoder(drop="first", sparse=False), ["cut", "color", "clarity"]),
        ]
    )

    # Create a pipeline that includes preprocessing and the model
    model_pipeline = Pipeline(
        [("preprocessor", preprocessor), ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))]
    )

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fit the pipeline
    model_pipeline.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model_pipeline.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model MSE: {mse}")

    # Save the entire pipeline
    joblib.dump(model_pipeline, "src/model_pipeline.joblib")
    print("Model pipeline saved successfully.")

if __name__ == "__main__":
    train_model()
```

**Train the Model**:
```bash
python src/train.py
```
The script defines a `train_model()` function that performs the following steps:

1. **Load Dataset**: Imports the Diamonds dataset from Seaborn.
2. **Preprocessing Setup**: Creates a `ColumnTransformer` using Scikit-learn to:
   - One-hot encode categorical features.
   - Scale numeric features.
3. **Model Pipeline Creation**: Combines the preprocessing transformer with a `RandomForestRegressor` to form a complete `model_pipeline`.
4. **Data Splitting and Training**: Splits the data into training and testing sets, then trains the pipeline on the training data.
5. **Model Evaluation**: Evaluates the model's performance on the test set by calculating the Mean Squared Error (MSE).
6. **Save the Pipeline**: Saves the trained model pipeline as a serialized object using `joblib`.

This script lays the foundation for building the REST API, which will serve predictions and expose monitoring metrics.

