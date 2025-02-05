# Structured Streaming with Apache Spark

## What is Spark Structured Streaming?
Spark Streaming is a scalable, high-throughput, fault-tolerant stream processing system that works with both batch and real time streaming data processing. And Structured Streaming is built on Spark SQL engine.

![streaming.drawio.svg](https://prod-files-secure.s3.us-west-2.amazonaws.com/0273592f-f54f-43f5-b46d-a5042292b3fe/191c59d3-bdf9-4457-9f3a-731b51550e2c/streaming.drawio.svg)

Key components of Spark Stream and how it works?

![howsssworks.drawio.svg](https://prod-files-secure.s3.us-west-2.amazonaws.com/0273592f-f54f-43f5-b46d-a5042292b3fe/4e18c9f2-8741-4bc1-a0da-c3ad6b197e59/howsssworks.drawio.svg)

code

Converting batch code to stream

```from pyspark.sql import SparkSession

spark= SparkSession.builder \
.master("local[*]") \
.appName("spark streaming") \
.getOrCreate()
```


![Screenshot 2025-01-24 at 02.13.15.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/0273592f-f54f-43f5-b46d-a5042292b3fe/70b51184-d4de-4d12-9c16-9cb2ae9ab9a0/Screenshot_2025-01-24_at_02.13.15.png)



```python
#read the file
df_raw= spark.read.format("text").load("data/input/example.txt")
```

```python
df_raw.printSchema()

root
 |-- value: string (nullable = true)
```

```python
df_raw.show()

+--------------------+
|               value|
+--------------------+
|hi my name is raj...|
+--------------------+
```

```python
#split the line into words
from pyspark.sql.functions import split
df_words= df_raw.withColumn("words", split("value", " "))

df_words.show()

+--------------------+--------------------+
|               value|               words|
+--------------------+--------------------+
|hi my name is raj...|[hi, my, name, is...|
+--------------------+--------------------+
```

```python
#explode the list of words
from pyspark.sql.functions import explode
df_explode= df_words.withColumn("word", explode("words"))

df_explode.show()

+--------------------+--------------------+----+
|               value|               words|word|
+--------------------+--------------------+----+
|hi my name is raj...|[hi, my, name, is...|  hi|
|hi my name is raj...|[hi, my, name, is...|  my|
|hi my name is raj...|[hi, my, name, is...|name|
|hi my name is raj...|[hi, my, name, is...|  is|
|hi my name is raj...|[hi, my, name, is...| raj|
|hi my name is raj...|[hi, my, name, is...|   i|
|hi my name is raj...|[hi, my, name, is...|love|
|hi my name is raj...|[hi, my, name, is...| cat|
|hi my name is raj...|[hi, my, name, is...| and|
|hi my name is raj...|[hi, my, name, is...| dog|
|hi my name is raj...|[hi, my, name, is...| cat|
|hi my name is raj...|[hi, my, name, is...| and|
|hi my name is raj...|[hi, my, name, is...| dog|
|hi my name is raj...|[hi, my, name, is...|love|
|hi my name is raj...|[hi, my, name, is...|  me|
+--------------------+--------------------+----+
```

```python
df_explode_final= df_words.withColumn("word", explode("words")).drop("value", "words")
df_explode_final.show()

+----+
|word|
+----+
|  hi|
|  my|
|name|
|  is|
| raj|
|   i|
|love|
| cat|
| and|
| dog|
| cat|
| and|
| dog|
|love|
|  me|
+----+
```

```python
#aggregate the words to generate the count
from pyspark.sql.functions import count, lit
df_agg= df_explode_final.groupBy("word").agg(count(lit(1)).alias("cnt"))

df_agg.show()

+----+---+
|word|cnt|
+----+---+
|name|  1|
| dog|  2|
|love|  2|
| cat|  2|
|  me|  1|
|  is|  1|
| raj|  1|
|  my|  1|
|   i|  1|
| and|  2|
|  hi|  1|
+----+---+
```

streaming

```python
#read the file
df_raw= spark.readStream.format("socket").option("host","localhost").option("port","9999").load()

df_raw.printSchema()

root
 |-- value: string (nullable = true)
```

```python
#write the output to console streaming
#console is the terminal in which the output will be displayed
#awaitTermination will make sure when the server is ideal it is still connected
df_agg.writeStream.format("console").outputMode("complete").start().awaitTermination()
```

```python
ncat -l 9999
hello world
hello this is raj
```

![Screenshot 2025-01-24 at 02.35.23.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/0273592f-f54f-43f5-b46d-a5042292b3fe/bad6380e-a803-4eb0-b5c0-e3fbcba5e03a/Screenshot_2025-01-24_at_02.35.23.png)

---

```2025-01-24 02:29:59 Batch: 0
2025-01-24 02:29:59 -------------------------------------------
2025-01-24 02:29:59 +----+---+
2025-01-24 02:29:59 |word|cnt|
2025-01-24 02:29:59 +----+---+
2025-01-24 02:29:59 +----+---+
2025-01-24 02:29:59
2025-01-24 02:30:32 -------------------------------------------
2025-01-24 02:30:32 Batch: 1
2025-01-24 02:30:32 -------------------------------------------
2025-01-24 02:30:32 +-----+---+
2025-01-24 02:30:32 | word|cnt|
2025-01-24 02:30:32 +-----+---+
2025-01-24 02:30:32 |hello|  1|
2025-01-24 02:30:32 |world|  1|
2025-01-24 02:30:32 +-----+---+
2025-01-24 02:30:32
2025-01-24 02:30:44 -------------------------------------------
2025-01-24 02:30:44 Batch: 2
2025-01-24 02:30:44 -------------------------------------------
2025-01-24 02:30:44 +-----+---+
2025-01-24 02:30:44 | word|cnt|
2025-01-24 02:30:44 +-----+---+
2025-01-24 02:30:44 |hello|  2|
2025-01-24 02:30:44 |   is|  1|
2025-01-24 02:30:44 |  raj|  1|
2025-01-24 02:30:44 |world|  1|
2025-01-24 02:30:44 | this|  1|
2025-01-24 02:30:44 +-----+---+
```

## Window operation

That is, word counts in words received between 10 minute windows 12:00 - 12:10, 12:05 - 12:15, 12:10 - 12:20, etc. Note that 12:00 - 12:10 means data that arrived after 12:00 but before 12:10. Now, consider a word that was received at 12:07. This word should increment the counts corresponding to two windows 12:00 - 12:10 and 12:05 - 12:15. So the counts will be indexed by both, the grouping key (i.e. the word) and the window (can be calculated from the event-time).

![window.drawio.svg](https://prod-files-secure.s3.us-west-2.amazonaws.com/0273592f-f54f-43f5-b46d-a5042292b3fe/bb9525a0-9999-41ba-b047-21a7beb9802f/window.drawio.svg)

## Discretized Streams (DStreams)

 **DStream** is the basic abstraction provided by Spark Streaming representing a continuous stream of data, either the input data stream received from source, or the processed data stream generated by transforming the input stream. Basic sources like StreamingContext API (file sources or sockets) and Advanced sources like Kafka are used.

Each RDD in a DStream contains data from a certain interval, as shown in the following figure.

## Join Operation