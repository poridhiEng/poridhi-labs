# Understanding Supervised Regression Models

This lab explores supervised regression techniques to predict daily bicycle rentals for a bike-sharing service. Using historical data, we train and evaluate multiple regression models to forecast rental counts based on features such as weather, season, and weekday. The lab emphasizes data exploration, preprocessing, model selection, and hyperparameter tuning to optimize performance.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/f23ce46b4fba8406a13bb4c2ceb3575ac23872da/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/Regression.svg)

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

## Regression

*Supervised* machine learning techniques involve training a model to
operate on a set of *features* and predict a *label* using a dataset
that includes some already-known label values. The training process
*fits* the features to the known labels to define a general function
that can be applied to new features for which the labels are unknown,
and predict them. You can think of this function like this, in which
***y*** represents the label we want to predict and ***x*** represents
the features the model uses to predict it.

$$y = f(x)$$

In most cases, *x* is actually a *vector* that consists of multiple
feature values, so to be a little more precise, the function could be
expressed like this:

$$y = f([x_1, x_2, x_3, ...])$$

The goal of training the model is to find a function that performs some
kind of calculation to the *x* values that produces the result *y*. We
do this by applying a machine learning *algorithm* that tries to fit the
*x* values to a calculation that produces *y* reasonably accurately for
all of the cases in the training dataset.

There are lots of machine learning algorithms for supervised learning,
and they can be broadly divided into two types:

-   ***Regression* algorithms**: Algorithms that predict a *y* value
    that is a numeric value, such as the price of a house or the number
    of sales transactions.
-   ***Classification* algorithms**: Algorithms that predict to which
    category, or *class*, an observation belongs. The *y* value in a
    classification model is a vector of probability values between 0 and
    1, one for each class, indicating the probability of the observation
    belonging to each class.

In this notebook, we\'ll focus on *regression*, using an example based
on a real study in which data for a bicycle sharing scheme was collected
and used to predict the number of rentals based on seasonality and
weather conditions. We\'ll use a simplified version of the dataset from
that study.

> **Citation**: The data used in this exercise is derived from [Capital
> Bikeshare](https://www.capitalbikeshare.com/system-data) and is used
> in accordance with the published [license
> agreement](https://www.capitalbikeshare.com/data-license-agreement).

## Loading a DataFrame from a  file

Download the Dataset by running the following command.

```bash
curl -o daily-bike-share.csv "https://raw.githubusercontent.com/Konami33/MlOps-Dataset/main/Data/daily-bike-share.csv"
```

* The -o flag specifies the output file name (`daily-bike-share.csv` in this case).
* The file will be saved in your current working directory.

## Required Libraries

Install the required libraries:

```python
pip install pandas matplotlib scikit-learn
```


## Explore the Data

The first step in any machine learning project is to explore the data
that you will use to train a model. The goal of this exploration is to
try to understand the relationships between its attributes; in
particular, any apparent correlation between the *features* and the
*label* your model will try to predict. This may require some work to
detect and fix issues in the data (such as dealing with missing values,
errors, or outlier values), deriving new feature columns by transforming
or combining existing features (a process known as *feature
engineering*), *normalizing* numeric features (values you can measure or
count) so they\'re on a similar scale, and *encoding* categorical
features (values that represent discrete categories) as numeric
indicators.

Let\'s start by loading the bicycle sharing data as a **Pandas**
DataFrame and viewing the first few rows.

``` python
import pandas as pd

# load the training dataset
bike_data = pd.read_csv('data/daily-bike-share.csv')
bike_data.head()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image.png)

The data consists of the following columns:

-   **instant**: A unique row identifier
-   **dteday**: The date on which the data was observed - in this case,
    the data was collected daily; so there\'s one row per date.
-   **season**: A numerically encoded value indicating the season
    (1:spring, 2:summer, 3:fall, 4:winter)
-   **yr**: The year of the study in which the observation was made (the
    study took place over two years - year 0 represents 2011, and year 1
    represents 2012)
-   **mnth**: The calendar month in which the observation was made
    (1:January \... 12:December)
-   **holiday**: A binary value indicating whether or not the
    observation was made on a public holiday)
-   **weekday**: The day of the week on which the observation was made
    (0:Sunday \... 6:Saturday)
-   **workingday**: A binary value indicating whether or not the day is
    a working day (not a weekend or holiday)
-   **weathersit**: A categorical value indicating the weather situation
    (1:clear, 2:mist/cloud, 3:light rain/snow, 4:heavy
    rain/hail/snow/fog)
-   **temp**: The temperature in celsius (normalized)
-   **atemp**: The apparent (\"feels-like\") temperature in celsius
    (normalized)
-   **hum**: The humidity level (normalized)
-   **windspeed**: The windspeed (normalized)
-   **rentals**: The number of bicycle rentals recorded.

In this dataset, **rentals** represents the label (the *y* value) our
model must be trained to predict. The other columns are potential
features (*x* values).

As mentioned previously, you can perform some *feature engineering* to
combine or derive new features. For example, let\'s add a new column
named **day** to the dataframe by extracting the day component from the
existing **dteday** column. The new column represents the day of the
month from 1 to 31.

``` python
bike_data['day'] = pd.DatetimeIndex(bike_data['dteday']).day
bike_data.head(32)
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-1.png)

OK, let\'s start our analysis of the data by examining a few key
descriptive statistics. We can use the dataframe\'s **describe** method
to generate these for the numeric features as well as the **rentals**
label column.

``` python
numeric_features = ['temp', 'atemp', 'hum', 'windspeed']
bike_data[numeric_features + ['rentals']].describe()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-2.png)

The statistics reveal some information about the distribution of the
data in each of the numeric fields, including the number of observations
(there are 731 records), the mean, standard deviation, minimum and
maximum values, and the quartile values (the threshold values for 25%,
50% - which is also the median, and 75% of the data). From this, we can
see that the mean number of daily rentals is around 848; but there\'s a
comparatively large standard deviation, indicating a lot of variance in
the number of rentals per day.

We might get a clearer idea of the distribution of rentals values by
visualizing the data. Common plot types for visualizing numeric data
distributions are *histograms* and *box plots*, so let\'s use Python\'s
**matplotlib** library to create one of each of these for the
**rentals** column.

``` python
import pandas as pd
import matplotlib.pyplot as plt

# This ensures plots are displayed inline in the Jupyter notebook
%matplotlib inline

# Get the label column
label = bike_data['rentals']


# Create a figure for 2 subplots (2 rows, 1 column)
fig, ax = plt.subplots(2, 1, figsize = (9,12))

# Plot the histogram   
ax[0].hist(label, bins=100)
ax[0].set_ylabel('Frequency')

# Add lines for the mean, median, and mode
ax[0].axvline(label.mean(), color='magenta', linestyle='dashed', linewidth=2)
ax[0].axvline(label.median(), color='cyan', linestyle='dashed', linewidth=2)

# Plot the boxplot   
ax[1].boxplot(label, vert=False)
ax[1].set_xlabel('Rentals')

# Add a title to the Figure
fig.suptitle('Rental Distribution')

# Show the figure
fig.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-3.png)

The plots show that the number of daily rentals ranges from 0 to just
over 3,400. However, the mean (and median) number of daily rentals is
closer to the low end of that range, with most of the data between 0 and
around 2,200 rentals. The few values above this are shown in the box
plot as small circles, indicating that they are *outliers* - in other
words, unusually high or low values beyond the typical range of most of
the data.

We can do the same kind of visual exploration of the numeric features.
Let\'s create a histogram for each of these.

``` python
# Plot a histogram for each numeric feature
for col in numeric_features:
    fig = plt.figure(figsize=(9, 6))
    ax = fig.gca()
    feature = bike_data[col]
    feature.hist(bins=100, ax = ax)
    ax.axvline(feature.mean(), color='magenta', linestyle='dashed', linewidth=2)
    ax.axvline(feature.median(), color='cyan', linestyle='dashed', linewidth=2)
    ax.set_title(col)
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-4.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-5.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-6.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-7.png)

The numeric features seem to be more *normally* distributed, with the
mean and median nearer the middle of the range of values, coinciding
with where the most commonly occurring values are.

> **Note**: The distributions are not truly *normal* in the statistical
> sense, which would result in a smooth, symmetric \"bell-curve\"
> histogram with the mean and mode (the most common value) in the
> center; but they do generally indicate that most of the observations
> have a value somewhere near the middle.

We\'ve explored the distribution of the numeric values in the dataset,
but what about the categorical features? These aren\'t continuous
numbers on a scale, so we can\'t use histograms; but we can plot a bar
chart showing the count of each discrete value for each category.

``` python
import numpy as np

# plot a bar plot for each categorical feature count
categorical_features = ['season','mnth','holiday','weekday','workingday','weathersit', 'day']

for col in categorical_features:
    counts = bike_data[col].value_counts().sort_index()
    fig = plt.figure(figsize=(9, 6))
    ax = fig.gca()
    counts.plot.bar(ax = ax, color='steelblue')
    ax.set_title(col + ' counts')
    ax.set_xlabel(col) 
    ax.set_ylabel("Frequency")
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-8.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-9.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-10.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-11.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-12.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-13.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-14.png)

Many of the categorical features show a more or less *uniform*
distribution (meaning there\'s roughly the same number of rows for each
category). Exceptions to this include:

-   **holiday**: There are many fewer days that are holidays than days
    that aren\'t.
-   **workingday**: There are more working days than non-working days.
-   **weathersit**: Most days are category *1* (clear), with category
    *2* (mist and cloud) the next most common. There are comparatively
    few category *3* (light rain or snow) days, and no category *4*
    (heavy rain, hail, or fog) days at all.

Now that we know something about the distribution of the data in our
columns, we can start to look for relationships between the features and
the **rentals** label we want to be able to predict.

For the numeric features, we can create scatter plots that show the
intersection of feature and label values. We can also calculate the
*correlation* statistic to quantify the apparent relationship.

``` python
for col in numeric_features:
    fig = plt.figure(figsize=(9, 6))
    ax = fig.gca()
    feature = bike_data[col]
    label = bike_data['rentals']
    correlation = feature.corr(label)
    plt.scatter(x=feature, y=label)
    plt.xlabel(col)
    plt.ylabel('Bike Rentals')
    ax.set_title('rentals vs ' + col + '- correlation: ' + str(correlation))
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-15.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-16.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-17.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-18.png)

The results aren\'t conclusive, but if you look closely at the scatter
plots for **temp** and **atemp**, you can see a vague diagonal trend
showing that higher rental counts tend to coincide with higher
temperatures; and a correlation value of just over 0.5 for both of these
features supports this observation. Conversely, the plots for **hum**
and **windspeed** show a slightly negative correlation, indicating that
there are fewer rentals on days with high humidity or windspeed.

Now let\'s compare the categorical features to the label. We\'ll do this
by creating box plots that show the distribution of rental counts for
each category.

``` python
# plot a boxplot for the label by each categorical feature
for col in categorical_features:
    fig = plt.figure(figsize=(9, 6))
    ax = fig.gca()
    bike_data.boxplot(column = 'rentals', by = col, ax = ax)
    ax.set_title('Label by ' + col)
    ax.set_ylabel("Bike Rentals")
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-19.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-20.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-21.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-22.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-23.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-24.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-25.png)

The plots show some variance in the relationship between some category
values and rentals. For example, there\'s a clear difference in the
distribution of rentals on weekends (**weekday** 0 or 6) and those
during the working week (**weekday** 1 to 5). Similarly, there are
notable differences for **holiday** and **workingday** categories.
There\'s a noticeable trend that shows different rental distributions in
summer and fall months compared to spring and winter months. The
**weathersit** category also seems to make a difference in rental
distribution. The **day** feature we created for the day of the month
shows little variation, indicating that it\'s probably not predictive of
the number of rentals.

## Train a Regression Model

Now that we\'ve explored the data, it\'s time to use it to train a
regression model that uses the features we\'ve identified as potentially
predictive to predict the **rentals** label. The first thing we need to
do is to separate the features we want to use to train the model from
the label we want it to predict.

``` python
# Separate features and labels
X, y = bike_data[['season','mnth', 'holiday','weekday','workingday','weathersit','temp', 'atemp', 'hum', 'windspeed']].values, bike_data['rentals'].values
print('Features:',X[:10], '\nLabels:', y[:10], sep='\n')
```

After separating the dataset, we now have numpy arrays named **X**
containing the features, and **y** containing the labels.

We *could* train a model using all of the data; but it\'s common
practice in supervised learning to split the data into two subsets; a
(typically larger) set with which to train the model, and a smaller
\"hold-back\" set with which to validate the trained model. This enables
us to evaluate how well the model performs when used with the validation
dataset by comparing the predicted labels to the known labels. It\'s
important to split the data *randomly* (rather than say, taking the
first 70% of the data for training and keeping the rest for validation).
This helps ensure that the two subsets of data are statistically
comparable (so we validate the model with data that has a similar
statistical distribution to the data on which it was trained).

To randomly split the data, we\'ll use the **train_test_split** function
in the **scikit-learn** library. This library is one of the most widely
used machine learning packages for Python.

``` python
from sklearn.model_selection import train_test_split

# Split data 70%-30% into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=0)

print ('Training Set: %d rows\nTest Set: %d rows' % (X_train.shape[0], X_test.shape[0]))
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-26.png)

Now we have the following four datasets:

-   **X_train**: The feature values we\'ll use to train the model
-   **y_train**: The corresponding labels we\'ll use to train the model
-   **X_test**: The feature values we\'ll use to validate the model
-   **y_test**: The corresponding labels we\'ll use to validate the
    model

Now we\'re ready to train a model by fitting a suitable regression
algorithm to the training data. We\'ll use a *linear regression*
algorithm, a common starting point for regression that works by trying
to find a linear relationship between the *X* values and the *y* label.
The resulting model is a function that conceptually defines a line where
every possible X and y value combination intersect.

In Scikit-Learn, training algorithms are encapsulated in *estimators*,
and in this case we\'ll use the **LinearRegression** estimator to train
a linear regression model.

``` python
# Train the model
from sklearn.linear_model import LinearRegression

# Fit a linear regression model on the training set
model = LinearRegression().fit(X_train, y_train)
print (model)
```

### Evaluate the Trained Model

Now that we\'ve trained the model, we can use it to predict rental
counts for the features we held back in our validation dataset. Then we
can compare these predictions to the actual label values to evaluate how
well (or not!) the model is working.

``` python
import numpy as np

predictions = model.predict(X_test)
np.set_printoptions(suppress=True)
print('Predicted labels: ', np.round(predictions)[:10])
print('Actual labels   : ' ,y_test[:10])
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-27.png)

Comparing each prediction with its corresponding \"ground truth\" actual
value isn\'t a very efficient way to determine how well the model is
predicting. Let\'s see if we can get a better indication by visualizing
a scatter plot that compares the predictions to the actual labels.
We\'ll also overlay a trend line to get a general sense for how well the
predicted labels align with the true labels.

``` python
import matplotlib.pyplot as plt

%matplotlib inline

plt.scatter(y_test, predictions)
plt.xlabel('Actual Labels')
plt.ylabel('Predicted Labels')
plt.title('Daily Bike Share Predictions')
# overlay the regression line
z = np.polyfit(y_test, predictions, 1)
p = np.poly1d(z)
plt.plot(y_test,p(y_test), color='magenta')
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-28.png)

There\'s a definite diagonal trend, and the intersections of the
predicted and actual values are generally following the path of the
trend line; but there\'s a fair amount of difference between the ideal
function represented by the line and the results. This variance
represents the *residuals* of the model - in other words, the difference
between the label predicted when the model applies the coefficients it
learned during training to the validation data, and the actual value of
the validation label. These residuals when evaluated from the validation
data indicate the expected level of *error* when the model is used with
new data for which the label is unknown.

You can quantify the residuals by calculating a number of commonly used
evaluation metrics. We\'ll focus on the following three:

-   **Mean Square Error (MSE)**: The mean of the squared differences
    between predicted and actual values. This yields a relative metric
    in which the smaller the value, the better the fit of the model
-   **Root Mean Square Error (RMSE)**: The square root of the MSE. This
    yields an absolute metric in the same unit as the label (in this
    case, numbers of rentals). The smaller the value, the better the
    model (in a simplistic sense, it represents the average number of
    rentals by which the predictions are wrong!)
-   **Coefficient of Determination (usually known as *R-squared* or R<sup>2</sup>)**:
    A relative metric in which the higher the value, the better the fit
    higher the value, the better the fit of the model. In essence, this
    metric represents how much of the variance between predicted and
    actual label values the model is able to explain.

> **Note**: You can find out more about these and other metrics for
> evaluating regression models in the [Scikit-Learn
> documentation](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics)

Let\'s use Scikit-Learn to calculate these metrics for our model, based
on the predictions it generated for the validation data.

``` python
from sklearn.metrics import mean_squared_error, r2_score

mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)

rmse = np.sqrt(mse)
print("RMSE:", rmse)

r2 = r2_score(y_test, predictions)
print("R2:", r2)
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-29.png)

So now we\'ve quantified the ability of our model to predict the number
of rentals. It definitely has *some* predictive power, but we can
probably do better!

## Experiment with Algorithms

The linear regression algorithm we used to train the model has some
predictive capability, but there are many kinds of regression algorithm
we could try, including:

-   **Linear algorithms**: Not just the Linear Regression algorithm we
    used above (which is technically an *Ordinary Least Squares*
    algorithm), but other variants such as *Lasso* and *Ridge*.
-   **Tree-based algorithms**: Algorithms that build a decision tree to
    reach a prediction.
-   **Ensemble algorithms**: Algorithms that combine the outputs of
    multiple base algorithms to improve generalizability.

> **Note**: For a full list of Scikit-Learn estimators that encapsulate
> algorithms for supervised machine learning, see the [Scikit-Learn
> documentation](https://scikit-learn.org/stable/supervised_learning.html).
> There are many algorithms to choose from, but for most real-world
> scenarios, the [Scikit-Learn estimator cheat
> sheet](https://scikit-learn.org/stable/tutorial/machine_learning_map/index.html)
> can help you find a suitable starting point.

### Try Another Linear Algorithm

Let\'s try training our regression model by using a **Lasso** algorithm.
We can do this by just changing the estimator in the training code.

``` python
from sklearn.linear_model import Lasso

# Fit a lasso model on the training set
model = Lasso().fit(X_train, y_train)
print (model, "\n")

# Evaluate the model using the test data
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)
rmse = np.sqrt(mse)
print("RMSE:", rmse)
r2 = r2_score(y_test, predictions)
print("R2:", r2)

# Plot predicted vs actual
plt.scatter(y_test, predictions)
plt.xlabel('Actual Labels')
plt.ylabel('Predicted Labels')
plt.title('Daily Bike Share Predictions')
# overlay the regression line
z = np.polyfit(y_test, predictions, 1)
p = np.poly1d(z)
plt.plot(y_test,p(y_test), color='magenta')
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-30.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-31.png)

### Try a Decision Tree Algorithm

As an alternative to a linear model, there\'s a category of algorithms
for machine learning that uses a tree-based approach in which the
features in the dataset are examined in a series of evaluations, each of
which results in a *branch* in a *decision tree* based on the feature
value. At the end of each series of branches are leaf-nodes with the
predicted label value based on the feature values.

It\'s easiest to see how this works with an example. Let\'s train a
Decision Tree regression model using the bike rental data. After
training the model, the code below will print the model definition and a
text representation of the tree it uses to predict label values.

``` python
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import export_text

# Train the model
model = DecisionTreeRegressor().fit(X_train, y_train)
print (model, "\n")

# Visualize the model tree
tree = export_text(model)
print(tree)
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-32.png)

So now we have a tree-based model; but is it any good? Let\'s evaluate
it with the test data.

``` python
# Evaluate the model using the test data
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)
rmse = np.sqrt(mse)
print("RMSE:", rmse)
r2 = r2_score(y_test, predictions)
print("R2:", r2)

# Plot predicted vs actual
plt.scatter(y_test, predictions)
plt.xlabel('Actual Labels')
plt.ylabel('Predicted Labels')
plt.title('Daily Bike Share Predictions')
# overlay the regression line
z = np.polyfit(y_test, predictions, 1)
p = np.poly1d(z)
plt.plot(y_test,p(y_test), color='magenta')
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-33.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-34.png)

The tree-based model doesn\'t seem to have improved over the linear
model, so what else could we try?

### Try an Ensemble Algorithm

Ensemble algorithms work by combining multiple base estimators to
produce an optimal model, either by applying an aggregate function to a
collection of base models (sometimes referred to a *bagging*) or by
building a sequence of models that build on one another to improve
predictive performance (referred to as *boosting*).

For example, let\'s try a Random Forest model, which applies an
averaging function to multiple Decision Tree models for a better overall
model.

``` python
from sklearn.ensemble import RandomForestRegressor

# Train the model
model = RandomForestRegressor().fit(X_train, y_train)
print (model, "\n")

# Evaluate the model using the test data
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)
rmse = np.sqrt(mse)
print("RMSE:", rmse)
r2 = r2_score(y_test, predictions)
print("R2:", r2)

# Plot predicted vs actual
plt.scatter(y_test, predictions)
plt.xlabel('Actual Labels')
plt.ylabel('Predicted Labels')
plt.title('Daily Bike Share Predictions')
# overlay the regression line
z = np.polyfit(y_test, predictions, 1)
p = np.poly1d(z)
plt.plot(y_test,p(y_test), color='magenta')
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-35.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-36.png)

For good measure, let\'s also try a *boosting* ensemble algorithm.
We\'ll use a Gradient Boosting estimator, which like a Random Forest
algorithm builds multiple trees, but instead of building them all
independently and taking the average result, each tree is built on the
outputs of the previous one in an attempt to incrementally reduce the
*loss* (error) in the model.
 
``` python
# Train the model
from sklearn.ensemble import GradientBoostingRegressor

# Fit a lasso model on the training set
model = GradientBoostingRegressor().fit(X_train, y_train)
print (model, "\n")

# Evaluate the model using the test data
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)
rmse = np.sqrt(mse)
print("RMSE:", rmse)
r2 = r2_score(y_test, predictions)
print("R2:", r2)

# Plot predicted vs actual
plt.scatter(y_test, predictions)
plt.xlabel('Actual Labels')
plt.ylabel('Predicted Labels')
plt.title('Daily Bike Share Predictions')
# overlay the regression line
z = np.polyfit(y_test, predictions, 1)
p = np.poly1d(z)
plt.plot(y_test,p(y_test), color='magenta')
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-37.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-38.png)

## Optimize Hyperparameters

Take a look at the **GradientBoostingRegressor** estimator definition in
the output above, and note that it, like the other estimators we tried
previously, includes a large number of parameters that control the way
the model is trained. In machine learning, the term *parameters* refers
to values that can be determined from data; values that you specify to
affect the behavior of a training algorithm are more correctly referred
to as *hyperparameters*.

The specific hyperparameters for an estimator vary based on the
algorithm that the estimator encapsulates. In the case of the
**GradientBoostingRegressor** estimator, the algorithm is an ensemble
that combines multiple decision trees to create an overall predictive
model. You can learn about the hyperparameters for this estimator in the
[Scikit-Learn
documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html).

We won\'t go into the details of each hyperparameter here, but they work
together to affect the way the algorithm trains a model. In many cases,
the default values provided by Scikit-Learn will work well; but there
may be some advantage in modifying hyperparameters to get better
predictive performance or reduce training time.

So how do you know what hyperparameter values you should use? Well, in
the absence of a deep understanding of how the underlying algorithm
works, you\'ll need to experiment. Fortunately, SciKit-Learn provides a
way to *tune* hyperparameters by trying multiple combinations and
finding the best result for a given performance metric.

Let\'s try using a *grid search* approach to try combinations from a
grid of possible values for the **learning_rate** and **n_estimators**
hyperparameters of the **GradientBoostingRegressor** estimator.

``` python
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, r2_score

# Use a Gradient Boosting algorithm
alg = GradientBoostingRegressor()

# Try these hyperparameter values
params = {
 'learning_rate': [0.1, 0.5, 1.0],
 'n_estimators' : [50, 100, 150]
 }

# Find the best hyperparameter combination to optimize the R2 metric
score = make_scorer(r2_score)
gridsearch = GridSearchCV(alg, params, scoring=score, cv=3, return_train_score=True)
gridsearch.fit(X_train, y_train)
print("Best parameter combination:", gridsearch.best_params_, "\n")

# Get the best model
model=gridsearch.best_estimator_
print(model, "\n")

# Evaluate the model using the test data
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)
rmse = np.sqrt(mse)
print("RMSE:", rmse)
r2 = r2_score(y_test, predictions)
print("R2:", r2)

# Plot predicted vs actual
plt.scatter(y_test, predictions)
plt.xlabel('Actual Labels')
plt.ylabel('Predicted Labels')
plt.title('Daily Bike Share Predictions')
# overlay the regression line
z = np.polyfit(y_test, predictions, 1)
p = np.poly1d(z)
plt.plot(y_test,p(y_test), color='magenta')
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-39.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-40.png)

> **Note**: The use of random values in the Gradient Boosting algorithm results in slightly different metrics each time. In this case, the best model produced by hyperparameter tuning is unlikely to be significantly better than one trained with the default hyperparameter values; but it's still useful to know about the hyperparameter tuning technique!

## Preprocess the Data

We trained a model with data that was loaded straight from a source file, with only moderately successful results.

In practice, it's common to perform some preprocessing of the data to make it easier for the algorithm to fit a model to it. There's a huge range of preprocessing transformations you can perform to get your data ready for modeling, but we'll limit ourselves to a few common techniques:

### Scaling numeric features

Normalizing numeric features so they're on the same scale prevents features with large values from producing coefficients that disproportionately affect the predictions. For example, suppose your data includes the following numeric features:

| A |  B  |  C  |
| - | --- | --- |
| 3 | 480 | 65  |
    
Normalizing these features to the same scale may result in the following values (assuming A contains values from 0 to 10, B contains values from 0 to 1000, and C contains values from 0 to 100):

|  A  |  B  |  C  |
| --  | --- | --- |
| 0.3 | 0.48| 0.65|

There are multiple ways you can scale numeric data, such as calculating the minimum and maximum values for each column and assigning a proportional value between 0 and 1, or by using the mean and standard deviation of a normally distributed variable to maintain the same *spread* of values on a different scale.

### Encoding categorical variables

Machine learning models work best with numeric features rather than text values, so you generally need to convert categorical features into numeric representations.  For example, suppose your data includes the following categorical feature. 

| Size |
| ---- |
|  S   |
|  M   |
|  L   |

You can apply *ordinal encoding* to substitute a unique integer value for each category, like this:

| Size |
| ---- |
|  0   |
|  1   |
|  2   |

Another common technique is to use *one hot encoding* to create individual binary (0 or 1) features for each possible category value. For example, you could use one-hot encoding to translate the possible categories into binary columns like this:

|  Size_S  |  Size_M  |  Size_L  |
| -------  | -------- | -------- |
|    1     |     0    |    0     |
|    0     |     1    |    0     |
|    0     |     0    |    1     |

To apply these preprocessing transformations to the bike rental, we'll make use of a Scikit-Learn feature named *pipelines*. These enable us to define a set of preprocessing steps that end with an algorithm. You can then fit the entire pipeline to the data, so that the model encapsulates all of the preprocessing steps as well as the regression algorithm. This is useful, because when we want to use the model to predict values from new data, we need to apply the same transformations (based on the same statistical distributions and category encodings used with the training data).

>**Note**: The term *pipeline* is used extensively in machine learning, often to mean very different things! In this context, we're using it to refer to pipeline objects in Scikit-Learn, but you may see it used elsewhere to mean something else.

``` python
# Train the model
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression
import numpy as np

# Define preprocessing for numeric columns (scale them)
numeric_features = [6,7,8,9]
numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())])

# Define preprocessing for categorical features (encode them)
categorical_features = [0,1,2,3,4,5]
categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

# Combine preprocessing steps
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

# Create preprocessing and training pipeline
pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                           ('regressor', GradientBoostingRegressor())])


# fit the pipeline to train a linear regression model on the training set
model = pipeline.fit(X_train, (y_train))
print (model)
```

OK, the model is trained, including the preprocessing steps. Let\'s see
how it performs with the validation data.

``` python
# Get predictions
predictions = model.predict(X_test)

# Display metrics
mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)
rmse = np.sqrt(mse)
print("RMSE:", rmse)
r2 = r2_score(y_test, predictions)
print("R2:", r2)

# Plot predicted vs actual
plt.scatter(y_test, predictions)
plt.xlabel('Actual Labels')
plt.ylabel('Predicted Labels')
plt.title('Daily Bike Share Predictions')
z = np.polyfit(y_test, predictions, 1)
p = np.poly1d(z)
plt.plot(y_test,p(y_test), color='magenta')
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-41.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-42.png)

The pipeline is composed of the transformations and the algorithm used
to train the model. To try an alternative algorithm you can just change
that step to a different kind of estimator.

``` python
# Use a different estimator in the pipeline
pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                           ('regressor', RandomForestRegressor())])


# fit the pipeline to train a linear regression model on the training set
model = pipeline.fit(X_train, (y_train))
print (model, "\n")

# Get predictions
predictions = model.predict(X_test)

# Display metrics
mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)
rmse = np.sqrt(mse)
print("RMSE:", rmse)
r2 = r2_score(y_test, predictions)
print("R2:", r2)

# Plot predicted vs actual
plt.scatter(y_test, predictions)
plt.xlabel('Actual Labels')
plt.ylabel('Predicted Labels')
plt.title('Daily Bike Share Predictions - Preprocessed')
z = np.polyfit(y_test, predictions, 1)
p = np.poly1d(z)
plt.plot(y_test,p(y_test), color='magenta')
plt.show()
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-43.png)

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-44.png)

We\'ve now seen a number of common techniques used to train predictive
models for regression. In a real project, you\'d likely try a few more
algorithms, hyperparameters, and preprocessing transformations; but by
now you should have got the general idea. Let\'s explore how you can use
the trained model with new data.

### Use the Trained Model

First, let\'s save the model.

``` python
import joblib

# Save the model as a pickle file
filename = './models/bike-share.pkl'
joblib.dump(model, filename)
```

Now, we can load it whenever we need it, and use it to predict labels
for new data. This is often called *scoring* or *inferencing*.

``` python
# Load the model from the file
loaded_model = joblib.load(filename)

# Create a numpy array containing a new observation (for example tomorrow's seasonal and weather forecast information)
X_new = np.array([[1,1,0,3,1,1,0.226957,0.22927,0.436957,0.1869]]).astype('float64')
print ('New sample: {}'.format(list(X_new[0])))

# Use the model to predict tomorrow's rentals
result = loaded_model.predict(X_new)
print('Prediction: {:.0f} rentals'.format(np.round(result[0])))
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-45.png)

The model\'s **predict** method accepts an array of observations, so you
can use it to generate multiple predictions as a batch. For example,
suppose you have a weather forecast for the next five days; you could
use the model to predict bike rentals for each day based on the expected
weather conditions.

``` python
# An array of features based on five-day weather forecast
X_new = np.array([[0,1,1,0,0,1,0.344167,0.363625,0.805833,0.160446],
                  [0,1,0,1,0,1,0.363478,0.353739,0.696087,0.248539],
                  [0,1,0,2,0,1,0.196364,0.189405,0.437273,0.248309],
                  [0,1,0,3,0,1,0.2,0.212122,0.590435,0.160296],
                  [0,1,0,4,0,1,0.226957,0.22927,0.436957,0.1869]])

# Use the model to predict rentals
results = loaded_model.predict(X_new)
print('5-day rental predictions:')
for prediction in results:
    print(np.round(prediction))
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MLOps%20Lab/ML-Fundamentals/02-Regression/images/image-46.png)

## Conclusion  
This lab demonstrated the effectiveness of ensemble methods like Gradient Boosting and Random Forest for predicting bike rentals. Key takeaways:  
1. **Hyperparameter tuning** marginally improved performance.  
2. **Preprocessing** (scaling/encoding) is critical for handling mixed data types.  
3. **Model Deployment**: The tuned Gradient Boosting model was saved for future predictions.
