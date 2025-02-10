# Exploring Clustering Techniques with Machine Learning

In contrast to *supervised* machine learning, *unsupervised* learning is used when there is no "ground truth" from which to train and validate label predictions. The most common form of unsupervised learning is *clustering*, which is similar conceptually to *classification*, except that the the training data does not include known values for the class label to be predicted. Clustering works by separating the training cases based on similarities that can be determined from their feature values. Think of it this way; the numeric features of a given entity can be thought of as vector coordinates that define the entity's position in n-dimensional space. What a clustering model seeks to do is to identify groups, or *clusters*, of entities that are close to one another while being separated from other clusters.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/719aad8ccd0df83b61bb918de560f883676321c1/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/Clustering.svg)


## **Task Overview**  

In this lab, you will:  
1. **Explore unsupervised clustering** using a seeds dataset.  
2. **Visualize high-dimensional data** with Principal Component Analysis (PCA).  
3. **Determine optimal cluster count** using the "elbow" method.  
4. **Implement K-Means and Agglomerative Clustering** to group seed samples.  
5. **Compare clusters** against actual species labels to evaluate performance.

## Setup `ipykernel` for the notebook

At first, create a new directory for this lab and navigate into it:

```bash
mkdir -p Clustering
cd Clustering
```

In Poridhi's VSCode server, create a new notebook named `Clustering.ipynb` and select the python kernel.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image-8.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image-7.png)

Then select the python kernel from the `ipykernel` environment.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image-9.png)

## Loading a DataFrame from a  file

Download the Dataset by running the following command.

```bash
curl -o seeds.csv "https://raw.githubusercontent.com/Konami33/MlOps-Dataset/main/Data/seeds.csv"
```

* The -o flag specifies the output file name (seeds.csv in this case).
* The file will be saved in your current working directory. 


> **Citation**: The seeds dataset used in the this exercise was originally published by the Institute of Agrophysics of the Polish Academy of Sciences in Lublin, and can be downloaded from the UCI dataset repository (Dua, D. and Graff, C. (2019). UCI Machine Learning Repository [http://archive.ics.uci.edu/ml]. Irvine, CA: University of California, School of Information and Computer Science).

## Required Libraries

Install the required libraries:

```python
pip install pandas matplotlib scikit-learn
```

## **1. Load and Explore the Dataset**  


Load the seeds dataset and inspect its features.  

```python  
import pandas as pd

# load the training dataset
data = pd.read_csv('data/seeds.csv')

# Display a random sample of 10 observations (just the features)
features = data[data.columns[0:6]]
features.sample(10) 
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image.png) 

## **2. Reduce Dimensionality with PCA**

As you can see, the dataset contains six data points (or *features*) for each instance (*observation*) of a seed. So you could interpret these as coordinates that describe each instance's location in six-dimensional space.

Now, of course six-dimensional space is difficult to visualise in a three-dimensional world, or on a two-dimensional plot; so we'll take advantage of a mathematical technique called *Principal Component Analysis* (PCA) to analyze the relationships between the features and summarize each observation as coordinates for two principal components - in other words, we'll translate the six-dimensional feature values into two-dimensional coordinates.

Project 6D data into 2D for visualization.  

```python  
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA

# Normalize the numeric features so they're on the same scale
scaled_features = MinMaxScaler().fit_transform(features[data.columns[0:6]])

# Get two principal components
pca = PCA(n_components=2).fit(scaled_features)
features_2d = pca.transform(scaled_features)
features_2d[0:10] 
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image-1.png)

Now that we have the data points translated to two dimensions, we can visualize them in a plot:

```python
import matplotlib.pyplot as plt

%matplotlib inline

plt.scatter(features_2d[:,0],features_2d[:,1])
plt.xlabel('Dimension 1')
plt.ylabel('Dimension 2')
plt.title('Data')
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image-2.png)

Hopefully you can see at least two, arguably three, reasonably distinct groups of data points; but here lies one of the fundamental problems with clustering - without known class labels, how do you know how many clusters to separate your data into?

## **3. Determine Optimal Clusters with the Elbow Method**  

One way we can try to find out is to use a data sample to create a series of clustering models with an incrementing number of clusters, and measure how tightly the data points are grouped within each cluster. A metric often used to measure this tightness is the *within cluster sum of squares* (WCSS), with lower values meaning that the data points are closer. You can then plot the WCSS for each model.

Use WCSS (Within Cluster Sum of Squares) to find the best cluster count.  

```python  
#importing the libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
%matplotlib inline

# Create 10 models with 1 to 10 clusters
wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters = i)
    # Fit the data points
    kmeans.fit(features.values)
    # Get the WCSS (inertia) value
    wcss.append(kmeans.inertia_)
    
#Plot the WCSS values onto a line graph
plt.plot(range(1, 11), wcss)
plt.title('WCSS by Clusters')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.show()  
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image-3.png) 

The plot shows a large reduction in WCSS (so greater *tightness*) as the number of clusters increases from one to two, and a further noticable reduction from two to three clusters. After that, the reduction is less pronounced, resulting in an "elbow" in the chart at around three clusters. This is a good indication that there are two to three reasonably well separated clusters of data points.

## **4. Apply K-Means Clustering**  

The algorithm we used to create our test clusters is *K-Means*. This is a commonly used clustering algorithm that separates a dataset into *K* clusters of equal variance. The number of clusters, *K*, is user defined. The basic algorithm has the following steps:

1. A set of K centroids are randomly chosen.
2. Clusters are formed by assigning the data points to their closest centroid.
3. The means of each cluster is computed and the centroid is moved to the mean.
4. Steps 2 and 3 are repeated until a stopping criteria is met. Typically, the algorithm terminates when each new iteration results in negligable movement of centroids and the clusters become static.
5. When the clusters stop changing, the algorithm has *converged*, defining the locations of the clusters - note that the random starting point for the centroids means that re-running the algorithm could result in slightly different clusters, so training usually involves multiple iterations, reinitializing the centroids each time, and the model with the best WCSS is selected.

Let's try using K-Means on our seeds data with a K value of 3.

```python  
from sklearn.cluster import KMeans

# Create a model based on 3 centroids
model = KMeans(n_clusters=3, init='k-means++', n_init=100, max_iter=1000)
# Fit to the data and predict the cluster assignments for each data point
km_clusters = model.fit_predict(features.values)
# View the cluster assignments
km_clusters 
```

Let's see those cluster assignments with the two-dimensional data points.

```python
def plot_clusters(samples, clusters):
    col_dic = {0:'blue',1:'green',2:'orange'}
    mrk_dic = {0:'*',1:'x',2:'+'}
    colors = [col_dic[x] for x in clusters]
    markers = [mrk_dic[x] for x in clusters]
    for sample in range(len(clusters)):
        plt.scatter(samples[sample][0], samples[sample][1], color = colors[sample], marker=markers[sample], s=100)
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.title('Assignments')
    plt.show()

plot_clusters(features_2d, km_clusters)
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image-4.png)

Hopefully, the data has been separated into three distinct clusters.

So what's the practical use of clustering? In some cases, you may have data that you need to group into distict clusters without knowing how many clusters there are or what they indicate. For example a marketing organization might want to separate customers into distinct segments, and then investigate how those segments exhibit different purchasing behaviors.

Sometimes, clustering is used as an initial step towards creating a classification model. You start by identifying distinct groups of data points, and then assign class labels to those clusters. You can then use this labelled data to train a classification model.

## **5. Compare Clusters to Actual Species**  

In the case of the seeds data, the different species of seed are already known and encoded as 0 (*Kama*), 1 (*Rosa*), or 2 (*Canadian*), so we can use these identifiers to compare the species classifications to the clusters identified by our unsupervised algorithm.

```python  
seed_species = data[data.columns[7]]
plot_clusters(features_2d, seed_species.values)
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image-5.png)  

There may be some differences between the cluster assignments and class labels, but the K-Means model should have done a reasonable job of clustering the observations so that seeds of the same species are generally in the same cluster.

## **6. Hierarchical Clustering with Agglomerative Method**

### Hierarchical Clustering

Hierarchical clustering methods make fewer distributional assumptions when compared to K-means methods. However, K-means methods are generally more scalable, sometimes very much so.

Hierarchical clustering creates clusters by either a *divisive* method or *agglomerative* method. The divisive method is a "top down" approach starting with the entire dataset and then finding partitions in a stepwise manner. Agglomerative clustering is a **bottom up** approach. In this lab you will work with agglomerative clustering which roughly works as follows:

1. The linkage distances between each of the data points is computed.
2. Points are clustered pairwise with their nearest neighbor.
3. Linkage distances between the clusters are computed.
4. Clusters are combined pairwise into larger clusters.
5. Steps 3 and 4 are repeated until all data points are in a single cluster.

The linkage function can be computed in a number of ways:
- Ward linkage measures the increase in variance for the clusters being linked,
- Average linkage uses the mean pairwise distance between the members of the two clusters,
- Complete or Maximal linkage uses the maximum distance between the members of the two clusters.

Several different distance metrics are used to compute linkage functions:
- Euclidian or l2 distance is the most widely used. This is the only metric for the Ward linkage method.
- Manhattan or l1 distance is robust to outliers and has other interesting properties.
- Cosine similarity, is the dot product between the location vectors divided by the magnitudes of the vectors. Notice that this metric is a measure of similarity, whereas the other two metrics are measures of difference. Similarity can be quite useful when working with data such as images or text documents.

### Agglomerative Clustering

Let's see an example of clustering the seeds data using an agglomerative clustering algorithm.

```python  
from sklearn.cluster import AgglomerativeClustering

agg_model = AgglomerativeClustering(n_clusters=3)
agg_clusters = agg_model.fit_predict(features.values)
agg_clusters  
```

So what do the agglomerative cluster assignments look like?

```python
import matplotlib.pyplot as plt

%matplotlib inline

def plot_clusters(samples, clusters):
    col_dic = {0:'blue',1:'green',2:'orange'}
    mrk_dic = {0:'*',1:'x',2:'+'}
    colors = [col_dic[x] for x in clusters]
    markers = [mrk_dic[x] for x in clusters]
    for sample in range(len(clusters)):
        plt.scatter(samples[sample][0], samples[sample][1], color = colors[sample], marker=markers[sample], s=100)
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.title('Assignments')
    plt.show()

plot_clusters(features_2d, agg_clusters)
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/04-Clustering/images/image-6.png) 

## **Conclusion**  

This lab demonstrated the power of unsupervised learning through clustering techniques. We explored how PCA helps visualize high-dimensional data, used the elbow method to determine an optimal number of clusters, and applied K-Means and Agglomerative Clustering to identify natural groupings. By comparing these clusters with actual species labels, we gained insights into the effectiveness of these algorithms.  

