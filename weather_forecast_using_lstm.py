# -*- coding: utf-8 -*-
"""Weather_Forecast_Using_LSTM.ipynb

Original file is located at
    https://colab.research.google.com/drive/1flMi_E714SnjMZ3b5psUhJ64T_1Mgeo0
"""

import pandas as pd
import matplotlib.pyplot as plt

# Read the excel dataset
!pip install openpyxl

def denton_data(): # Defining the function
  denton_data = pd.read_excel('denton_data.xlsx', engine='openpyxl') # Read the data
  return denton_data # return the function

# Define variable for the function
denton_data = denton_data()
denton_data.head(5)

# Get the information and dtypes in the data
denton_data.info()

# Check for missing values
denton_data.isnull().sum()

# Drop the categorical columns.
columns_to_drop = ['name', 'preciptype', 'sunrise', 'sunset', 'conditions', 'description', 'icon', 'stations']
denton_data.drop(columns=columns_to_drop, inplace=True)
denton_data.info()

# Check for missing values
denton_data.isnull().sum()

# Set datetime
denton_data['date_time']=pd.to_datetime(denton_data['datetime'])
denton_data.set_index('date_time', inplace=True) # Set date_time column as index
denton_data.head()

# Drop datetime column
denton_data.drop('datetime', axis=1, inplace=True)
denton_data.head()

# Get the descriptive statistics
descriptive_stats = denton_data.describe()
descriptive_stats

# Create a Correlation Matrix
import seaborn as sns

plt.figure(figsize=(18, 12))
correlation_matrix = denton_data.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, fmt='.2f')
plt.title('Correlation Matrix')
plt.show()

# Visualize the temp over time
plt.figure(figsize=(12, 6))
plt.plot(denton_data.index, denton_data['temp'], label='Temperature', color='blue',)
plt.title('Temperature Over Time')
plt.xlabel('Date')
plt.ylabel('Temperature')
plt.legend()
plt.show()

# Visualize the frequency of temp
plt.figure(figsize=(12, 8))
plt.hist(denton_data['temp'], bins=20, color = 'skyblue', edgecolor='black')
plt.title('Frequency of Temperature Over Time')
plt.xlabel('Temperature')
plt.ylabel('Frequency')
plt.show()

# Visualize seasonal trend of temp by month
denton_data['Month'] = denton_data.index.month
monthly_avg = denton_data.groupby('Month')['temp'].mean()
plt.figure(figsize=(8, 6))
monthly_avg.plot(kind='bar', color='green')
plt.title('Seasonal Trend of Temperature by Month')
plt.xlabel('Month')
plt.ylabel('Average Temperature')
plt.xticks(rotation=0)
plt.show()

plt.figure(figsize=(12, 8))
sns.pairplot(denton_data[['temp', 'humidity', 'windspeed']], diag_kind='kde')
plt.suptitle("Pairwise Relationships Between Variables", y=1.02)
plt.show()

# Drop the temporary 'month' column
denton_data.drop(columns=['Month'], inplace=True)

# Forecast of Denton's Daily Average Temperatures (Next 1 Year)

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error, mean_absolute_error
from math import sqrt

# Parse date
data = denton_data.copy() # Make a copy of denton_data to avoid changing the original DataFrame.
data = data.sort_index() # Sort values by index, which is the 'date_time'.
data['Date'] = data.index # Rename index to 'Date' and add it as a column for convenience
data.set_index('Date', inplace=True)

data = data[['temp', 'humidity', 'windspeed']]

# Add dayofyear for seasonal encoding
data['dayofyear'] = data.index.dayofyear
data['sin_doy'] = np.sin(2 * np.pi * data['dayofyear'] / 365)
data['cos_doy'] = np.cos(2 * np.pi * data['dayofyear'] / 365)
data.drop(columns='dayofyear', inplace=True)

# Scale data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

# 2. Create sequences for LSTM
def create_sequences(dataset, seq_len):
    x, y = [], []
    for i in range(len(dataset) - seq_len):
        x.append(dataset[i:i+seq_len])
        y.append(dataset[i+seq_len][0])  # only temp as target
    return np.array(x), np.array(y)

seq_len = 30
X, y = create_sequences(scaled_data, seq_len)

# Train-test split
split_idx = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

# 3. Build the LSTM model
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(32))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse')

# Train
history = model.fit(X_train, y_train, epochs=30, batch_size=32, validation_data=(X_test, y_test), verbose=1)

# 4. Evaluate performance
y_pred = model.predict(X_test)
actual = y_test
predicted = y_pred.flatten()

# Rescale
temp_index = list(data.columns).index('temp')
temp_min = scaler.data_min_[temp_index]
temp_max = scaler.data_max_[temp_index]

actual_rescaled = actual * (temp_max - temp_min) + temp_min
predicted_rescaled = predicted * (temp_max - temp_min) + temp_min

mse = mean_squared_error(actual_rescaled, predicted_rescaled)
rmse = sqrt(mse)
mae = mean_absolute_error(actual_rescaled, predicted_rescaled)
print(f"MSE: {mse:.2f}, RMSE: {rmse:.2f}, MAE: {mae:.2f}")

# 5. Recursive Forecast for 365 days
forecast_days = 365
last_seq = scaled_data[-seq_len:].copy()
forecast = []

for i in range(forecast_days):
    input_seq = np.expand_dims(last_seq, axis=0)
    next_temp_scaled = model.predict(input_seq, verbose=0)[0, 0]

    next_dayofyear = ((data.index[-1] + pd.Timedelta(days=i+1)).dayofyear)
    sin_doy = np.sin(2 * np.pi * next_dayofyear / 365)
    cos_doy = np.cos(2 * np.pi * next_dayofyear / 365)

    # Use average humidity & wind speed by day of year (seasonal)
    past_doy = data.copy()
    past_doy['doy'] = past_doy.index.dayofyear
    avg_features = past_doy.groupby('doy')[['humidity', 'windspeed']].mean()
    avg_humidity, avg_wind = avg_features.loc[next_dayofyear]

    # Rescale all features
    next_point = scaler.transform([[0, avg_humidity, avg_wind, sin_doy, cos_doy]])[0]
    next_point[0] = next_temp_scaled  # update predicted temp only

    forecast.append(next_point)
    last_seq = np.vstack((last_seq[1:], next_point))

# Inverse transform forecast temps
forecast_scaled = np.array(forecast)
forecast_temp_scaled = forecast_scaled[:, 0]
forecast_temp = forecast_temp_scaled * (temp_max - temp_min) + temp_min

# 6. Plot forecast
forecast_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=forecast_days)
recent_dates = data.index[-120:]
recent_real_temp = data['temp'][-120:]

plt.figure(figsize=(14, 6))
plt.plot(recent_dates, recent_real_temp, label='Recent Real Temp')
plt.plot(forecast_dates, forecast_temp, label='Forecast', color='orange')
plt.title("Forecast of Denton's Daily Average Temperature (Next 1 Year)")
plt.xlabel("Date")
plt.ylabel("Temperature (F)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Save evaluation for RQ3
evaluation = {
    'MSE': mse,
    'RMSE': rmse,
    'MAE': mae
}
print("Evaluation:", evaluation)

import numpy as np
from sklearn.metrics import mean_squared_error
import copy

def permutation_feature_importance(model, X_test, y_test, baseline_preds, scaler_y, feature_names):
    """
    Calculates permutation feature importance for a trained LSTM model.
    """
    importances = []
    baseline_rmse = mean_squared_error(y_test, baseline_preds, squared=False)

    for i in range(X_test.shape[2]):
        X_permuted = copy.deepcopy(X_test)
        np.random.shuffle(X_permuted[:, :, i])  # Shuffle the i-th feature across all sequences

        preds_permuted = model.predict(X_permuted, verbose=0)
        preds_permuted = scaler_y.inverse_transform(preds_permuted)
        y_test_inv = scaler_y.inverse_transform(y_test)

        rmse_permuted = mean_squared_error(y_test_inv, preds_permuted, squared=False)
        importance = rmse_permuted - baseline_rmse
        importances.append(importance)

    # Pair feature names with importance scores
    feature_importance = dict(zip(feature_names, importances))
    return feature_importance

from sklearn.metrics import mean_squared_error
import copy

def permutation_feature_importance(model, X_test, y_test, baseline_preds, scaler_y, feature_names):
    """
    Calculates permutation feature importance for a trained LSTM model.
    """
    importances = []
    # Calculate baseline RMSE without 'squared' argument
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_preds))

    for i in range(X_test.shape[2]):
        X_permuted = copy.deepcopy(X_test)
        np.random.shuffle(X_permuted[:, :, i])  # Shuffle the i-th feature across all sequences

        preds_permuted = model.predict(X_permuted, verbose=0)
        preds_permuted = scaler_y.inverse_transform(preds_permuted)
        # Reshape y_test before inverse transforming
        y_test_inv = scaler_y.inverse_transform(y_test.reshape(-1, 1)) # Reshape y_test to a 2D array

        # Calculate RMSE without 'squared' argument
        rmse_permuted = np.sqrt(mean_squared_error(y_test_inv, preds_permuted))
        importance = rmse_permuted - baseline_rmse
        importances.append(importance)

    # Pair feature names with importance scores
    feature_importance = dict(zip(feature_names, importances))
    return feature_importance

baseline_preds = model.predict(X_test, verbose=0)

scaler_y = MinMaxScaler()
# Fit using the training data.
scaler_y.fit(y_train.reshape(-1,1))

# Calculate feature importance scores using the permutation function
importance_scores = permutation_feature_importance(
    model, X_test, y_test, baseline_preds, scaler_y, data.columns  # Use data.columns for feature names
)

# Plot the importance scores
plt.figure(figsize=(8, 4))
plt.bar(importance_scores.keys(), importance_scores.values(), color='skyblue')
plt.ylabel("Increase in RMSE after shuffling")
plt.title("Feature Importance (Permutation)")
plt.show()

