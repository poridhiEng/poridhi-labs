# Apache Spark for Data Partitioning



In this lab, we will get familiar with an important topic of Apache Spark. It is Data Partitioning.

# Table of Contents

1. Partitioning Data
    - Why use Partitioning?
2. Other types of Partitioning
    - Repartitioning
    - Coalesce

## Partitioning Data

Partitioning Data means the dividation of data stack into some chunks in order to improve query executions. In big data, we work with large datasets which can be bigger than we expect like 100 million to 100 billion of data. Now if we divide the dataset of 100 Billions in 10,000 partitions, every partitions will consist 10,000,000 data. Which will give an user ease to query better and faster.

### Why use Partitioning?

- To improve manageability and scalability.
- Reduce contention and optimise performance.
- To perform parallelism to allow the tasks perform independently.
- Easier query performance.

For example if we are not applying partitions in big datasets accordingly, whenever we perform any actions to it, for each query we’ll have to load, read, and apply our mapper and reducer to the entire dataset to get the result we’re looking for. This is not very efficient, since for most queries we only actually need a subset of the data. A much faster approach is to just load the data that you need.

In Spark, the main purpose of partitioning data is to achieve maximum parallelism, by having executors on cluster nodes execute many tasks at the same time. Spark executors are launched at the start of a Spark application in coordination with the Spark cluster manager. They are worker node processes responsible for running individual tasks in a given Spark job/application. Breaking up data into partitions allows executors to process those partitions in parallel and independently, with each executor assigned its own data partition to work on.

Partitions can be a group of rows or subset of DataFrame. Transformation on data partitions are known as task. Each task takes place on one spark core.

![The rows of the DataFrame are divided into four partitions and are dedicatedly working on different cores of the Executors. ](images/image1.svg)

The rows of the DataFrame are divided into four partitions and are dedicatedly working on different cores of the Executors. 

We are going to try out to make a DataFrame and use partitioning concepts in it. Firstly, creating a SparkSession.

```python
from pyspark.sql import SparkSession
spark= SparkSession.builder \
      .appName("Partitions") \
      .getOrCreate()
```

A sample DataFrame consisting car brands and count.

```python
data = [("toyota", 1), ("benz", 2), ("volkswagen", 3), ("mazda", 4), ("lucid", 5), ("nissan", 6)]
columns = ["car", "count"]
df = spark.createDataFrame(data, columns)
df.show()

+----------+-----+
|       car|count|
+----------+-----+
|    toyota|    1|
|      benz|    2|
|volkswagen|    3|
|     mazda|    4|
|     lucid|    5|
|    nissan|    6|
+----------+-----+
```

To check how many partitions are initially the DataFrame has.

```python
initial_partitions= df.rdd.getNumPartitions()
print(f"Initial number of partitions : {initial_partitions}")

Initial number of partitions : 2
```

As initially it has two partitions, checking the existing elements of each partitions.

```python
def inspect_partition(index, iterator):
	yield f"Partition {index} : {list(iterator)}"
	
partition_data_before= df.rdd.mapPartitionsWithIndex(inspect_partition).collect()
print("\n".join(partition_data_before))

output:

Partition 0 : [Row(car='toyota', count=1), Row(car='benz', count=2), Row(car='volkswagen', count=3)]
Partition 1 : [Row(car='mazda', count=4), Row(car='lucid', count=5), Row(car='nissan', count=6)]
```

<aside>
💡

**how do we figure out what should be the partition’s size?**

Partitions= Data Size (mb)/ 128 mb

</aside>

## Other types of Partitioning

### **Repartitioning**

Process of redistributing the data across different partitions in a Spark RDD or DataFrame. It comes handy when we are performing queries which needs joining in the datasets.

![The Original DataFrame was divided into 3 partitions and then repartitioned into 4 where the elements were shuffled randomly to fit into partitions.](images/image2.svg)

The Original DataFrame was divided into 3 partitions and then repartitioned into 4 where the elements were shuffled randomly to fit into partitions.

Repartitioning the DataFrame into four partitions which will shuffle the elements and divide them. 

```python
repartitioned_df= df.repartition(4)
new_partition= repartitioned_df.rdd.getNumPartitions()
print(f"Repartitioned to: {new_partition}")

output: 
Repartitioned to: 4
```

To check how the elements are repartitioned into four partitions.

```python
partitioned_data = repartitioned_df.rdd.glom().collect()
for idx, partition in enumerate(partitioned_data):
    print(f"Partition {idx}: {partition}")

output:
Data in partitions after repartition:
Partition 0: []
Partition 1: [Row(car='toyota', count=1), Row(car='mazda', count=4)]
Partition 2: [Row(car='volkswagen', count=3), Row(car='lucid', count=5)]
Partition 3: [Row(car='benz', count=2), Row(car='nissan', count=6)]
```

### **Coalesce**

basically reducing the partitions to smaller number. Useful when there is too many small partitions present.

![The main DataFrame was initially one partitioned which was then partitioned into 4 and by using coalesce, the partitions were reduced to two.](images/image3.svg)

The main DataFrame was initially one partitioned which was then partitioned into 4 and by using coalesce, the partitions were reduced to two.

Using the coalesce to reduce the partitions into three from four.

```python
coalesced_df = repartitioned_df.coalesce(3)
print(f"Number of partitions after coalesce: {coalesced_df.rdd.getNumPartitions()}")

output:
Number of partitions after coalesce: 3
```

Checking the elements of three partitions

```python
partitioned_data = coalesced_df.rdd.glom().collect()
for idx, partition in enumerate(partitioned_data):
print(f"Partition {idx}: {partition}")

output:
Partition 0: [Row(car='toyota', count=1), Row(car='mazda', count=4)]
Partition 1: [Row(car='benz', count=2), Row(car='nissan', count=6)]
Partition 2: [Row(car='volkswagen', count=3), Row(car='lucid', count=5)]
```
