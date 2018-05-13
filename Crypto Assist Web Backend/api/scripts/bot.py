import warnings
warnings.filterwarnings("ignore") 

import time
import sys, getopt
from datetime import datetime, timedelta
import pandas as pd
import scipy.stats
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Normalizer

import random
import os, errno

from sklearn import linear_model, preprocessing, model_selection
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import statsmodels.api as sm
import statsmodels.formula.api as smf

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc
import seaborn as sns

from matplotlib import style

import numpy as np
import talib
from talib.abstract import *

import predict
import test
import trade
import backtest
import json
import requests

style.use('ggplot')

from binance.client import Client

key_file = open("./key.txt", "r")
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
    price = client.get_all_tickers()
    #print(price)

    curr_btc_price = 0.0
    prices = {}
    for pri in price:
        if pri['symbol'][-3:] == 'BTC':
            prices[pri['symbol'][:-3]] = float(pri['price'])
        if pri['symbol'] == 'BTCUSDT':
            curr_btc_price = float(pri['price'])
    data_str = json.dumps(prices)
    print(data_str)

    print("Current Balances")
    balance = {}
    for inf in info['balances']:
        balance[inf['asset']] = inf['free']
        #print(inf['asset'] + ': ' + inf['free'])
    #print('\n')
    #print(balance)
    data_str2 = json.dumps(balance)
    print(data_str2)

    total_btc_bal = sum(prices[k]*float(balance[k]) for k in prices)
    total_btc_bal += float(balance['BTC'])

    print("{0:.8f}".format(total_btc_bal)) #Portfolio Value (BTC)
    print("{0:.2f}".format(total_btc_bal*curr_btc_price)) #Portfolio Value (USD)
    print("{0:.2f}".format(curr_btc_price)) #Current BTC Price

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

def returnCandles(pair):
    candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_4HOUR, limit=30)
    date, closep, highp, lowp, openp, volume = [], [], [], [], [], []
    ts_format = []
    gmt_time = []

    for candle in candles:
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

    inputs = {
        "date": gmt_time,
        "close": closep
    }
    data_str = json.dumps(inputs)
    print(data_str)

def analyzePair(pair):
    formattedPair = pair
    if(pair == 'BTC'):
        formattedPair += 'USDT'
    else:
        if(pair == 'BCH'):
            formattedPair = 'BCC'
        if(pair == 'MIOTA'):
            formattedPair = 'IOTA'
        formattedPair += 'BTC'
    
    candles = client.get_klines(symbol=formattedPair, interval=Client.KLINE_INTERVAL_4HOUR, limit=500)
    btcCandles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_4HOUR, limit=500)
    
    close, date, volume, gmt_time = [], [], [], []
    for c in candles:
        dt_ts = datetime.fromtimestamp(int(c[0]) / 1e3 )
        date.append(mdates.date2num(dt_ts))
        timestamp = time.strftime("%b %d %H:%M", time.gmtime(c[0] / 1000.0))
        gmt_time.append(timestamp)
        if(formattedPair == "BTCUSDT"):
            close.append(int("{0:.0f}".format(round(float(c[4]),2))))
        else:
            close.append(float(c[4]))
        volume.append(float(c[5]))
    
    bclose, bdate, bvolume, bgmt_time = [], [], [], []
    for c in btcCandles:
        dt_ts = datetime.fromtimestamp(int(c[0]) / 1e3 )
        bdate.append(mdates.date2num(dt_ts))
        timestamp = time.strftime("%b %d %H:%M", time.gmtime(c[0] / 1000.0))
        bgmt_time.append(timestamp)
        if(formattedPair == "BTCUSDT"):
            bclose.append(int("{0:.0f}".format(round(float(c[4]),2))))
        else:
            bclose.append(float(c[4]))
        bvolume.append(float(c[5]))

    Y = close[-100:]
    Y_total = [c for c in close]
    X = [i for i in range(100)]
    X_total = [i for i in range(len(close))]
    Y = np.array(Y)
    X = np.array(X)
    Y_total = np.array(Y_total)
    X_total = np.array(X_total)
    vol = np.array(volume)

    bprice = np.array(bclose)

    names = ['date', 'volume', 'price', 'btc_price']
    data = pd.DataFrame({'date':X_total, 'volume': vol, 'price':Y_total, 'btc_price':bprice})
    normalized = Normalizer().fit_transform(data)
    df_normalized = pd.DataFrame(normalized, columns=names)

    X2 = np.array(data)
    X2 = preprocessing.scale(X2)
    y2 = np.array(data['price'])
    forecast_out = 30
    X_train = X2[:-2 * forecast_out]
    y_train = y2[forecast_out:-forecast_out]
    X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2)

    clf = linear_model.LinearRegression()
    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)
    print(float("{0:.2f}".format(round(float(accuracy*100),2))))

    # predict last 30 days
    X_eval30 = X2[-2 * forecast_out:-forecast_out]
    y_eval_forecast = clf.predict(X_eval30)

    data['prediction'] = np.nan
    data['prediction'][-forecast_out:] = y_eval_forecast
    
    # predict 30 days into future
    X_pred30 = X2[-forecast_out:]
    y_pred_forecast = clf.predict(X_pred30)

    last_date = data['date'].iloc[-1]
    dt = last_date

    #print(data)

    for i in y_pred_forecast:
        dt += 1
        data.loc[dt] = [np.nan for _ in range(len(data.columns) - 1)] + [i]
    
    #print(data[-forecast_out:])

    fig, ax = plt.subplots(1,1)

    fit = np.polyfit(X, Y, deg=1)
    plt.title("BTC price in past 100 4 hr candles")
    plt.scatter(X, Y, color='blue')
    plt.plot(X, fit[0] * X + fit[1])
    
    linearY = []
    for i in range(len(Y)):
        linear = fit[0] * X[i] + fit[1]
        #linear = int("{0:.8f}".format(round(float(linear),2)))
        linearY.append(linear)

    data.hist("price")
    #plt.margins(0.1)
    #plt.locator_params(nbins=10)
    
    #z = np.polyfit(x,y,1)
    #z = np.polyfit(x, y, 1)
    #p = np.poly1d(z)
    #ax.plot(date,p(date),"r--")

    displayArr = []
    for i in range(len(Y)):
        obj = {
            'time': float(X[i]),
            'price': float(Y[i]),
            'linearY': float("{0:.8f}".format(round(float(linearY[i]),8)))
        }
        displayArr.append(obj)
    for i in range(len(Y_total)):
        obj = {
            'rtime': float(X_total[i]),
            'rprice': float(Y_total[i])
        }
        displayArr.append(obj)
    for i in range(len(data) - forecast_out, len(data)):
        obj = {
            'ptime': float(i),
            'prediction': float("{0:.8f}".format(round(float(data.iloc[i]['prediction']),8)))
        }
        displayArr.append(obj)
    data_str = json.dumps(displayArr)
    print(data_str)
    
    #plt.show()

    
def printKlines(email):
    api_url_base = 'https://api.coinmarketcap.com/v2/ticker/?limit=10'
    headers = {'Content-Type': 'application/json'}

    response = requests.get(api_url_base, headers=headers)

    jsonData = {}

    if response.status_code == 200:
        jsonData = json.loads(response.content.decode('utf-8'))
    else:
        sys.exit()
    
    top10 = []

    for coin in jsonData['data']:
        if (jsonData['data'][coin]['symbol'] == "BCH"):
            top10.append("BCC")
        elif (jsonData['data'][coin]['symbol'] == "MIOTA"):
            top10.append("IOTA")
        else:
            top10.append(jsonData['data'][coin]['symbol'])

    print(top10)
    pair = []
    for t in top10:
        if(t == "BTC"):
            pair.append(t + "USDT")
        else:
            pair.append(t + "BTC")

    print(pair)

    candles = {}
    i = 0
    for t in top10:
        candles[t] = client.get_klines(symbol=pair[i], interval=Client.KLINE_INTERVAL_4HOUR, limit=100)
        i += 1

    #candles = client.get_klines(symbol=pair, interval=Client.KLINE_INTERVAL_30MINUTE)
    '''
    candles = {
        'BTC': client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_4HOUR, limit=100),
        'ETH': client.get_klines(symbol='ETHBTC', interval=Client.KLINE_INTERVAL_4HOUR, limit = 100),
        'XRP': client.get_klines(symbol='XRPBTC', interval=Client.KLINE_INTERVAL_4HOUR, limit = 100),
        'BCC': client.get_klines(symbol='BCCBTC', interval=Client.KLINE_INTERVAL_4HOUR, limit = 100),
        'EOS': client.get_klines(symbol='EOSBTC', interval=Client.KLINE_INTERVAL_4HOUR, limit = 100),
        'ADA': client.get_klines(symbol='ADABTC', interval=Client.KLINE_INTERVAL_4HOUR, limit = 100),
        'LTC': client.get_klines(symbol='LTCBTC', interval=Client.KLINE_INTERVAL_4HOUR, limit = 100),
        'XLM': client.get_klines(symbol='XLMBTC', interval=Client.KLINE_INTERVAL_4HOUR, limit = 100),
        'TRX': client.get_klines(symbol='TRXBTC', interval=Client.KLINE_INTERVAL_4HOUR, limit = 100),
        'NEO': client.get_klines(symbol='NEOBTC', interval=Client.KLINE_INTERVAL_4HOUR, limit = 100)
    }
    '''
    formatted = {}

    for c in candles:
        formatted[c] = {'date': [], 'close':[], 'open':[], 'high':[],'low':[], 'volume':[], 'price_usd': []}

    for c in candles:
        date, closep, highp, lowp, openp, volume, gmt_time, ts_format = [], [], [], [], [], [], [], []
        for d in candles[c]:
        #timestamp = time.strftime("%a %d %b %Y %H:%M:%S GMT", time.gmtime(candle[0] / 1000.0))
            dt_ts = datetime.fromtimestamp(int(d[0]) / 1e3 )
            formatted[c]['date'].append(mdates.date2num(dt_ts))
            timestamp = time.strftime("%b %d %H:%M", time.gmtime(d[0] / 1000.0))
            gmt_time.append(timestamp)
            date.append(int(d[0]))
            formatted[c]['open'].append(float(d[1]))
            formatted[c]['high'].append(float(d[2]))
            formatted[c]['low'].append(float(d[3]))
            formatted[c]['close'].append(float(d[4]))
            formatted[c]['volume'].append(float(d[5]))

    for f in formatted:
        priceIndex = 0
        if(f == 'BTC'):
            formatted[f]['price_usd'] = formatted[f]['close']
        else:
            for coin in formatted[f]['close']:
                formatted[f]['price_usd'].append(coin * formatted['BTC']['close'][priceIndex])
                priceIndex+=1

    df_list = {}
    prices = {}

    for f in formatted:
        df_list[f] = pd.DataFrame.from_dict(formatted[f])
        prices[f] = formatted[f]['price_usd']

    df_prices = pd.DataFrame(data=prices)
    corrMat = df_prices.pct_change().corr(method='pearson')

    print(corrMat)
    sns.heatmap(corrMat, square=True)
    plt.yticks(rotation=0)
    plt.xticks(rotation=90)
    #plt.title("Cryptocurrency Correlation Heatmap")

    directory = '../../../light-bootstrap-dashboard-react-master/src/assets/img/'
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    plt.savefig(directory + 'graph.png', bbox_inches='tight')
    print(f"Image saved to {directory + 'graph.png'}")
    #plt.show()

    '''
    candles1 = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_30MINUTE, limit=100)
    candles2 = client.get_klines(symbol='ETHBTC', interval=Client.KLINE_INTERVAL_30MINUTE, limit = 100)
    candles3 = client.get_klines(symbol='XRPBTC', interval=Client.KLINE_INTERVAL_30MINUTE, limit = 100)
    candles4 = client.get_klines(symbol='BCCBTC', interval=Client.KLINE_INTERVAL_30MINUTE, limit = 100)
    candles5 = client.get_klines(symbol='EOSBTC', interval=Client.KLINE_INTERVAL_30MINUTE, limit = 100)
    
    #print(candles2)
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

    date2, closep2, highp2, lowp2, openp2, volume2, ts_format2, gmt_time2 = [], [], [], [], [], [], [], []

    for candle in candles2:
        dt_ts2 = datetime.fromtimestamp(int(candle[0]) / 1e3 )
        ts_format2.append(mdates.date2num(dt_ts2))
        timestamp2 = time.strftime("%b %d %H:%M", time.gmtime(candle[0] / 1000.0))
        gmt_time2.append(timestamp2)
        date2.append(int(candle[0]))
        openp2.append(float(candle[1]))
        highp2.append(float(candle[2]))
        lowp2.append(float(candle[3]))
        closep2.append(float(candle[4]))
        volume2.append(float(candle[5]))

    x2 = 0
    y2 = len(date2)
    ohlc2 = []
    while x2 < y2:
        append_me2 = ts_format2[x2], openp2[x2], highp2[x2], lowp2[x2], closep2[x2], volume2[x2]
        ohlc2.append(append_me2)
        x2 += 1

    inputs2 = {
        'open': np.array(openp2),
        'high': np.array(highp2),
        'low': np.array(lowp2),
        'close': np.array(closep2),
        'volume': np.array(volume2)
    }

    
    output = SMA(inputs, timeperiod=25)
    slowk, slowd = STOCH(inputs, 5, 3, 0, 3, 0)
    real = RSI(inputs, timeperiod=7)
    

    macd, macdsignal, macdhist = MACD(inputs, fastperiod=12, slowperiod=26, signalperiod=9)
    #print(real)
    '''
    '''
    ax1 = plt.subplot2grid((6,1), (0,2))
    plt.xticks(rotation=25)
    plt.margins(0)
    ax2 = plt.subplot2grid((6,1), (3, 0))
    plt.xticks(rotation=25)
    plt.margins(0)
    ax3 = plt.subplot2grid((6,1), (5, 0))
    plt.xticks(rotation=25)
    plt.margins(0)
    
    ax1.scatter(closep, closep2)
    print(f'PearsonR: {scipy.stats.pearsonr(closep2, closep)}')
    '''

    '''
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
    '''

    
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
    jsParams = ''
    analyzeParams = ''

    try:
        opts, args = getopt.getopt(argv,"efwlhp:c:k:m:t:b:s:x:a:r:j:d:",["period=", "asset=", "klines=", "model=", "test=", "buy=", "sell=", "cancel=", "predict=", "btest=", "js=", "analyze="])
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
        elif opt in ("-j", "--js"):
            jsParams = arg
        elif opt in ("-d", "--analyze"):
            analyzeParams = arg
            

    while True:
        if(analyzeParams):
            analyzePair(analyzeParams)

        if(jsParams):
            returnCandles(jsParams)

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
                #sys.stdout = open(f'output/{filename1}.txt', 'w')

                print(datetime.now())
                prices = client.get_all_tickers()
                marketsymbols = []
                ta = []
                for symbol in prices:
                    if symbol['symbol'][-3:] == 'BTC':
                        marketsymbols.append(symbol['symbol'])
        
                for symbol in marketsymbols:
                    ta.append(test.testMethod(client, symbol, True))

                ta = list(filter(None.__ne__, ta))
                print("Stoch K lower than 20")
                for t in ta:
                    if(t['slowk'] <= 20):
                        if(t['macd'] <= t['macdsignal']):
                            if(t['price'] <= t['middleband']):
                                test.printOutputs(t)

                print("\n-------------------------------")
                print("Stoch K lower than D")

                for t in ta:
                    if(t['slowk'] <= 80 and t['slowk'] <= t['slowd']):
                        if(t['macd'] <= t['macdsignal']):
                            if(t['price'] <= t['middleband']):
                                test.printOutputs(t)

                #sys.stdout.close()
                #sys.stdout = sys.__stdout__
                print(f'Results displayed in output/{filename1}.txt')
            elif(testSymbol == 'ALL2') or (testSymbol == 'all2'):
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

                ta = list(filter(None.__ne__, ta))
                print("RSI lower than 30")
                for t in ta:
                    if(t['rsi'] <= 30):
                        test.printOutputs(t)

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