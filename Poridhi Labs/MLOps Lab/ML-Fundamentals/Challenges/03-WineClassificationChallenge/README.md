# Classification Challenge

Wine experts can identify wines from specific vineyards through smell and taste, but the factors that give different wines their individual charateristics are actually based on their chemical composition.

In this challenge, you must train a classification model to analyze the **chemical and visual** features of wine samples and classify them based on their cultivar (grape variety).

> **Citation**: The data used in this exercise was originally collected by Forina, M. et al.
>
> PARVUS - An Extendible Package for Data Exploration, Classification and Correlation.
Institute of Pharmaceutical and Food Analysis and Technologies, Via Brigata Salerno,
16147 Genoa, Italy.


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
curl -o "wine.csv" "https://raw.githubusercontent.com/Konami33/MlOps-Dataset/refs/heads/main/Challenges_Data/wine.csv"
```

Run the following cell to load the data and view the first few rows.

```python
import pandas as pd

# load the training dataset
data = pd.read_csv('wine.csv')
data.sample(10)
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/Challenges/03-WineClassificationChallenge/images/image-1.png)

> Make sure to install the necessary packages.

The dataset consists of 12 numeric features and a classification label with the following classes:

- **0** (*variety A*)
- **1** (*variety B*)
- **2** (*variety C*)

## Challenge

Your challenge is to train a classification model that achieves an overall *Recall* metric of over `0.95 (95%)`.

> Add markdown and code cells as required to create your solution.

## Evaluate the Model

When you're happy with your model's predictive performance, save it and then use it to predict classes for the following two new wine samples:

- \[13.72,1.43,2.5,16.7,108,3.4,3.67,0.19,2.04,6.8,0.89,2.87,1285\]
- \[12.37,0.94,1.36,10.6,88,1.98,0.57,0.28,0.42,1.95,1.05,1.82,520\]


## Solution

There is no single "**correct**" solution. First try to explore the data and then come up with your own analysis and conclusions. Here is a sample solution if you get stuck. Here is method to do analysis on the data.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/Challenges/03-WineClassificationChallenge/images/c3.drawio.svg)

Run this command in a terminal to download the sample solution.

```sh
curl -o "Wine Classification Solution.ipynb" "https://raw.githubusercontent.com/Konami33/MlOps-Dataset/refs/heads/main/Challenges_Soln/03%20-%20Wine%20Classification%20Solution.ipynb"
```