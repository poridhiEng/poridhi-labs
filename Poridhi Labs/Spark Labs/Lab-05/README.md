# Feature Engineering with Spark



In this lab, we are performing various operations of Feature Engineering using PySpark, which will help us to have a proper understanding on how to handle Big Data.

# Table of Content

- Introduction to Feature Engineering.
- Adding new features
- Binarizing Data
- Data Imputation
- Tokenization
- Standardization
- Normalization.
- Vector Assembly
- Bucketing
- One-hot Encoding
- TF-IDF
- Feature Hashing
- SQL Transformation

## Introduction to Feature Engineering

Feature engineering is the process of transforming raw data into meaningful features that can be used by machine learning models to improve their predictive accuracy.

![featureeng.drawio.svg](https://github.com/nakibworkspace/AS-Lab-05/raw/main/images/image1.svg)

## Prerequisites:

1. Pyspark installation
    
    ```python
    sudo apt install pyspark
    ```
    
2. Java JDK installation
    
    ```python
    sudo apt install default-jdk
    ```
    

First create a spark session 

```python
from pyspark.sql import SparkSession
spark= SparkSession.builder \
      .appName("Feature Engineering") \
      .getOrCreate()
```

> In the whole process of feature engineering with PySpark, we will understand the following topics in a very simple format with sample datasets.
> 

## Adding new features

While working with raw data, we may need to add the features to make it more accesable and sometimes readable as well.

```python
records= [(100, 120000), (200, 170000), (300, 150000)]
columns= ["emp_id","salary"]
df= spark.createDataFrame(records, columns
df.show()

+------+------+
|emp_id|salary|
+------+------+
|   100|120000|
|   200|170000|
|   300|150000|
+------+------+
```

Now adding a column as feature for task using `withColumn()` function.

```python
df2= df.withColumn("bonus", df.salary * 0.05)
df2.show()

+------+------+------+
|emp_id|salary| bonus|
+------+------+------+
|   100|120000|6000.0|
|   200|170000|8500.0|
|   300|150000|7500.0|
+------+------+------+
```

If PySpark does not provide the function you need, you can define your own Python functions and register them as user-defined functions `UDFs`

```python
from pyspark.sql.functions import udf
@udf("integer")
def triplet(num):
  return 3*int(num)
  
df2= df.withColumn("triplet_col", triplet(df.salary))
df2.show()

+------+------+-----------+
|emp_id|salary|triplet_col|
+------+------+-----------+
|   100|120000|     360000|
|   200|170000|     510000|
|   300|150000|     450000|
+------+------+-----------+
```

## Creating pipeline

A pipeline is a series of steps for processing and modeling data, encapsulating all transformations and model training in a structured way. 

![pipeline.drawio.svg](https://github.com/nakibworkspace/AS-Lab-05/raw/main/images/image2.svg)

```python
df = spark.createDataFrame([
(1, 'CS', 'MS'),
(2, 'MATH', 'PHD'),
(3, 'MATH', 'MS'),
(4, 'CS', 'MS'),
(5, 'CS', 'PHD'),
(6, 'ECON', 'BS'),
(7, 'ECON', 'BS'),
], ['id', 'dept', 'education'])
df.show()

+---+----+---------+
| id|dept|education|
+---+----+---------+
|  1|  CS|       MS|
|  2|MATH|      PHD|
|  3|MATH|       MS|
|  4|  CS|       MS|
|  5|  CS|      PHD|
|  6|ECON|       BS|
|  7|ECON|       BS|
+---+----+---------+
```

```python
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoder

stage_1= StringIndexer(inputCol="dept", outputCol="dept_index")

stage_2= StringIndexer(inputCol= "education", outputCol="education_index")

stage_3= OneHotEncoder(inputCols= ["education_index",],

outputCols=["education_encoded"])

pipeline= Pipeline(stages=[stage_1, stage_2, stage_3])
pipeline_model= pipeline.fit(df)
final_df= pipeline_model.transform(df)
final_df.show(truncate=False)

+---+----+---------+----------+---------------+-----------------+
|id |dept|education|dept_index|education_index|education_encoded|
+---+----+---------+----------+---------------+-----------------+
|1  |CS  |MS       |0.0       |0.0            |(2,[0],[1.0])    |
|2  |MATH|PHD      |2.0       |2.0            |(2,[],[])        |
|3  |MATH|MS       |2.0       |0.0            |(2,[0],[1.0])    |
|4  |CS  |MS       |0.0       |0.0            |(2,[0],[1.0])    |
|5  |CS  |PHD      |0.0       |2.0            |(2,[],[])        |
|6  |ECON|BS       |1.0       |1.0            |(2,[1],[1.0])    |
|7  |ECON|BS       |1.0       |1.0            |(2,[1],[1.0])    |
+---+----+---------+----------+---------------+-----------------+
```

## Binarizing data

Binarizing data is **the process of converting numerical or categorical data into binary values, usually 0s and 1s to simplify complex datasets.**

```python
from pyspark.ml.feature import Binarizer
raw_df = spark.createDataFrame([
(1, 0.1),
(2, 0.2),
(3, 0.5),
(4, 0.8),
(5, 0.9),
(6, 1.1)
], ["id", "feature"])
```

Here the `Binarizer` used the features as input and send outputs as binarized_feature where threshold is set to 0.5.

```python
binarizer= Binarizer(threshold=0.5, inputCol="feature", outputCol="binarized_feature")
binarized_df= binarizer.transform(raw_df)
binarized_df.show(truncate=False)

+---+-------+-----------------+
|id |feature|binarized_feature|
+---+-------+-----------------+
|1  |0.1    |0.0              |
|2  |0.2    |0.0              |
|3  |0.5    |0.0              |
|4  |0.8    |1.0              |
|5  |0.9    |1.0              |
|6  |1.1    |1.0              |
+---+-------+-----------------+
```

## Data imputation

Data imputation involves filling in missing values in the dataset. It follows various methods to fill the values such as median, mean and mode.

```xml
Missing Data → Imputation Strategy
NaN       |   Median   → Replace with median
NaN       |   Mean     → Replace with mean
NaN       |   Most Frequent → Replace with mode
```

```python
df = spark.createDataFrame([
(1, 12.0, 5.0),
(2, 7.0, 10.0),
(3, 10.0, 12.0),
(4, 5.0, float("nan")),
(5, 6.0, None),
(6, float("nan"), float("nan")),
(7, None, None)
], ["id", "col1", "col2"])
df.show(truncate=False)

+---+----+----+
|id |col1|col2|
+---+----+----+
|1  |12.0|5.0 |
|2  |7.0 |10.0|
|3  |10.0|12.0|
|4  |5.0 |NaN |
|5  |6.0 |NULL|
|6  |NaN |NaN |
|7  |NULL|NULL|
+---+----+----+
```

We can perform operations on multiple columns using `Imputer`

```python
from pyspark.ml.feature import Imputer
imputer= Imputer(inputCols=["col1","col2"], outputCols=["col1_out","col2_out"])
model= imputer.fit(df)
transformed= model.transform(df)
transformed.show(truncate=False)

+---+----+----+--------+--------+
|id |col1|col2|col1_out|col2_out|
+---+----+----+--------+--------+
|1  |12.0|5.0 |12.0    |5.0     |
|2  |7.0 |10.0|7.0     |10.0    |
|3  |10.0|12.0|10.0    |12.0    |
|4  |5.0 |NaN |5.0     |9.0     |
|5  |6.0 |NULL|6.0     |9.0     |
|6  |NaN |NaN |8.0     |9.0     |
|7  |NULL|NULL|8.0     |9.0     |
+---+----+----+--------+--------+
```

Another way of filling the values is called `setStrategy()` where the process (here median) can be declared.

```python
imputer.setStrategy("median")
model= imputer.fit(df)
transformed= model.transform(df)
transformed.show(truncate=False)

+---+----+----+--------+--------+
|id |col1|col2|col1_out|col2_out|
+---+----+----+--------+--------+
|1  |12.0|5.0 |12.0    |5.0     |
|2  |7.0 |10.0|7.0     |10.0    |
|3  |10.0|12.0|10.0    |12.0    |
|4  |5.0 |NaN |5.0     |10.0    |
|5  |6.0 |NULL|6.0     |10.0    |
|6  |NaN |NaN |7.0     |10.0    |
|7  |NULL|NULL|7.0     |10.0    |
+---+----+----+--------+--------+
```

## Tokenization

Tokenization splits text into individual words or tokens. The `Tokenizer` or `RegexTokenizer` classes from `pyspark.ml.feature` handle tokenization.

![tokenization.drawio.svg](https://github.com/nakibworkspace/AS-Lab-05/raw/main/images/image3.svg)

```python
data = [(1, "a Fox jumped over FOX"),
(2, "RED of fox jumped")]
df= spark.createDataFrame(data, ["id","text"])
df.show()

+---+--------------------+
| id|                text|
+---+--------------------+
|  1|a Fox jumped over...|
|  2|   RED of fox jumped|
+---+--------------------+
```

The `Tokenizer` will split the text by white spaces and `withColumn()` will help to count the length.

```python
from pyspark.ml.feature import Tokenizer
from pyspark.sql.functions import col, size

tokenizer= Tokenizer(inputCol="text", outputCol="tokens")
tokenized= tokenizer.transform(df)
tokenized.select("text","tokens").withColumn("tokens_length", size(col("tokens"))).show(truncate=False)

+---------------------+---------------------------+-------------+
|text                 |tokens                     |tokens_length|
+---------------------+---------------------------+-------------+
|a Fox jumped over FOX|[a, fox, jumped, over, fox]|5            |
|RED of fox jumped    |[red, of, fox, jumped]     |4            |
+---------------------+---------------------------+-------------+
```

Another way of splitting the text is `RegexTokenizer` where we can declare how we want the text to be splitted.

```python
from pyspark.ml.feature import RegexTokenizer
from pyspark.sql.types import IntegerType

regextokenizer= RegexTokenizer(inputCol="text", outputCol="tokens",pattern="\\W", minTokenLength=3)
regex_tokenized= regextokenizer.transform(df)
regex_tokenized.select("text","tokens").withColumn("tokens_length", size(col("tokens"))).show(truncate=False)

+---------------------+------------------------+-------------+
|text                 |tokens                  |tokens_length|
+---------------------+------------------------+-------------+
|a Fox jumped over FOX|[fox, jumped, over, fox]|4            |
|RED of fox jumped    |[red, fox, jumped]      |3            |
+---------------------+------------------------+-------------+
```

Here is an example of performing the splitting operation using Pipeline, where it will be divided into 3 stages.

```python
docs = [(1, "a Fox jumped, over, the fence?"),
(2, "a RED, of fox?")]
df= spark.createDataFrame(docs, ["id","text"])
df.show(truncate=False)

+---+------------------------------+
|id |text                          |
+---+------------------------------+
|1  |a Fox jumped, over, the fence?|
|2  |a RED, of fox?                |
+---+------------------------------+
```

Here in the `RegexTokenizer` the pattern is declared to split the text by white spaces and punctuations as well.

```python
from pyspark.ml.feature import StopWordsRemover
rgx= RegexTokenizer(inputCol="text", outputCol="text2", pattern=r"(?:\p{Punct}|\s)+")

sw= StopWordsRemover(inputCol='text2', outputCol='text3')
pipeline = Pipeline(stages=[rgx, sw])
df4= pipeline.fit(df).transform(df)
df4.show(truncate=False)

+---+------------------------------+----------------------------------+--------------------+
|id |text                          |text2                             |text3               |
+---+------------------------------+----------------------------------+--------------------+
|1  |a Fox jumped, over, the fence?|[a, fox, jumped, over, the, fence]|[fox, jumped, fence]|
|2  |a RED, of fox?                |[a, red, of, fox]                 |[red, fox]          |
+---+------------------------------+----------------------------------+--------------------+
```

## Standardization

Standardization transforms the data to have a mean of 0 and a standard deviation of 1. 

```python
features = [('alex', 1), ('bob', 3), ('ali', 6), ('dave', 10)]
columns = ("name", "age")
df= spark.createDataFrame(features, columns)
df.show(truncate=False)

+----+---+
|name|age|
+----+---+
|alex|1  |
|bob |3  |
|ali |6  |
|dave|10 |
+----+---+
```

You can build the standardrization from scratch.

```python
from pyspark.sql.functions import stddev, mean, col
df.select(mean("age").alias("mean_age"), stddev("age").alias("std_age")).crossJoin(df).withColumn(
    "age_scaled", (col("age")- col("mean_age")) / col("std_age")
).show(truncate=False)

+--------+------------------+----+---+-------------------+
|mean_age|std_age           |name|age|age_scaled         |
+--------+------------------+----+---+-------------------+
|5.0     |3.9157800414902435|alex|1  |-1.0215078369104984|
|5.0     |3.9157800414902435|bob |3  |-0.5107539184552492|
|5.0     |3.9157800414902435|ali |6  |0.2553769592276246 |
|5.0     |3.9157800414902435|dave|10 |1.276884796138123  |
+--------+------------------+----+---+-------------------+
```

Or, The `StandardScaler` class in `pyspark.ml.feature` is used for standardization.

```python
from pyspark.ml.feature import VectorAssembler, StandardScaler

vector= VectorAssembler(inputCols=['age'], outputCol='age_vec')
df2= vector.transform(df)
df2.show()

+----+---+-------+
|name|age|age_vec|
+----+---+-------+
|alex|  1|  [1.0]|
| bob|  3|  [3.0]|
| ali|  6|  [6.0]|
|dave| 10| [10.0]|
+----+---+-------+

standard= StandardScaler(inputCol='age_vec', outputCol='age_scaled', withStd=True, withMean=True)
scalermodel= standard.fit(df2)
scaledData= scalermodel.transform(df2)
scaledData.show(truncate=False)

+----+---+-------+---------------------+
|name|age|age_vec|age_scaled           |
+----+---+-------+---------------------+
|alex|1  |[1.0]  |[-1.0215078369104984]|
|bob |3  |[3.0]  |[-0.5107539184552492]|
|ali |6  |[6.0]  |[0.2553769592276246] |
|dave|10 |[10.0] |[1.276884796138123]  |
+----+---+-------+---------------------+
```

## Normalization

Normalization rescales the data so that each data point has a norm (e.g., L1 or L2 norm) of 1.

```python
df = spark.createDataFrame([ (100, 77560, 45),
(200, 41560, 23),
(300, 30285, 20),
(400, 10345, 6),
(500, 88000, 50)
], ["user_id", "revenue","num_of_days"])
df.show()

+-------+-------+-----------+
|user_id|revenue|num_of_days|
+-------+-------+-----------+
|    100|  77560|         45|
|    200|  41560|         23|
|    300|  30285|         20|
|    400|  10345|          6|
|    500|  88000|         50|
+-------+-------+-----------+
```

```python
from pyspark.ml.feature import VectorAssembler, MinMaxScaler

vector_assembler = VectorAssembler(inputCols=["revenue", "num_of_days"], outputCol="features")
df_vector = vector_assembler.transform(df)

scaler = MinMaxScaler(inputCol="features", outputCol="scaled_features")
scaler_model = scaler.fit(df_vector)
df_scaled = scaler_model.transform(df_vector)

df_scaled.select("user_id", "scaled_features").show(truncate=False)

+-------+-----------------------------------------+
|user_id|scaled_features                          |
+-------+-----------------------------------------+
|100    |[0.8655592041723005,0.8863636363636364]  |
|200    |[0.40197025304230244,0.38636363636363635]|
|300    |[0.25677676904256,0.3181818181818182]    |
|400    |(2,[],[])                                |
|500    |[0.9999999999999999,1.0]                 |
+-------+-----------------------------------------+
```

## Vector assembly

Combines multiple feature columns into a single vector column, often required for machine learning models in Spark. The `VectorAssembler` class is used for this purpose.

![A pictorial representation of Vector Assembly where the numeric value is converted to vectors](https://github.com/nakibworkspace/AS-Lab-05/raw/main/images/image4.svg)

A pictorial representation of Vector Assembly where the numeric value is converted to vectors

```python
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
triplets = [(0, 1, 100), (1, 2, 200), (2, 5, 1000)]
df = spark.createDataFrame(triplets, ['x', 'y', 'z'])
df.show()

+---+---+----+
|  x|  y|   z|
+---+---+----+
|  0|  1| 100|
|  1|  2| 200|
|  2|  5|1000|
+---+---+----+
```

```python
assembler = VectorAssembler(inputCols=["x"], outputCol="x_vector")
scaler = MinMaxScaler(inputCol="x_vector", outputCol="x_scaled")
pipeline = Pipeline(stages=[assembler, scaler])
scalerModel = pipeline.fit(df)
scaledData = scalerModel.transform(df)
scaledData.show(truncate=False)

+---+---+----+--------+--------+
|x  |y  |z   |x_vector|x_scaled|
+---+---+----+--------+--------+
|0  |1  |100 |[0.0]   |[0.0]   |
|1  |2  |200 |[1.0]   |[0.5]   |
|2  |5  |1000|[2.0]   |[1.0]   |
+---+---+----+--------+--------+
```

## Bucketing

Divides continuous values into discrete buckets or bins. Spark provides the `Bucketizer` class for bucketing. 

![The initial tasks are bucketed and in the buckets after the shuffling operation, the final output is showed.](https://github.com/nakibworkspace/AS-Lab-05/raw/main/images/image5.svg)

The initial tasks are bucketed and in the buckets after the shuffling operation, the final output is showed.

```python
data = [('A', -99.99), ('B', -0.5), ('C', -0.3),
('D', 0.0), ('E', 0.7), ('F', 99.99)]

df= spark.createDataFrame(data, ['id','features'])
df.show()

+---+--------+
| id|features|
+---+--------+
|  A|  -99.99|
|  B|    -0.5|
|  C|    -0.3|
|  D|     0.0|
|  E|     0.7|
|  F|   99.99|
+---+--------+
```

```python
bucket_border= [-float("inf"), -0.5, 0.0, 0.5, float("inf")]
from pyspark.ml.feature import Bucketizer

bucketer= Bucketizer().setSplits(bucket_border).setInputCol("features").setOutputCol("buckets")
bucketer.transform(df).show()

+---+--------+-------+
| id|features|buckets|
+---+--------+-------+
|  A|  -99.99|    0.0|
|  B|    -0.5|    1.0|
|  C|    -0.3|    1.0|
|  D|     0.0|    2.0|
|  E|     0.7|    3.0|
|  F|   99.99|    3.0|
+---+--------+-------+
```

## One-hot encoding

Converts categorical values into a binary vector, with a single 1 indicating the presence of a category.

```python
from pyspark.sql.types import *
schema = StructType().add("id","integer").add("safety_level","string").add("engine_type","string")

data = [
        (1,'Very-Low','v4'),
       (2,'Very-Low','v6'),
        (3,'Low','v6'),
        (4,'Low','v6'),
        (5,'Medium','v4'),
        (6,'High','v6'),
        (7,'High','v6'),
        (8,'Very-High','v4'),
        (9,'Very-High','v6')
 ]
 
 df= spark.createDataFrame(data, schema=schema)
df.show()

+---+------------+-----------+
| id|safety_level|engine_type|
+---+------------+-----------+
|  1|    Very-Low|         v4|
|  2|    Very-Low|         v6|
|  3|         Low|         v6|
|  4|         Low|         v6|
|  5|      Medium|         v4|
|  6|        High|         v6|
|  7|        High|         v6|
|  8|   Very-High|         v4|
|  9|   Very-High|         v6|
+---+------------+-----------+
```

```python
from pyspark.ml.feature import StringIndexer
safety_level_indexer= StringIndexer(inputCol='safety_level', outputCol='safety_level_index')
df1= safety_level_indexer.fit(df).transform(df)
df1.show()

+---+------------+-----------+------------------+
| id|safety_level|engine_type|safety_level_index|
+---+------------+-----------+------------------+
|  1|    Very-Low|         v4|               3.0|
|  2|    Very-Low|         v6|               3.0|
|  3|         Low|         v6|               1.0|
|  4|         Low|         v6|               1.0|
|  5|      Medium|         v4|               4.0|
|  6|        High|         v6|               0.0|
|  7|        High|         v6|               0.0|
|  8|   Very-High|         v4|               2.0|
|  9|   Very-High|         v6|               2.0|
+---+------------+-----------+------------------+
```

```python
engine_type_indexer= StringIndexer(inputCol='engine_type', outputCol='engine_type_index')
df2= engine_type_indexer.fit(df).transform(df)
df2.show(truncate=False)

+---+------------+-----------+-----------------+
|id |safety_level|engine_type|engine_type_index|
+---+------------+-----------+-----------------+
|1  |Very-Low    |v4         |1.0              |
|2  |Very-Low    |v6         |0.0              |
|3  |Low         |v6         |0.0              |
|4  |Low         |v6         |0.0              |
|5  |Medium      |v4         |1.0              |
|6  |High        |v6         |0.0              |
|7  |High        |v6         |0.0              |
|8  |Very-High   |v4         |1.0              |
|9  |Very-High   |v6         |0.0              |
+---+------------+-----------+-----------------+
```

```python
from pyspark.ml.feature import OneHotEncoder
ohr_level_encoder= OneHotEncoder(inputCol='safety_level_index', outputCol='safety_level_vector')
df11= ohr_level_encoder.fit(df1).transform(df1)
df11.show(truncate=False)

+---+------------+-----------+------------------+-------------------+
|id |safety_level|engine_type|safety_level_index|safety_level_vector|
+---+------------+-----------+------------------+-------------------+
|1  |Very-Low    |v4         |3.0               |(4,[3],[1.0])      |
|2  |Very-Low    |v6         |3.0               |(4,[3],[1.0])      |
|3  |Low         |v6         |1.0               |(4,[1],[1.0])      |
|4  |Low         |v6         |1.0               |(4,[1],[1.0])      |
|5  |Medium      |v4         |4.0               |(4,[],[])          |
|6  |High        |v6         |0.0               |(4,[0],[1.0])      |
|7  |High        |v6         |0.0               |(4,[0],[1.0])      |
|8  |Very-High   |v4         |2.0               |(4,[2],[1.0])      |
|9  |Very-High   |v6         |2.0               |(4,[2],[1.0])      |
+---+------------+-----------+------------------+-------------------+
```

```python
ohe_engine_type= OneHotEncoder(inputCol='engine_type_index',outputCol='engine_type_vector')
df12= ohe_engine_type.fit(df2).transform(df2)
df12.show(truncate=False)

+---+------------+-----------+-----------------+------------------+
|id |safety_level|engine_type|engine_type_index|engine_type_vector|
+---+------------+-----------+-----------------+------------------+
|1  |Very-Low    |v4         |1.0              |(1,[],[])         |
|2  |Very-Low    |v6         |0.0              |(1,[0],[1.0])     |
|3  |Low         |v6         |0.0              |(1,[0],[1.0])     |
|4  |Low         |v6         |0.0              |(1,[0],[1.0])     |
|5  |Medium      |v4         |1.0              |(1,[],[])         |
|6  |High        |v6         |0.0              |(1,[0],[1.0])     |
|7  |High        |v6         |0.0              |(1,[0],[1.0])     |
|8  |Very-High   |v4         |1.0              |(1,[],[])         |
|9  |Very-High   |v6         |0.0              |(1,[0],[1.0])     |
+---+------------+-----------+-----------------+------------------+
```

Applying the `OneHotEncoder` to multiple indexes.

```python
indexers = [StringIndexer(inputCol=column, outputCol=column+"_index").fit(df) for column in list(set(df.columns)-set(['id'])) ]

from pyspark.ml import Pipeline
pipeline= Pipeline(stages= indexers)
df_indexed= pipeline.fit(df).transform(df)
df_indexed.show()

+---+------------+-----------+-----------------+------------------+
| id|safety_level|engine_type|engine_type_index|safety_level_index|
+---+------------+-----------+-----------------+------------------+
|  1|    Very-Low|         v4|              1.0|               3.0|
|  2|    Very-Low|         v6|              0.0|               3.0|
|  3|         Low|         v6|              0.0|               1.0|
|  4|         Low|         v6|              0.0|               1.0|
|  5|      Medium|         v4|              1.0|               4.0|
|  6|        High|         v6|              0.0|               0.0|
|  7|        High|         v6|              0.0|               0.0|
|  8|   Very-High|         v4|              1.0|               2.0|
|  9|   Very-High|         v6|              0.0|               2.0|
+---+------------+-----------+-----------------+------------------+
```

```python
encoder= OneHotEncoder(inputCols=[indexer.getOutputCol() for indexer in indexers],
outputCols=["{0}_encoded".format(indexer.getOutputCol()) for indexer in indexers])

from pyspark.ml.feature import VectorAssembler
assembler= VectorAssembler(inputCols= encoder.getOutputCols(),outputCol="features")

pipeline= Pipeline(stages= indexers + [encoder, assembler])
pipeline.fit(df).transform(df).show()

+---+------------+-----------+-----------------+------------------+-------------------------+--------------------------+-------------------+
| id|safety_level|engine_type|engine_type_index|safety_level_index|engine_type_index_encoded|safety_level_index_encoded|           features|
+---+------------+-----------+-----------------+------------------+-------------------------+--------------------------+-------------------+
|  1|    Very-Low|         v4|              1.0|               3.0|                (1,[],[])|             (4,[3],[1.0])|      (5,[4],[1.0])|
|  2|    Very-Low|         v6|              0.0|               3.0|            (1,[0],[1.0])|             (4,[3],[1.0])|(5,[0,4],[1.0,1.0])|
|  3|         Low|         v6|              0.0|               1.0|            (1,[0],[1.0])|             (4,[1],[1.0])|(5,[0,2],[1.0,1.0])|
|  4|         Low|         v6|              0.0|               1.0|            (1,[0],[1.0])|             (4,[1],[1.0])|(5,[0,2],[1.0,1.0])|
|  5|      Medium|         v4|              1.0|               4.0|                (1,[],[])|                 (4,[],[])|          (5,[],[])|
|  6|        High|         v6|              0.0|               0.0|            (1,[0],[1.0])|             (4,[0],[1.0])|(5,[0,1],[1.0,1.0])|
|  7|        High|         v6|              0.0|               0.0|            (1,[0],[1.0])|             (4,[0],[1.0])|(5,[0,1],[1.0,1.0])|
|  8|   Very-High|         v4|              1.0|               2.0|                (1,[],[])|             (4,[2],[1.0])|      (5,[3],[1.0])|
|  9|   Very-High|         v6|              0.0|               2.0|            (1,[0],[1.0])|             (4,[2],[1.0])|(5,[0,3],[1.0,1.0])|
+---+------------+-----------+-----------------+------------------+-------------------------+--------------------------+-------------------+
```

```python
safety_level_indexer = StringIndexer(inputCol="safety_level",
outputCol="safety_level_index")
engine_type_indexer = StringIndexer(inputCol="engine_type", outputCol="engine_type_index")
onehotencoder_safety_level = OneHotEncoder(inputCol="safety_level_index",outputCol="safety_level_vector")
onehotencoder_engine_type = OneHotEncoder(
inputCol="engine_type_index",
outputCol="engine_type_vector")

pipeline = Pipeline(stages=[safety_level_indexer,
                             engine_type_indexer,
                             onehotencoder_safety_level,
                             onehotencoder_engine_type
                     ])

df_transformed = pipeline.fit(df).transform(df)
df_transformed.show(truncate=False)

+---+------------+-----------+------------------+-----------------+-------------------+------------------+
|id |safety_level|engine_type|safety_level_index|engine_type_index|safety_level_vector|engine_type_vector|
+---+------------+-----------+------------------+-----------------+-------------------+------------------+
|1  |Very-Low    |v4         |3.0               |1.0              |(4,[3],[1.0])      |(1,[],[])         |
|2  |Very-Low    |v6         |3.0               |0.0              |(4,[3],[1.0])      |(1,[0],[1.0])     |
|3  |Low         |v6         |1.0               |0.0              |(4,[1],[1.0])      |(1,[0],[1.0])     |
|4  |Low         |v6         |1.0               |0.0              |(4,[1],[1.0])      |(1,[0],[1.0])     |
|5  |Medium      |v4         |4.0               |1.0              |(4,[],[])          |(1,[],[])         |
|6  |High        |v6         |0.0               |0.0              |(4,[0],[1.0])      |(1,[0],[1.0])     |
|7  |High        |v6         |0.0               |0.0              |(4,[0],[1.0])      |(1,[0],[1.0])     |
|8  |Very-High   |v4         |2.0               |1.0              |(4,[2],[1.0])      |(1,[],[])         |
|9  |Very-High   |v6         |2.0               |0.0              |(4,[2],[1.0])      |(1,[0],[1.0])     |
+---+------------+-----------+------------------+-----------------+-------------------+------------------+
```

## TF-IDF

A statistical measure used to evaluate the importance of a word in a document relative to a collection of documents (corpus). Spark implements TF-IDF using `HashingTF` and `IDF` classes.

```python
sentences = spark.createDataFrame([
(0.0, "My name is Hasan"),
(0.0, "I am wokring with MLOps"),
(1.0, "cat has beautiful eyes"),
(1.0, "black cat jumped over")
], ["label", "text"])

sentences.show(truncate=False)

+-----+-----------------------+
|label|text                   |
+-----+-----------------------+
|0.0  |My name is Hasan       |
|0.0  |I am working with MLOps|
|1.0  |cat has beautiful eyes |
|1.0  |black cat jumped over  |
+-----+-----------------------+
```

![The text values are splitted using `Tokenizer` and then raw_features are generated using `HashingTF`. Finally, the texts are converted using `IDF`](https://github.com/nakibworkspace/AS-Lab-05/raw/main/images/image6.svg)

The text values are splitted using `Tokenizer` and then raw_features are generated using `HashingTF`. Finally, the texts are converted using `IDF`

```python
tokenizer= Tokenizer(inputCol='text', outputCol='words')
words_data= tokenizer.transform(sentences)
words_data.show(truncate=False)

+-----+-----------------------+-----------------------------+
|label|text                   |words                        |
+-----+-----------------------+-----------------------------+
|0.0  |My name is Hasan       |[my, name, is, hasan]        |
|0.0  |I am working with MLOps|[i, am, working, with, mlops]|
|1.0  |cat has beautiful eyes |[cat, has, beautiful, eyes]  |
|1.0  |black cat jumped over  |[black, cat, jumped, over]   |
+-----+-----------------------+-----------------------------+
```

```python
hashingtf= HashingTF(inputCol='words', outputCol= 'raw_features')
featurized_data= hashingtf.transform(words_data)
featurized_data.select('text','raw_features').show(truncate=False)

+-----------------------+-----------------------------------------------------------------+
|text                   |raw_features                                                     |
+-----------------------+-----------------------------------------------------------------+
|My name is Hasan       |(262144,[35119,106841,159001,240944],[1.0,1.0,1.0,1.0])          |
|I am working with MLOps|(262144,[19036,35290,114321,126466,186845],[1.0,1.0,1.0,1.0,1.0])|
|cat has beautiful eyes |(262144,[8449,132786,141363,259145],[1.0,1.0,1.0,1.0])           |
|black cat jumped over  |(262144,[1398,141363,154828,179832],[1.0,1.0,1.0,1.0])           |
+-----------------------+-----------------------------------------------------------------+
```

```python
idf= IDF(inputCol='raw_features', outputCol='features')
idf_model= idf.fit(featurized_data)
rescaled_data= idf_model.transform(featurized_data)
rescaled_data.select('raw_features','features').show(truncate=False)

+-----------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+
|raw_features                                                     |features                                                                                                                                    |
+-----------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+
|(262144,[35119,106841,159001,240944],[1.0,1.0,1.0,1.0])          |(262144,[35119,106841,159001,240944],[0.9162907318741551,0.9162907318741551,0.9162907318741551,0.9162907318741551])                         |
|(262144,[19036,35290,114321,126466,186845],[1.0,1.0,1.0,1.0,1.0])|(262144,[19036,35290,114321,126466,186845],[0.9162907318741551,0.9162907318741551,0.9162907318741551,0.9162907318741551,0.9162907318741551])|
|(262144,[8449,132786,141363,259145],[1.0,1.0,1.0,1.0])           |(262144,[8449,132786,141363,259145],[0.9162907318741551,0.9162907318741551,0.5108256237659907,0.9162907318741551])                          |
|(262144,[1398,141363,154828,179832],[1.0,1.0,1.0,1.0])           |(262144,[1398,141363,154828,179832],[0.9162907318741551,0.5108256237659907,0.9162907318741551,0.9162907318741551])                          |
+-----------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------+

```

## Feature hashing

A method to map features to a fixed-size vector using a hash function, reducing dimensionality. Spark uses the `HashingTF` class for feature hashing, particularly useful for text data. Instead of creating a sparse matrix for all terms, it hashes terms into a fixed number of buckets.

```python
from pyspark.ml.feature import FeatureHasher
df = spark.createDataFrame([
     (2.1, True, "1", "fox"),
     (2.1, False, "2", "gray"),
     (3.3, False, "2", "red"),
    (4.4, True, "4", "fox") ], ["number", "boolean", "string_number", "string"])
    
input_cols= ['number','boolean','string_number','string']

hasher= FeatureHasher(inputCols= input_cols, outputCol= 'features')
hasher.setNumFeatures(10)
featurized= hasher.transform(df)
featurized.show()

+------+-------+-------------+------+--------------------+
|number|boolean|string_number|string|            features|
+------+-------+-------------+------+--------------------+
|   2.1|   true|            1|   fox|(10,[2,6,9],[2.0,...|
|   2.1|  false|            2|  gray|(10,[2,3,9],[1.0,...|
|   3.3|  false|            2|   red|(10,[2,7,9],[1.0,...|
|   4.4|   true|            4|   fox|(10,[2,4,6,9],[1....|
+------+-------+-------------+------+--------------------+
```

## Applying SQL transformations

SQL transformation refers to applying SQL queries directly on Spark DataFrames using the Spark SQL engine. Spark SQL allows you to query structured data in a familiar SQL syntax, enabling complex transformations, aggregations, and filtering operations.

```python
from pyspark.ml.feature import SQLTransformer
df = spark.createDataFrame([
       (10, "d1", 27000),
        (20, "d1", 29000),
       (40, "d2", 31000),
        (50, "d2", 39000)], ["id", "dept", "salary"])

df.show()

+---+----+------+
| id|dept|salary|
+---+----+------+
| 10|  d1| 27000|
| 20|  d1| 29000|
| 40|  d2| 31000|
| 50|  d2| 39000|
+---+----+------+
```

we can perform queries using `SQLTransformer`

```python
query = "SELECT dept, SUM(salary) AS sum_of_salary FROM **THIS** GROUP BY dept"
sqlTrans = SQLTransformer(statement=query)
sqlTrans.transform(df).show()

+----+-------------+
|dept|sum_of_salary|
+----+-------------+
|  d1|        56000|
|  d2|        70000|
+----+-------------+
```
