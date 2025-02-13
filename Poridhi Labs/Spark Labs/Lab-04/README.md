# MLlib(Machine Learning with Spark)



Spark also introduces us a library that is used to handle Machine Learning Models. In this lab, we are going to explore MLlib.

# Table of Contents

1. What is MLlib?
2. Components of MLlib
3. Training a Machine Learning Model using MLlib
4. Training, Evaluating and Comparing multiple Machine Learning Models with MLlib

## What is MLlib?

Apache Spark MLlib is a built-in scalable machine learning library. It provides high-performance toolkit for building machine learning models on distributed datasets. Now here’s the catch, MLlib is used for RDD-based API and for DataFrame-based API Spark ML is recommended.

## Components of MLlib

1. Data Types
2. Feature Engineering
3. ML Algorithm
4. Pipelines
5. Tuning and Evaluation 

![A diagram of what is usually done using MLlib library from Spark for handling Machine Learning Model that are trained with BIg Data.](https://github.com/nakibworkspace/AS-Lab-04/raw/main/image/image1.svg)

A diagram of what is usually done using MLlib library from Spark for handling Machine Learning Model that are trained with BIg Data.

## Training a Machine Learning Model using MLlib

### Import the necessary libraries

```python
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.pipeline import Pipeline
import pyspark.ml.feature as feat
```

### Start the Spark Session

```python
spark= SparkSession.builder \
.appName("Spark for Machine Learning with MLlib") \
.getOrCreate()
```

### Load a dataset and create DataFrame out of it

```python
def load_breast_cancer_data():
  from sklearn.datasets import load_breast_cancer
  import pandas as pd

  data= load_breast_cancer()
  df= pd.DataFrame(data.data, columns= data.feature_names)
  df['target']= data.target

  return spark.createDataFrame(df)
```

```python
data= load_breast_cancer_data()

data.show(5)

+-----------+------------+--------------+---------+---------------+----------------+--------------+-------------------+-------------+----------------------+------------+-------------+---------------+----------+----------------+-----------------+---------------+--------------------+--------------+-----------------------+------------+-------------+---------------+----------+----------------+-----------------+---------------+--------------------+--------------+-----------------------+------+
|mean radius|mean texture|mean perimeter|mean area|mean smoothness|mean compactness|mean concavity|mean concave points|mean symmetry|mean fractal dimension|radius error|texture error|perimeter error|area error|smoothness error|compactness error|concavity error|concave points error|symmetry error|fractal dimension error|worst radius|worst texture|worst perimeter|worst area|worst smoothness|worst compactness|worst concavity|worst concave points|worst symmetry|worst fractal dimension|target|
+-----------+------------+--------------+---------+---------------+----------------+--------------+-------------------+-------------+----------------------+------------+-------------+---------------+----------+----------------+-----------------+---------------+--------------------+--------------+-----------------------+------------+-------------+---------------+----------+----------------+-----------------+---------------+--------------------+--------------+-----------------------+------+
|      17.99|       10.38|         122.8|   1001.0|         0.1184|          0.2776|        0.3001|             0.1471|       0.2419|               0.07871|       1.095|       0.9053|          8.589|     153.4|        0.006399|          0.04904|        0.05373|             0.01587|       0.03003|               0.006193|       25.38|        17.33|          184.6|    2019.0|          0.1622|           0.6656|         0.7119|              0.2654|        0.4601|                 0.1189|     0|
|      20.57|       17.77|         132.9|   1326.0|        0.08474|         0.07864|        0.0869|            0.07017|       0.1812|               0.05667|      0.5435|       0.7339|          3.398|     74.08|        0.005225|          0.01308|         0.0186|              0.0134|       0.01389|               0.003532|       24.99|        23.41|          158.8|    1956.0|          0.1238|           0.1866|         0.2416|               0.186|         0.275|                0.08902|     0|
|      19.69|       21.25|         130.0|   1203.0|         0.1096|          0.1599|        0.1974|             0.1279|       0.2069|               0.05999|      0.7456|       0.7869|          4.585|     94.03|         0.00615|          0.04006|        0.03832|             0.02058|        0.0225|               0.004571|       23.57|        25.53|          152.5|    1709.0|          0.1444|           0.4245|         0.4504|               0.243|        0.3613|                0.08758|     0|
|      11.42|       20.38|         77.58|    386.1|         0.1425|          0.2839|        0.2414|             0.1052|       0.2597|               0.09744|      0.4956|        1.156|          3.445|     27.23|         0.00911|          0.07458|        0.05661|             0.01867|       0.05963|               0.009208|       14.91|         26.5|          98.87|     567.7|          0.2098|           0.8663|         0.6869|              0.2575|        0.6638|                  0.173|     0|
|      20.29|       14.34|         135.1|   1297.0|         0.1003|          0.1328|         0.198|             0.1043|       0.1809|               0.05883|      0.7572|       0.7813|          5.438|     94.44|         0.01149|          0.02461|        0.05688|             0.01885|       0.01756|               0.005115|       22.54|        16.67|          152.2|    1575.0|          0.1374|            0.205|            0.4|              0.1625|        0.2364|                0.07678|     0|
+-----------+------------+--------------+---------+---------------+----------------+--------------+-------------------+-------------+----------------------+------------+-------------+---------------+----------+----------------+-----------------+---------------+--------------------+--------------+-----------------------+------------+-------------+---------------+----------+----------------+-----------------+---------------+--------------------+--------------+-----------------------+------+
```

### Feature Engineering

```python
def preprocess_data(data):
    # Select features and target
    feature_columns = data.columns[:-1]

    # Vector Assembler to combine features
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")

    # Standard Scaler for feature scaling
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")

    return assembler, scaler

# Create preprocessing transformers
assembler, scaler = preprocess_data(data)
```

### Splitting the dataset

```python
(train_data, test_data) = data.randomSplit([0.7, 0.3], seed=42)
```

### Pipeline Creation

```python
def create_ml_pipeline(assembler, scaler):
    lr = LogisticRegression(
        featuresCol="scaled_features",
        labelCol="target",
        predictionCol="prediction",
        probabilityCol="probability"
    )

    
    pipeline = Pipeline(stages=[
        assembler,   
        scaler,      
        lr           
    ])

    return pipeline

ml_pipeline = create_ml_pipeline(assembler, scaler)
```

### Training and Predictions

```python
model = ml_pipeline.fit(train_data)

predictions = model.transform(test_data)
```

### Evaluation process of the model

```python
def evaluate_model(predictions):
    evaluator = BinaryClassificationEvaluator(
        labelCol="target",
        metricName="areaUnderROC"
    )

    
    auc = evaluator.evaluate(predictions)
    print(f"Area Under ROC: {auc}")

    
    accuracy = predictions.filter(
        predictions.target == predictions.prediction
    ).count() / predictions.count()

    print(f"Model Accuracy: {accuracy * 100:.2f}%")

evaluate_model(predictions)

Output:

Area Under ROC: 0.9855287569573283
Model Accuracy: 96.86%
```

### Save the model

Saving the model when gets best accuracy

```python
def save_model(model, path="./breast_cancer_model"):
    model.write().overwrite().save(path)
    print(f"Model saved to {path}")
save_model(model)
```

## Training, Evaluating and Comparing multiple Machine Learning Models with MLlib

Using MLlib, we can also evaluate multiple models at once with `MulticlassClassificationEvaluator` . Let’s start with the necessary imports along with the previous ones.

```python
from pyspark.ml.classification import RandomForestClassifier, GBTClassifier, DecisionTreeClassifier # Corrected import statement
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
```

Defining the models we are trying to compare. Here we’ve taken `LogisticRegression`, `RandomForestClassifier`, `GBTClassifier`, `DecisionTreeClassifier`.

```python
models = {
    "Logistic Regression": LogisticRegression(
        featuresCol="scaled_features",
        labelCol="target"
    ),
    "Random Forest": RandomForestClassifier(
        featuresCol="scaled_features",
        labelCol="target",
        numTrees=100
    ),
    "Gradient Boosted Trees": GBTClassifier(
        featuresCol="scaled_features",
        labelCol="target",
        maxIter=10
    ),
    "Decision Tree": DecisionTreeClassifier(
        featuresCol="scaled_features",
        labelCol="target"
    )
}
```

### **Evaluating the models**

```python
def evaluate_model(predictions, model_name):
    binary_evaluator = BinaryClassificationEvaluator(labelCol="target")
    multi_evaluator = MulticlassClassificationEvaluator(labelCol="target")

    metrics = {
        "Model": model_name,
        "AUC": binary_evaluator.evaluate(predictions),
        "Accuracy": multi_evaluator.setMetricName("accuracy").evaluate(predictions),
        "F1": multi_evaluator.setMetricName("f1").evaluate(predictions),
        "Precision": multi_evaluator.setMetricName("weightedPrecision").evaluate(predictions),
        "Recall": multi_evaluator.setMetricName("weightedRecall").evaluate(predictions)
    }

    return metrics

```

![The way the Pipeline is making the whole process to one line from assembling, scaling to evaluating, selecting best model and then saving it.](https://github.com/nakibworkspace/AS-Lab-04/raw/main/image/image2.svg)

The way the Pipeline is making the whole process to one line from assembling, scaling to evaluating, selecting best model and then saving it.

### Creating the pipeline, and evaluate the results

```python
results = []
for name, model in models.items():
    
    pipeline = Pipeline(stages=[assembler, scaler, model])

    
    print(f"Training {name}...")
    trained_model = pipeline.fit(train_data)
    predictions = trained_model.transform(test_data)

    
    metrics = evaluate_model(predictions, name)
    results.append(metrics)  
    trained_model.write().overwrite().save(f"./models/{name.lower().replace(' ', '_')}")
    
    
Training Logistic Regression...
Training Random Forest...
Training Gradient Boosted Trees...
Training Decision Tree...
```

### Comparing the models output using `pandas`

```python
import pandas as pd
comparison_df = pd.DataFrame(results)
print("\nModel Comparison:")
print(comparison_df.round(4))

Model Comparison:
                    Model     AUC  Accuracy      F1  Precision  Recall
0     Logistic Regression  0.9855    0.9686  0.9686     0.9688  0.9686
1           Random Forest  0.9922    0.9560  0.9563     0.9574  0.9560
2  Gradient Boosted Trees  0.9827    0.9434  0.9438     0.9450  0.9434
3           Decision Tree  0.9692    0.9434  0.9441     0.9469  0.9434
```

### Making a visual representation of the comparison using `Matplotlib`

```python
import matplotlib.pyplot as plt
def plot_model_comparison(df):
    metrics = ['AUC', 'Accuracy', 'F1', 'Precision', 'Recall']
    df_plot = df.set_index('Model')

    ax = df_plot[metrics].plot(kind='bar', figsize=(12, 6), width=0.8)
    plt.title('Model Performance Comparison')
    plt.xlabel('Models')
    plt.ylabel('Score')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.show()

plot_model_comparison(comparison_df)
```

![Output of the comparison to the models used to train and predict on the dataset.](https://github.com/nakibworkspace/AS-Lab-04/raw/main/image/image3.png)

Output of the comparison to the models used to train and predict on the dataset.

## Conclusion

In this lab we have successfully did the machine learning operations with Spark built-in library MLlib
