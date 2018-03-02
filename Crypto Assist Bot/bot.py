import time
import sys, getopt
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
    print('     -c <asset>      Check asset balance')
    print('     -b              Show current asset balances')
    print('     -l              Last market prices')
    
def main(argv):
    period = 0
    pair = ''
    checkLastPrice = False
    showCurrentBalance = False

    try:
        opts, args = getopt.getopt(argv,"blhp:c:",["period=", "asset="])
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


    while True:
        if(checkLastPrice):
            printLastMarketPrices()
        
        if(showCurrentBalance):
            printCurrentAssets()

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