# Clustering Challenge

Clustering is an **unsupervised** machine learning technique in which you train a model to group similar entities into clusters based on their features.

In this challenge, you must separate a dataset consisting of three numeric features (**A**, **B**, and **C**) into clusters.

## Environment Setup in Poridhi's VS Code

First, we need to install the required packages.

```bash
sudo apt-get update
sudo apt-get install python3-pip
```

### Kernel Setup

In **Poridhi's VSCode server**, create a new Jupyter notebook. Select the python kernel.

![!\[alt text\](lab-5a-final.drawio.svg)](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/05a%20-%20Deep%20Neural%20Networks%20(TensorFlow)/images/image-13.png)

Install required extensions for running the notebook and then select the python kernel.

![!\[alt text\](lab-5a-final.drawio.svg)](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/05a%20-%20Deep%20Neural%20Networks%20(TensorFlow)/images/image-12.png)

## Review the data

First download the dataset file by running the following command and save it in the same directory as the notebook.

```sh
curl -o "clusters.csv" "https://raw.githubusercontent.com/Konami33/MlOps-Dataset/refs/heads/main/Challenges_Data/clusters.csv"
```

Run the following cell to load the data and view the first few rows.

```python
import pandas as pd

data = pd.read_csv('clusters.csv')
data.sample(10)
```

This dataset contains three numeric features (**A**, **B**, and **C**). This is how the data looks like:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/Challenges/04-Clustering%20Challenge/images/image-1.png)

> Make sure to install the necessary packages.

## Challenge

Your challenge is to 

- Identify the number of discrete clusters present in the data, and
- Create a clustering model that separates the data into that number of clusters. 
- You should also visualize the clusters to evaluate the level of separation achieved by your model.

> Add markdown and code cells as required to create your solution.

## Solution

There is no single "**correct**" solution. First try to explore the data and then come up with your own analysis and conclusions. Here is a sample solution if you get stuck. Here is method to do analysis on the data.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/Challenges/04-Clustering%20Challenge/images/c4.drawio.svg)

Run this command in a terminal to download the sample solution.

```sh
curl -o "Clustering Solution.ipynb" "https://raw.githubusercontent.com/Konami33/MlOps-Dataset/refs/heads/main/Challenges_Soln/04%20-%20Clustering%20Solution.ipynb"
```
