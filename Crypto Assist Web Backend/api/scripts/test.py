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
    try:
        candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_4HOUR)
        depth = client.get_order_book(symbol=pair)
    except:
        return

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
    
    closep2 = [i * 10000 for i in closep]
    inputs = {
        'open': np.array(openp),
        'high': np.array(highp),
        'low': np.array(lowp),
        'close': np.array(closep),
        'volume': np.array(volume)
    }

    inputs2 = {
        'open': np.array(openp),
        'high': np.array(highp),
        'low': np.array(lowp),
        'close': np.array(closep2),
        'volume': np.array(volume)
    }

    #sma = SMA(inputs, timeperiod=14)
    slowk, slowd = STOCH(inputs, 5, 3, 0, 3, 0)
    rsi = RSI(inputs, timeperiod=14)
    macd, macdsignal, macdhist = MACD(inputs, fastperiod=12, slowperiod=26, signalperiod=9)
    fastk, fastd = STOCHRSI(inputs, timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=0)
    upperband, middleband, lowerband = BBANDS(inputs2, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
    upperband = [b / 10000 for b in upperband]
    middleband = [b / 10000 for b in middleband]
    lowerband = [b / 10000 for b in lowerband]
    
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

    output = {
        'symbol': pair,
        'price': lowest_ask,
        'slowk': slowk[-1],
        'slowd': slowd[-1],
        'macd': '{0:.8f}'.format(macd[-1]),
        'macdsignal': '{0:.8f}'.format(macdsignal[-1]),
        'upperband': '{0:.8f}'.format(upperband[-1]),
        'middleband': '{0:.8f}'.format(middleband[-1]),
        'lowerband': '{0:.8f}'.format(lowerband[-1]),
        'rsi': rsi[-1]
    }
    print(output)
    return output

def printOutputs(ta):

    print(f"\n{ta['symbol']}")
    print(f"RSI: {ta['rsi']}")
    print(f"STOCH    K: {ta['slowk']}   D: {ta['slowd']}")
    print(f"MACD     MACD: {ta['macd']}  SIGNAL: {ta['macdsignal']}")
    print(f"BBANDS   Upper: {ta['upperband']}   Middle: {ta['middleband']}   Lower: {ta['lowerband']}")
    print(f"Last ask price: {ta['price']}")