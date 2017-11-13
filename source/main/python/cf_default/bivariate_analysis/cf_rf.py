import numpy as np
import os.path
import time
import re
from pickle import load
from pickle import dump
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error


"""
The "canonical" way to do time-series cross-validation is to roll through the dataset. Basically, the training set
should not contain information that occurs after the test set, hence k-fold cross-validation is not appropiate.

In other words: When the data are not independent, cross-validation becomes more difficult as leaving out an observation
does not remove all the associated information due to the correlations with other observations. For time series 
forecasting, a cross-validation statistic may be obtained as follows:

1. Fit the model to the data y_1,...,y_t and let y^_t+1 denote the forecast of the next observation. Then compute the 
error (e_t+1 = y_t+1 - y^_t+1) for the forecast observation.
2. Repeat step 1 for t=m,..., T-1 where m is the minimmum number of observations needed for fitting the model and T is
the length of the time serie dataset. 
3. Compute the MAE/MSE from e_m+1,...,e*_T.

In our case: m = 1000, T = 1500
script running time:  440 seconds if no_estimators = 1  
script running time: 3438 seconds if no_estimators = 10 (default)

"""


#  Set seed for pseudorandom number generator. This allows us to reproduce the results from our script.
np.random.seed(42)  # 42:The answer to life, the universe and everything.

# Load data into dataframe
file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                        'resources/Data/bivariate_analysis')
files_list = os.listdir(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                        'resources/Data/bivariate_analysis'))

start_time = time.time()
mae_rf_vec = np.full(200, np.nan)  # Initialisation vector containing MAE for all window sizes
k = 0
for filename in files_list:
    i = [int(s) for s in re.findall(r'\d+', filename)]
    k += 1
    print(k)
    data_cor_true = load(open(file_path + '/' + filename, 'rb'))
    # Drop first m_max = 200 rows to ensure same training and test set for all values of m
    data_cor_true.drop(data_cor_true.head(200).index, inplace=True)
    data_cor_true.reset_index(drop=True, inplace=True)
    # Separate data into feature and response components
    X = data_cor_true.iloc[:, 0:-1]  # feature matrix
    y = data_cor_true.iloc[:, -1]    # response vector

    t_start = 1000
    T = len(y)
    y_hat_rf = np.full(T - t_start, np.nan)    # Initialisation vector containing y_hat_t for t = m+1,...,T
    rf = RandomForestRegressor()  # Default settings (for now)
    dt = DecisionTreeRegressor()

    for j, t in enumerate(range(t_start, T)):
        X_train = X.iloc[0:t, :]
        y_train = y.iloc[0:t]
        x_test = X.iloc[t]  # This is in fact x_t+1
        y_test = y.iloc[t]  # This is in fact y_t+1
        y_hat = rf.fit(X_train, y_train).predict(x_test.reshape(-1, 1))
        y_hat_rf[j] = y_hat

    mae_rf_vec[i] = mean_absolute_error(y[t_start:], y_hat_rf)

path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                        ('resources/Data/mae_rf_true_corr_default.pkl'))
dump(mae_rf_vec, open(path, 'wb'))

print(mae_rf_vec)
print("%s: %f" % ('Execution time script', (time.time() - start_time)))

plt.plot(mae_rf_vec, label='RF')
plt.title('MAE for Random Forest with true correlations')
plt.xlabel('window length')
plt.ylabel('MAE')
plt.legend(loc='upper right', fancybox=True)
plt.show()

