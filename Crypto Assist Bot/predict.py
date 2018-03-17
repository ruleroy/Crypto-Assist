from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from sklearn import linear_model, preprocessing, model_selection
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import statsmodels.api as sm

import scipy.stats

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from talib.abstract import *


def linearRegressionModel(pair, candles, depth):
    date, closep, highp, lowp, openp, volume = [], [], [], [], [], []
    ts_format = []

    #print(depth)
    lowest_ask = depth['asks'][0][0]
    for d in depth['asks']:
        if d[0] < lowest_ask:
            lowest_ask = d[0]

    for candle in candles:
        dt_ts = datetime.fromtimestamp(int(candle[0]) / 1e3 )
        ts_format.append(mdates.date2num(dt_ts))
        date.append(int(candle[0]))
        openp.append(float(candle[1]))
        highp.append(float(candle[2]))
        lowp.append(float(candle[3]))
        closep.append(float(candle[4]))
        volume.append(float(candle[5]))
    
    inputs = {
        'open': np.array(openp),
        'high': np.array(highp),
        'low': np.array(lowp),
        'close': np.array(closep),
        'volume': np.array(volume)
    }

    output = SMA(inputs, timeperiod=25)
    slowk, slowd = STOCH(inputs, 5, 3, 0, 3, 0)
    real = RSI(inputs, timeperiod=14)
    macd, macdsignal, macdhist = MACD(inputs, fastperiod=12, slowperiod=26, signalperiod=9)

    data = {
        'date': np.array(ts_format[50:]),
        'open': np.array(openp[50:]),
        'high': np.array(highp[50:]),
        'low': np.array(lowp[50:]),
        'close': np.array(closep[50:]),
        'volume': np.array(volume[50:]),
        'rsi': np.array(real[50:]),
        'macd': np.array(macd[50:]),
        'macdsignal': np.array(macdsignal[50:]),
        'macdhist': np.array(macdhist[50:]),
        'sma': np.array(output[50:])
    }

    #print(output[25:])
    #print(closep[25:])

    #linear regression model
    #future = datetime.datetime(2018, 4, 10)
    #print(future)
    #future = mdates.date2num(future)

    #forecasting
    df2 = pd.DataFrame.from_dict(data)
    df2.set_index('date', inplace=True, drop=False)

    df2 = df2[['close', 'rsi', 'macd', 'sma', 'volume', 'high', 'low', 'open']]
    forecast_col = 'close'
    df2.fillna(value=-99999, inplace=True)
    forecast_out = int(1)
    df2['prediction'] = df2[[forecast_col]].shift(-forecast_out)

    X2 = np.array(df2.drop(['prediction', 'close'], 1))
    X2 = preprocessing.scale(X2)

    X_forecast = X2[-forecast_out:]
    X2 = X2[:-forecast_out]

    df2.dropna(inplace=True)

    y2 = np.array(df2['prediction'])

    X2_train, X2_test, y2_train, y2_test = model_selection.train_test_split(X2, y2, test_size = 0.2)
    # Training
    reg_close = linear_model.LinearRegression(n_jobs=-1)
    reg_close.fit(X2_train, y2_train)

    reg_rsi = linear_model.LinearRegression(n_jobs=-1)
    reg_rsi.fit(X2_train, y2_train)

    reg_macd = linear_model.LinearRegression(n_jobs=-1)
    reg_macd.fit(X2_train, y2_train)

    reg_sma = linear_model.LinearRegression(n_jobs=-1)
    reg_sma.fit(X2_train, y2_train)

    last_close = df2[['close']]
    last_close = last_close[-1:]
    last_date = df2.index[-1].tolist()

    df2['forecast'] = np.nan
    predictions_arr = X_forecast

    for i in range(1):
        last_close_prediction = reg_close.predict(predictions_arr)
        last_rsi_prediction = reg_rsi.predict(predictions_arr)
        last_macd_prediction = reg_macd.predict(predictions_arr)
        last_sma_prediction = reg_sma.predict(predictions_arr)

        predictions_arr = np.array((last_close_prediction, last_rsi_prediction, last_macd_prediction, last_sma_prediction)).T
        
        next_date = mdates.num2date(last_date)
        next_date = next_date + timedelta(hours=4)
        next_date = mdates.date2num(next_date)
        last_date = next_date

        df2.loc[next_date] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, float(last_close_prediction)]

    close = df2['close'].iloc[-2]
    forecast = df2['forecast'].iloc[-1]
    increase = forecast - float(lowest_ask)
    increase = (increase / float(lowest_ask)) * 100
    
    if increase >= 0.5:
        print(f'\n{pair}')
        print(f'Lowest Ask: {lowest_ask}')
        print(f'Last close price: {close}')
        print(f'Forecasted price: {forecast}')
        print(f'% change: {increase}')