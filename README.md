# Weather_Forecasting_Using_LSTM
Analysis of historical data to forecast daily avg temperatures

## Overview
This project aims to forecast daily average temperatures in Denton, Texas, for the upcoming year using historical weather data. A Recurrent Neural Network (RNN) model with Long Short-Term Memory (LSTM) layers is employed to capture temporal dependencies in the data. The primary objective is to assess the effectiveness of deep learning models in time-series forecasting tasks involving meteorological indicators such as temperature, humidity, and wind speed.

## Research Objectives
**Forecasting:** Can daily average temperatures in Denton be accurately predicted using historical weather data through an RNN model?

**Feature Importance:** Which meteorological variables contribute most significantly to the prediction of average temperature?

**Model Evaluation:** How does the RNN model perform in terms of standard forecasting metrics?

## Dataset
**Source:** Visual Crossing Weather Database

**Time Range:** Historical daily data

**Location:** Denton, Texas

## Features:

Date

Average, Minimum, and Maximum Temperature

Humidity

Wind Speed

## Methodology
Data Preprocessing

Handling missing values

Normalization using Min-Max scaling

Sequence generation for time-series modeling

Model Development

Recurrent Neural Network (RNN) with LSTM layers

Sequential model structure

Hyperparameter tuning for optimization

Model Evaluation

## Metrics used:

Mean Squared Error (MSE)

Root Mean Squared Error (RMSE)

Mean Absolute Error (MAE)

## Key Findings
Temperature and humidity were the most influential predictors of daily average temperature.

The LSTM model demonstrated strong capability in capturing seasonal and temporal patterns in the data.

The model's predictions followed the historical trends with a low margin of error, indicating robustness.

## Future Enhancements
Incorporate additional meteorological features such as atmospheric pressure, precipitation, and solar radiation.

Compare LSTM with other sequence models such as GRUs or Transformer-based models.

Deploy the trained model through a web interface for interactive visualization and real-time forecasting.

## Technologies Used
Python (Pandas, NumPy)

TensorFlow and Keras (Deep Learning)

Scikit-learn (Preprocessing and Evaluation)

Jupyter Notebook (Exploratory Analysis and Modeling)

Matplotlib and Seaborn (Data Visualization)
