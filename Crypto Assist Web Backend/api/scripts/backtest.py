import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc
from matplotlib import style

import time
import sys, getopt
from datetime import datetime, timedelta
import pandas as pd
import scipy.stats

import numpy as np
import talib
from talib.abstract import *
from binance.client import Client

import predict
import test
import trade

style.use('ggplot')

class backtest(object):
    balance1 = float(0)
    balance2 = float(0)
    symbol = ''
    client = object
    trades = []
    x = []
    y = []

    def __init__(self, client, symbol, balance1, balance2):
        self.client = client
        self.balance1 = balance1
        self.balance2 = balance2
        self.symbol = symbol

    def testModel(self):
        candles = self.client.get_klines(symbol=self.symbol, interval=Client.KLINE_INTERVAL_1MINUTE)
        depth = self.client.get_order_book(symbol=self.symbol)
        print(f"Crypto Balance: {self.balance1}")
        print(f"USD Balance: {self.balance2}")
        for i in range(10):
            self.buy(8000.00, 1.00)
            self.sell(8000.00, 2.00)
        self.plotBalances()

    def buy(self, price, qty):
        if float(self.balance2) >= (float(price) * float(qty)):
            self.balance2 = float(self.balance2) - (price * qty)
            self.balance1 = float(self.balance1) + qty
        else:
            print("Not enough balance to place buy order.")
        print(f"Crypto Balance: {self.balance1}")
        print(f"USD Balance: {self.balance2}")
        self.x.append(self.balance2)
        self.y.append(self.balance1)

    def sell(self, price, qty):
        if float(self.balance1) >= float(qty):
            self.balance1 = float(self.balance1) - qty
            self.balance2 = float(self.balance2) + (qty * price)
        else:
            print("Not enough balance to place sell order.")
        print(f"Crypto Balance: {self.balance1}")
        print(f"USD Balance: {self.balance2}")
        self.x.append(self.balance2)
        self.y.append(self.balance1)

    def plotBalances(self):
        print(self.y)
        plt.plot(self.y)
        plt.show()

