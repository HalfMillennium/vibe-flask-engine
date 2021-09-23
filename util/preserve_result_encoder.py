import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle

"""## Importing the dataset"""

dataset = pd.read_csv('data_imputed_binned.csv')
X = dataset.iloc[:,2:-1].values
y = dataset.iloc[:,-1].values

"""## Splitting the dataset into the Training set and Test set"""

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

"""## Feature Scaling"""

from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)
print(X)

"""# Encoding"""

from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
y_enc = encoder.fit_transform(y_train)
y_test = encoder.transform(y_test)

"""## Training the Logistic Regression model on the Training set"""

from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier()
classifier.fit(X_train, y_enc)
filename = 'result_encoder.sav'
pickle.dump(encoder, open(filename, 'wb'))
