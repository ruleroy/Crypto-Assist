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


def testMethod(pair, candles, depth):
    date, closep, highp, lowp, openp, volume = [], [], [], [], [], []
    ts_format = []

    #print(depth)
    '''
    print('\nBids')
    for d in depth['bids']:
        print(f'Price: {d[0]}   Quantity: {d[1]}')

    print('\nAsks')
    for d in depth['asks']:
        print(f'Price: {d[0]}   Quantity: {d[1]}')
    '''

    lowest_bid = depth['bids'][0][0]
    print(f"Lowest bid: {lowest_bid}    Quantity: {depth['bids'][0][1]}")

    lowest_ask = depth['asks'][0][0]
    print(f"Lowest ask: {lowest_ask}    Quantity: {depth['asks'][0][1]}")

    spread = float(lowest_ask) - float(lowest_bid)
    print(f'Spread: {spread}')
    
    mid_price = (float(lowest_ask) + float(lowest_bid)) / 2
    print(f"Mid price: {mid_price}")

    weighted_spread = float(0)
    order_imbalance = []
    for i in range(8):
        bid_price = float(depth['bids'][i][0])
        bid_qty = float(depth['bids'][i][1])

        ask_price = float(depth['asks'][i][0])
        ask_qty = float(depth['asks'][i][1])

        weighted_spread = ((bid_qty * ask_price) + (ask_qty * bid_price)) / (ask_qty + bid_qty)
        weighted_spread2 = (bid_qty - ask_qty) / (bid_qty + ask_qty)

        order_imbalance.append(weighted_spread2)

    
    print(f"Weighted mid price: {weighted_spread}")
    print(f"Limit order imbalance: {order_imbalance}")
    print("\n")

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

    plt.plot(slowk)
    plt.plot(slowd)
    #plt.show()