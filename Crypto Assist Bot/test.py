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
from binance.client import Client

from pyti.stochrsi import stochrsi


def testMethod(client, pair, filter):

    candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_4HOUR, limit=100)
    depth = client.get_order_book(symbol=pair, limit=100)

    date, closep, highp, lowp, openp, volume = [], [], [], [], [], []
    ts_format = []

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

    #sma = SMA(inputs, timeperiod=14)
    slowk, slowd = STOCH(inputs, 5, 3, 0, 3, 0)
    real = RSI(inputs, timeperiod=14)
    macd, macdsignal, macdhist = MACD(inputs, fastperiod=12, slowperiod=26, signalperiod=9)
    fastk, fastd = STOCHRSI(inputs, timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=0)
    
    lowest_bid = depth['bids'][0][0]
    lowest_ask = depth['asks'][0][0]
    spread = float(lowest_ask) - float(lowest_bid)
    mid_price = (float(lowest_ask) + float(lowest_bid)) / 2

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


    def printOutput():
        print(f'\n{pair}')
        print(f"Stoch    K: {slowk[-1]}   D: {slowd[-1]}")
        print(f"Lowest ask: {lowest_ask}    Quantity: {depth['asks'][0][1]}")
        print(f"Lowest bid: {lowest_bid}    Quantity: {depth['bids'][0][1]}")
        print(f'Spread: {spread}')
        print(f"Mid price: {mid_price}")
        print(f"Weighted mid price: {weighted_spread}")
        #print(f"Limit order imbalance: {order_imbalance}")
        print("\n")
    '''
    if filter:
        if (slowk[-1] <= 20) or (slowk[-1] <= slowd[-1] and slowk[-1] <= 80):
            printOutput()
    else:
        printOutput()
    '''
    output = {
        'symbol': pair,
        'price': lowest_ask,
        'slowk': slowk[-1],
        'slowd': slowd[-1],
        'macd': '{0:.8f}'.format(macd[-1]),
        'macdsignal': '{0:.8f}'.format(macdsignal[-1])
    }
    return output

    #print(depth)
    '''
    print('\nBids')
    for d in depth['bids']:
        print(f'Price: {d[0]}   Quantity: {d[1]}')

    print('\nAsks')
    for d in depth['asks']:
        print(f'Price: {d[0]}   Quantity: {d[1]}')
    '''
    


    '''
    stochResults = []
    i = 0
    for n in real[15:]:
        if i == 0:
            inputs2 = {
                'high': [],
                'low': [],
                'close': np.array(closep)
            }
        else:
            inputs2 = {
                'high': [],
                'low': [],
                'close': np.array(closep[:-i])
            }

        rsi = RSI(inputs2, timeperiod=14)

        highest = max(rsi[15:])
        lowest = min(rsi[15:])
        stochrsi = 100 * ((rsi[-1] - lowest) / (highest - lowest))
        stochResults.append(stochrsi)
        print(stochrsi)
        i = i + 1
        print(i)
    
    print(stochResults)

    stoch = {
        'close': np.array(stochResults),
        'high': [],
        'low': []
    }

    fastk = SMA(stoch, timeperiod=3)

    stoch2 = {
        'close': np.array(fastk),
        'high': [],
        'low': []
    }
    fastd = SMA(stoch2, timeperiod=3)

    print(fastk)
    '''



    '''
    ax1 = plt.subplot2grid((6,1), (0,2))
    plt.xticks(rotation=25)
    plt.margins(0)
    ax2 = plt.subplot2grid((6,1), (3, 0))
    plt.xticks(rotation=25)
    plt.margins(0)

    ax1.plot(ts_format, inputs['close'])

    ax2.plot(slowk, color='blue')
    ax2.plot(slowd, color='orange')
    plt.show()
    '''
def printOutputs(ta):
    f = open('output.txt', 'w')
    f.write(f"\n{ta['symbol']}")
    f.write(f"Stoch    K: {ta['slowk']}   D: {ta['slowd']}")
    f.write(f"Macd     macd: {ta['macd']}  Signal: {ta['macdsignal']}")
    f.write(f"Last ask price: {ta['price']}")

    print(f"\n{ta['symbol']}")
    print(f"Stoch    K: {ta['slowk']}   D: {ta['slowd']}")
    print(f"Macd     macd: {ta['macd']}  Signal: {ta['macdsignal']}")
    print(f"Last ask price: {ta['price']}")