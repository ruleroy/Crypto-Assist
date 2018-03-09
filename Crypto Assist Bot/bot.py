import time
import sys, getopt
import datetime
import pandas as pd
import scipy.stats

from sklearn import linear_model
from sklearn.model_selection import train_test_split
import statsmodels.api as sm

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc
from matplotlib import style

import numpy as np
import talib
from talib.abstract import *

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
    account = client.get_account()
except:
    print("Connection Error")
    print("Please check your API_KEY and SECRET in key.txt and make sure it is correct.")
    sys.exit()

print("Connection Success")

def printLastMarketPrices():
    prices = client.get_all_tickers()
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
    print('     -p <period>     Delay to loop update in seconds')
    print('     -k <asset>      Klines')
    print('     -c <asset>      Check asset balance')
    print('     -b              Show current asset balances')
    print('     -l              Last market prices')

def candlestick_ohlc_black(*args,**kwargs):
    lines, patches = candlestick_ohlc(*args,**kwargs)
    for line, patch in zip(lines, patches):
        patch.set_edgecolor("k")
        patch.set_linewidth(0.72)
        patch.set_antialiased(False)
        line.set_color("k")
        line.set_zorder(0)

def linearRegressionModel(pair):
    candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_4HOUR)
    date, closep, highp, lowp, openp, volume = [], [], [], [], [], []
    ts_format = []

    for candle in candles:
        dt_ts = datetime.datetime.fromtimestamp(int(candle[0]) / 1e3 )
        #print(dt_ts)
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

    df = pd.DataFrame.from_dict(data)
    X = df[['date', 'rsi', 'macd', 'sma']].values
    Y = df['close'].values

    index = df['date'].values
    index = index[-50:]

    pred_x = X
    pred_x = pred_x[-50:]
    pred_y = df['close'].values
    pred_y = pred_y[-50:]
    #pred_x = df['close']

    pearR = scipy.stats.pearsonr(df['close'], df['date'])
    print(f"\nPearson Correlation: {pearR}")
    if pearR[1] < 0.05: 
        print("p-value is less than 5%, correlation between x and y is significant")
    else:
        print("p-value is greater than or equal to 5%, correlation between x and y is insignificant")


    #training set
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
    #print(f'{X_train.shape} , {y_train.shape}')
    #print(f'{X_test.shape} , {y_test.shape}')

    lm = linear_model.LinearRegression()
    model = lm.fit(X_train, Y_train)
    #print(X[0:500])
    predictions = lm.predict(pred_x)

    #to_predict = X[X[50,0]+1]
    #predictions2 = lm.predict(to_predict)
    #print(predictions2)

    print("\nAccuracy Score: ")
    accuracy = lm.score(pred_x, pred_y) * 100
    accuracy = '{:,.2f}'.format(accuracy)
    print(lm.score(pred_x, pred_y))
    print("\nsklearn predictions: ")
    print(predictions[-5:])
    print("\nTrue values: ")
    #print(y_test[-5:])
    print(pred_y[-5:])

    ax = plt.subplot2grid((1,1), (0,0))
    ax.plot(index, predictions, '--', label=f'Prediction ({accuracy}% accuracy)')
    ax.plot(index, pred_y, label='True value')

    #print(index.values)
    #ax.xaxis.set_ticks(np.arange(min(index), max(index)+1, 1.0))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))

    #plt.plot(predictions, '--', color='#EB3737', linewidth=2, label='Prediction')
    #plt.plot(pred_y, label='True', color='green')
    #plt.plot(predictions, '--', color='#EB3737', linewidth=2, label='Prediction')
    #plt.plot(Y_test, label='True', color='green', linewidth=2)
    plt.legend()
    #plt.plot(df['date'], df['close'])
    #plt.plot(df['date'], predictions)
    
    plt.title("BTC to USD - Model Accuracy")

    #plt.scatter(y_test, predictions)
    #plt.xlabel("True Values")
    #plt.ylabel("Predictions")
    
    #X = ts_format[25:100]
    #Y = closep[25:100]

    #test_data = ts_format[-74:]
    #test_data.append(future)

    #print(mdates.num2date(test_data[-1]))

    #linearModel = linear_model.LinearRegression()
    #model = linearModel.fit([X], [Y])
    #predictions = model.predict([test_data])

    #print("\nAccuracy Score: ")
    #print(linearModel.score([X], [Y]))
    #print("\nsklearn predictions: ")
    #print(predictions[:,-2:])

    #print(Y[-2:])

    #ax1 = plt.subplot2grid((1,1), (0,0))
    #ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    #ax1.set_title(pair)
    #ax1.grid(True)
    #ax1.scatter(real[25:], closep[25:])
    plt.show()


    
def printKlines(pair):
    candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_4HOUR)
    #print(candles)
    date, closep, highp, lowp, openp, volume = [], [], [], [], [], []
    gmt_time = []
    ts_format = []

    for candle in candles:
        #timestamp = time.strftime("%a %d %b %Y %H:%M:%S GMT", time.gmtime(candle[0] / 1000.0))
        dt_ts = datetime.datetime.fromtimestamp(int(candle[0]) / 1e3 )
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
    real = RSI(inputs, timeperiod=14)

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

    try:
        opts, args = getopt.getopt(argv,"blhp:c:k:m:",["period=", "asset=", "klines=", "model="])
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
        elif opt == '-b':
            showCurrentBalance = True
        elif opt in ("-k", "--klines"):
            kpair = arg
        elif opt in ("-m", "--model"):
            linearPair = arg


    while True:
        if(checkLastPrice):
            printLastMarketPrices()
        
        if(showCurrentBalance):
            printCurrentAssets()

        if(kpair):
            printKlines(kpair)

        if(linearPair):
            linearRegressionModel(linearPair)

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