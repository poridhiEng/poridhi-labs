# Graph Algorithms with GraphFrame



On this lab of Spark, we will get to know about a new library of Apache Spark named GraphFrame.

# Table of Contents

1. Graph Algorithms with GraphFrame
    - Motif Finding
2. Graph Algorithms
    - Pagerank
    - Triangle Count
    - BFS
    - Label Propagation Algorithm
    - Shortest Path


## Graph Algorithms with GraphFrame

So far we’ve mainly been focusing on record data, which is typically stored in flat files or relational databases and can be represented as a matrix (a set of rows with named columns). Now we’ll turn our attention to graph-based data, which depicts the relationships between two or more data points.

This chapter introduces GraphFrames, a powerful external package for Spark that provides APIs for representing directed and undirected graphs, querying and analyzing graphs, and running algorithms on graphs.

## Overviews on Graphs

A graph is a pair of V(a set of nodes, called verticles) and E(collection of pairs of verticles, edges)

The graphs are basically divided into two types: 
    1. Directed edge & 2. Undirected edge.
    

![directedgraph.drawio.svg](https://github.com/nakibworkspace/AS-Lab-03/raw/main/images/image1.svg)

Here the nodes are the verticles and the arrows are called the edges.

> To implement graph algorithms, Spark offers two different APIs to work with GraphX (RDD based) and GraphFrame (DataFrame based). As GraphFrame is more versatile to work with different programming languages and it’s pythonic, we are going to focus on that more.
> 

**Prerequisites**:

- Java Development Kit (jdk)
    
    ```python
    sudo apt install default-jdk -y
    ```
    
    ```python
    sudo apt install default-jdk -y
    ```
    
- PySpark
    
    ```python
    sudo apt install python3-pip -y
    pip install pyspark
    ```
    
    ```python
    sudo apt install python3-pip -y
    pip install pyspark
    ```
    
- GraphFrame
    
    ```python
    pip install graphframes
    ```
    
    ```python
    pip install graphframes
    ```
    

Importing required libraries

```python
from pyspark.sql import SparkSession
from graphframes import GraphFrame
```

Creating a SparkSession

```python
spark = SparkSession.builder \
.appName("GraphFrames Tutorial") \
.config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.2-s_2.12") \
.getOrCreate()
```

![Screenshot 2025-01-16 at 15.08.32.png](https://github.com/nakibworkspace/AS-Lab-03/raw/main/images/image2.png)

Creating vertices(nodes) and edges(the connection between the nodes)

```python
vertices= spark.createDataFrame([
("a", "Alice", 34),
("b", "Bob", 36),
("c", "Charlie", 30),
("d", "David", 29),
("e", "Esther", 32),
("f", "Fanny", 36),
("g", "Gabby", 60)
], ["id", "name", "age"])

edges = spark.createDataFrame([
  ("a", "b", "friend"),
  ("b", "c", "follow"),
  ("c", "b", "follow"),
  ("f", "c", "follow"),
  ("e", "f", "follow"),
  ("e", "d", "friend"),
  ("d", "a", "friend"),
  ("a", "e", "friend")
], ["src", "dst", "relationship"])
```

Creating GraphFrame with the vertices and edges.

```python
graph= GraphFrame(vertices, edges)
```

With the created `graphframe`, we can do some basic operations shown below.

```python
graph.vertices.show()

+---+-------+---+
| id|   name|age|
+---+-------+---+
|  a|  Alice| 34|
|  b|    Bob| 36|
|  c|Charlie| 30|
|  d|  David| 29|
|  e| Esther| 32|
|  f|  Fanny| 36|
|  g|  Gabby| 60|
+---+-------+---+
```

```python
graph.edges.show()

+---+---+------------+
|src|dst|relationship|
+---+---+------------+
|  a|  b|      friend|
|  b|  c|      follow|
|  c|  b|      follow|
|  f|  c|      follow|
|  e|  f|      follow|
|  e|  d|      friend|
|  d|  a|      friend|
|  a|  e|      friend|
+---+---+------------+
```

The `indegree` of a vertex is the number of edges that point into it.

```python
graph.inDegrees.show()

+---+--------+
| id|inDegree|
+---+--------+
|  c|       2|
|  b|       2|
|  f|       1|
|  e|       1|
|  d|       1|
|  a|       1|
+---+--------+
```

The `outdegree` of a vertex is the number of edges that point out of it.

```python
graph.outDegrees.show()

+---+---------+
| id|outDegree|
+---+---------+
|  f|        1|
|  c|        1|
|  b|        1|
|  a|        2|
|  e|        2|
|  d|        1|
+---+---------+
```

```python
#find the youngest user in the group
graph.vertices.groupBy().min("age").show()

+--------+
|min(age)|
+--------+
|      29|
+--------+
```

used `filter` operation with conditions for explorations

```python
numFollows=graph.edges.filter("relationship= 'follow'").show()

+---+---+------------+
|src|dst|relationship|
+---+---+------------+
|  b|  c|      follow|
|  c|  b|      follow|
|  f|  c|      follow|
|  e|  f|      follow|
+---+---+------------+
```

### **Motif Finding**

Motif finding refers to searching for structural patterns in a graph.

For example, `graph.find("(a)-[e]->(b); (b)-[e2]->(a)")` will search for pairs of vertices `a,b` connected by edges in both directions. It will return a `DataFrame` of all such structures in the graph, with columns for each of the named elements (vertices or edges) in the motif. In this case, the returned columns will be “a, b, e, e2.”

```python
graph.find("(a)-[e]->(b)").show()

+----------------+--------------+----------------+
|               a|             e|               b|
+----------------+--------------+----------------+
|  {f, Fanny, 36}|{f, c, follow}|{c, Charlie, 30}|
|    {b, Bob, 36}|{b, c, follow}|{c, Charlie, 30}|
|{c, Charlie, 30}|{c, b, follow}|    {b, Bob, 36}|
|  {a, Alice, 34}|{a, b, friend}|    {b, Bob, 36}|
|  {d, David, 29}|{d, a, friend}|  {a, Alice, 34}|
| {e, Esther, 32}|{e, f, follow}|  {f, Fanny, 36}|
|  {a, Alice, 34}|{a, e, friend}| {e, Esther, 32}|
| {e, Esther, 32}|{e, d, friend}|  {d, David, 29}|
+----------------+--------------+----------------+
```

using `graph.find` or motif finding to find out the friends of friend.

```python

f_of_f = graph.find("(a)-[]->(b); (b)-[]->(c)")
f_of_f.show()

+----------------+----------------+----------------+
|               a|               b|               c|
+----------------+----------------+----------------+
| {e, Esther, 32}|  {d, David, 29}|  {a, Alice, 34}|
|  {d, David, 29}|  {a, Alice, 34}|    {b, Bob, 36}|
|  {f, Fanny, 36}|{c, Charlie, 30}|    {b, Bob, 36}|
|    {b, Bob, 36}|{c, Charlie, 30}|    {b, Bob, 36}|
|{c, Charlie, 30}|    {b, Bob, 36}|{c, Charlie, 30}|
|  {a, Alice, 34}|    {b, Bob, 36}|{c, Charlie, 30}|
| {e, Esther, 32}|  {f, Fanny, 36}|{c, Charlie, 30}|
|  {a, Alice, 34}| {e, Esther, 32}|  {d, David, 29}|
|  {d, David, 29}|  {a, Alice, 34}| {e, Esther, 32}|
|  {a, Alice, 34}| {e, Esther, 32}|  {f, Fanny, 36}|
+----------------+----------------+----------------+
```

## **Graph Algorithms:**

### **Pagerank**

Assigns a rank to each vertex in a graph based on the number and quality of incoming edges. Also helps to find out the influence of a vertex in the graph.

```python
#pagerank
results= graph.pageRank(resetProbability=0.15, maxIter=10)
results.vertices.select("id","pagerank").show()

+---+-------------------+
| id|           pagerank|
+---+-------------------+
|  g|0.17073170731707318|
|  f|0.32504910549694244|
|  e| 0.3613490987992571|
|  d|0.32504910549694244|
|  c| 2.6667877057849627|
|  b| 2.7025217677349773|
|  a| 0.4485115093698443|
+---+-------------------+
```

Using `graph.pageRank` to find the most influential person it the graph. 

```python

pr_result= graph.pageRank(resetProbability=0.15, maxIter=10)
pr_result.vertices.orderBy("pagerank", ascending= False).show()

+---+-------+---+-------------------+
| id|   name|age|           pagerank|
+---+-------+---+-------------------+
|  b|    Bob| 36| 2.7025217677349773|
|  c|Charlie| 30| 2.6667877057849627|
|  a|  Alice| 34| 0.4485115093698443|
|  e| Esther| 32| 0.3613490987992571|
|  f|  Fanny| 36|0.32504910549694244|
|  d|  David| 29|0.32504910549694244|
|  g|  Gabby| 60|0.17073170731707318|
+---+-------+---+-------------------+
```

### **Triangle Count**

A set of three vertices where each vertex is connected to the other two. Also can be the number of triangles that passes through each vertex in a graph. Spark checks pair of it’s neighbours to see if they are connected. Used to measure the transitivity or clustering coefficient of a graph.

```python
result= graph.triangleCount()
result.select("id","count").show()

+---+-----+
| id|count|
+---+-----+
|  c|    0|
|  b|    0|
|  a|    1|
|  g|    0|
|  f|    0|
|  e|    1|
|  d|    1|
+---+-----+
```

### **BFS(Breadth-first Search)**

 finds the shortest path from one vertex to another. The beginning and the end is needed to be specified in Spark.

```python
paths= graph.bfs("name= 'Esther'", "age < 32")
paths.show()

+---------------+--------------+--------------+
|           from|            e0|            to|
+---------------+--------------+--------------+
|{e, Esther, 32}|{e, d, friend}|{d, David, 29}|
+---------------+--------------+--------------+
```

We can also specify edge filters and max path length.

```python
#specify edge filters and max path length
new= graph.bfs("name= 'Esther'", "age < 32", \
edgeFilter= "relationship != 'friend'", maxPathLength= 3)
new.show()

+---------------+--------------+--------------+--------------+----------------+
|           from|            e0|            v1|            e1|              to|
+---------------+--------------+--------------+--------------+----------------+
|{e, Esther, 32}|{e, f, follow}|{f, Fanny, 36}|{f, c, follow}|{c, Charlie, 30}|
+---------------+--------------+--------------+--------------+----------------+
```

### **Label Propagation Algorithm**

 a graph clustering algorithm used to identify communities or clusters in a graph. It assigns labels to vertices and propagates these labels through the graph based on the structures of the graph.

![Initial phase of LPA where only two nodes are marked only as different.](https://github.com/nakibworkspace/AS-Lab-03/raw/main/images/image3.svg)

Initial phase of LPA where only two nodes are marked only as different.

![Final phase of LPA where the other nodes are effected by the neighbour nodes.](https://github.com/nakibworkspace/AS-Lab-03/raw/main/images/image4.svg)

Final phase of LPA where the other nodes are effected by the neighbour nodes.

```python
result= graph.labelPropagation(maxIter=5)
result.select("id","label").show()

+---+-------------+
| id|        label|
+---+-------------+
|  g| 146028888064|
|  f|1047972020224|
|  e|1460288880640|
|  d|1460288880640|
|  c|1382979469312|
|  b|1047972020224|
|  a|1382979469312|
+---+-------------+
```

### **Shortest Path**

Refers to the path between two vertices or nodes that has the smallest total weight. This is used for problems with graph theory such as navigation, network routing and optimization.

```python
results= graph.shortestPaths(landmarks=["a","d"])
results.select("id","distances").show()

+---+----------------+
| id|       distances|
+---+----------------+
|  g|              {}|
|  f|              {}|
|  e|{a -> 2, d -> 1}|
|  d|{a -> 1, d -> 0}|
|  c|              {}|
|  b|              {}|
|  a|{a -> 0, d -> 2}|
+---+----------------+
```
