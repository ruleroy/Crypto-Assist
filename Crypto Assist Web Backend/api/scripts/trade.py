from binance.client import Client
from binance.enums import *

def buyOrder(client, pair, price, quantity):
    try:
        info = client.get_symbol_info(pair)
        print(f"Min price: {info['filters'][0]['minPrice']}")
        print(f"Max price: {info['filters'][0]['maxPrice']}")
        print(f"Min quantity: {info['filters'][1]['minQty']}")
        print(f"Max quantity: {info['filters'][1]['maxQty']}")
        print(f"Min notional: {info['filters'][2]['minNotional']}")

        order = client.create_order(
        symbol=pair,
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=price)

        orderId = order['orderId']
        getOrder = client.get_order(symbol=pair, orderId=orderId)
        print(f"Price: {getOrder['price']}      Amount: {getOrder['executedQty']}/{getOrder['origQty']}      Side: {getOrder['side']}    Status: {getOrder['status']}")

    except Exception as e:
        print("Error placing buy order.")
        print(e)
    
def sellOrder(client, pair, price, quantity):
    try:
        order = client.create_order(
        symbol=pair,
        side=SIDE_SELL,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=price)

        orderId = order['orderId']
        getOrder = client.get_order(symbol=pair, orderId=orderId)
        print(f"Price: {getOrder['price']}      Amount: {getOrder['executedQty']}/{getOrder['origQty']}      Side: {getOrder['side']}    Status: {getOrder['status']}")

        cancelOrder(client, pair, orderId)
    except Exception as e:
        print("Error placing sell order.")
        print(e)

def cancelOrder(client, pair, orderId):
    try:
        result = client.cancel_order(
        symbol=pair,
        orderId=orderId)

        print(f"Order Id {orderId} canceled")
    except Exception as e:
        print("Error canceling order.")
        print(e)

def cancelAllOrders(client, pair):
    try:
        orders = client.get_open_orders(symbol=pair)
        for order in orders:
            cancelOrder(client, pair, order['orderId'])
        print("All orders canceled")
    except Exception as e:
        print("Error canceling all orders.")
        print(e)