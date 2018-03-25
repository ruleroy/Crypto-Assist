import warnings
warnings.filterwarnings("ignore") 

import time
import sys, getopt
from datetime import datetime, timedelta
import pandas as pd
import scipy.stats

import random

from sklearn import linear_model, preprocessing, model_selection
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import statsmodels.api as sm

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc

from matplotlib import style

import numpy as np
import talib
from talib.abstract import *

import predict
import test
import trade
import backtest

style.use('ggplot')

from binance.client import Client

key_file = open("key.txt", "r")
lines = key_file.readlines()
lines[0] = lines[0].strip().split(':')
lines[1] = lines[1].strip().split(':')



if(not lines[0][1] or not lines[1][1]):
    print('API_KEY or SECRET in key.txt is empty')
    print('Please input your Binance API keys in key.txt file.')
    sys.exit()

api_key = lines[0][1]
api_secret = lines[1][1]
client = Client(api_key, api_secret)

try:
    client.ping()
except:
    print("Connection Error")
    print("Please check your API_KEY and SECRET in key.txt and make sure it is correct.")
    sys.exit()

print("Connection Success")

def printLastMarketPrices():
    prices = client.get_all_tickers()
    marketsymbols = []
    for symbol in prices:
        if symbol['symbol'][-3:] == 'BTC':
            marketsymbols.append(symbol['symbol'])

    print('Last Market Prices')
    for price in prices:
        print(price['symbol'] + ': ' + price['price'])
    print('\n')

def printCurrentAssets():
    info = client.get_account()
    print("Current Balances")
    for inf in info['balances']:
        if(float(inf['free']) > 0.00000000):
            print(inf['asset'] + ': ' + inf['free'])
    print('\n')

def printCurrentAssetBalance(pair):
    acc_asset = client.get_asset_balance(asset=pair)
    print("Current Asset Balance")
    print(acc_asset['asset'] + ': ' + acc_asset['free'] + '\n')
    
def help():
    print('bot.py')
    print('     -e                                      Current exchange rate limits')
    print('     -p <period>                             Delay to loop update in seconds')
    print('     -k <asset>                              Klines')
    print('     -c <asset>                              Check asset balance')
    print('     -w                                      Show current asset balances')
    print('     -l                                      Last market prices')
    print('     -f                                      Forecast market prices')
    print('     -t                                      Test method')
    print('     -b <asset_price_qty>                    Buy order')
    print('     -s <asset_price_qty>                    Sell order')
    print('     -x <asset>                              Cancel all orders for pair')
    print('     -r <asset_bal crypto_bal usd>           Run backtest')

def candlestick_ohlc_black(*args,**kwargs):
    lines, patches = candlestick_ohlc(*args,**kwargs)
    for line, patch in zip(lines, patches):
        patch.set_edgecolor("k")
        patch.set_linewidth(0.72)
        patch.set_antialiased(False)
        line.set_color("k")
        line.set_zorder(0)
    
def printKlines(pair):
    candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_30MINUTE)
    #print(candles)
    date, closep, highp, lowp, openp, volume = [], [], [], [], [], []
    gmt_time = []
    ts_format = []

    for candle in candles:
        #timestamp = time.strftime("%a %d %b %Y %H:%M:%S GMT", time.gmtime(candle[0] / 1000.0))
        dt_ts = datetime.fromtimestamp(int(candle[0]) / 1e3 )
        ts_format.append(mdates.date2num(dt_ts))
        timestamp = time.strftime("%b %d %H:%M", time.gmtime(candle[0] / 1000.0))
        gmt_time.append(timestamp)
        date.append(int(candle[0]))
        openp.append(float(candle[1]))
        highp.append(float(candle[2]))
        lowp.append(float(candle[3]))
        closep.append(float(candle[4]))
        volume.append(float(candle[5]))

    x = 0
    y = len(date)
    ohlc = []
    while x<y:
        append_me = ts_format[x], openp[x], highp[x], lowp[x], closep[x], volume[x]
        ohlc.append(append_me)
        x+=1

    inputs = {
        'open': np.array(openp),
        'high': np.array(highp),
        'low': np.array(lowp),
        'close': np.array(closep),
        'volume': np.array(volume)
    }

    output = SMA(inputs, timeperiod=25)
    slowk, slowd = STOCH(inputs, 5, 3, 0, 3, 0)
    real = RSI(inputs, timeperiod=7)
    print(real[-1])


    macd, macdsignal, macdhist = MACD(inputs, fastperiod=12, slowperiod=26, signalperiod=9)
    #print(real)

    ax1 = plt.subplot2grid((6,1), (0,2))
    plt.xticks(rotation=25)
    plt.margins(0)
    ax2 = plt.subplot2grid((6,1), (3, 0))
    plt.xticks(rotation=25)
    plt.margins(0)
    ax3 = plt.subplot2grid((6,1), (5, 0))
    plt.xticks(rotation=25)
    plt.margins(0)
    
    candlestick_ohlc(ax1, ohlc, width=0.1, colorup='#77d879', colordown='#db3f3f')
    #candlestick_ohlc_black(ax1, ohlc, width=1)
    #ax1.plot(date, closep)

    #ax1.set_xticklabels(gmt_time)

    #time.strftime("%b %d %H:%M", time.gmtime(candle[0] / 1000.0))
    xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax1.xaxis.set_major_formatter(xfmt)
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(12))
    #ax1.xaxis.pan(5)

    ax1.set_title(pair)
    ax1.grid(True)
    ax1.set_ylabel('Price')

    ax2.plot(ts_format, macd)
    ax2.plot(ts_format, macdsignal)
    ax2.plot(ts_format, macdhist)
    ax2.xaxis.set_major_formatter(xfmt)
    ax2.set_title('MACD')

    ax3.plot(ts_format, real)
    ax3.xaxis.set_major_formatter(xfmt)
    ax3.set_title('RSI')

    plt.show()

    
def main(argv):
    period = 0
    pair = ''
    kpair = ''
    linearPair = ''
    checkLastPrice = False
    showCurrentBalance = False
    forecast = False
    testSymbol = ''
    buyParams = ''
    sellParams = ''
    cancelParams = ''
    predictPair = ''
    backtestParams = ''

    try:
        opts, args = getopt.getopt(argv,"efwlhp:c:k:m:t:b:s:x:a:r:",["period=", "asset=", "klines=", "model=", "test=", "buy=", "sell=", "cancel=", "predict=", "btest="])
    except getopt.GetoptError:
        help()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-p", "--period"):
            period = arg
        elif opt in ("-c", "--asset"):
            pair = arg
        elif opt == '-h':
            help()
        elif opt == '-l':
            checkLastPrice = True
        elif opt == '-w':
            showCurrentBalance = True
        elif opt in ("-k", "--klines"):
            kpair = arg
        elif opt in ("-m", "--model"):
            linearPair = arg
        elif opt == '-f':
            forecast = True
        elif opt == '-e':
            exchange_info = client.get_exchange_info()
            rate_limits = exchange_info['rateLimits']
            for r in rate_limits:
                print(f"{r['rateLimitType']} per {r['interval']}: {r['limit']}")
        elif opt in ("-t", "--test"):
            testSymbol = arg
        elif opt in ("-b", "--buy"):
            buyParams = arg
        elif opt in ("-s", "--sell"):
            sellParams = arg
        elif opt in ("-x", "--cancel"):
            cancelParams = arg
        elif opt in ("-a", "--predict"):
            predictPair = arg
        elif opt in ("-r", "--btest"):
            backtestParams = arg
            

    while True:
        if(backtestParams):
            params_arr = backtestParams.split("_")
            bt = backtest.backtest(client, params_arr[0], params_arr[1], params_arr[2])
            bt.testModel()

        if(cancelParams):
            trade.cancelAllOrders(client, cancelParams)

        if(sellParams):
            params_arr = sellParams.split("_")
            print(params_arr)
            trade.sellOrder(client, params_arr[0], params_arr[1], params_arr[2])

        if(buyParams):
            params_arr = buyParams.split("_")
            print(params_arr)
            trade.buyOrder(client, params_arr[0], params_arr[1], params_arr[2])

        if(testSymbol):
            print(datetime.now())
            t0 = time.time()
            if(testSymbol == 'ALL') or (testSymbol == 'all'):
                filename1 = datetime.now().strftime("%Y%m%d-%H%M%S")
                #open('output.txt', 'w').close()
                sys.stdout = open(f'output/{filename1}.txt', 'w')

                print(datetime.now())
                prices = client.get_all_tickers()
                marketsymbols = []
                ta = []
                for symbol in prices:
                    if symbol['symbol'][-3:] == 'BTC':
                        marketsymbols.append(symbol['symbol'])
        
                for symbol in marketsymbols:
                    ta.append(test.testMethod(client, symbol, True))

                print("Stoch K lower than 20")
                for t in ta:
                    if(t['slowk'] <= 20):
                        test.printOutputs(t)

                print("\n-------------------------------")
                print("Stoch K lower than D")
                for t in ta:
                    if(t['slowk'] <= 80 and t['slowk'] <= t['slowd']):
                        if(t['macd'] <= t['macdsignal']):
                            test.printOutputs(t)
                print('\n')
                sys.stdout.close()
                sys.stdout = sys.__stdout__
                print(f'Results displayed in output/{filename1}.txt')
            else:
                t0 = time.time()
                test.printOutputs(test.testMethod(client, testSymbol, False))
                t1 = time.time()
                total = t1-t0
                #print(total)
            t1 = time.time()
            total = t1-t0
            print(f"Finished in: {total}")
            

        if(checkLastPrice):
            printLastMarketPrices()
        
        if(showCurrentBalance):
            printCurrentAssets()

        if(kpair):
            printKlines(kpair)

        if(forecast):
            prices = client.get_all_tickers()
            marketsymbols = []
            for symbol in prices:
                if symbol['symbol'][-3:] == 'BTC':
                    marketsymbols.append(symbol['symbol'])
        
            for symbol in marketsymbols:
                candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
                depth = client.get_order_book(symbol=symbol)
                predict.linearRegressionModel(symbol, candles, depth)

        if(predictPair):
            candles = client.get_klines(symbol=predictPair, interval=Client.KLINE_INTERVAL_4HOUR, limit=100)
            depth = client.get_order_book(symbol=predictPair)
            predict.linearRegressionModel(predictPair, candles, depth)

        if(pair):
            printCurrentAssetBalance(pair)
            #
            #printCurrentAssets(info)
            #printLastPrices(prices)

        if(int(period) > 0):
            time.sleep(int(period))
        else:
            sys.exit()
            

if __name__ == "__main__":
    main(sys.argv[1:])