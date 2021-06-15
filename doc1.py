import os

import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
from datetime import datetime

from flask import Flask, jsonify, request


app = Flask(__name__)


SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

RSI_PERIOD = 14 # 14
RSI_OVERBOUGHT = 70 # 70
RSI_OVERSOLD = 30 # 30
TRADE_SYMBOL = 'BTCBRL'
TRADE_QUANTITY = 0.000109 #BTC 0.000109 = R$22,00 #ETH 0.003

closes = []
in_position = False
qtd_candle_closed = 0
qtd_compra = 0
qtd_venda = 0
string1 = ''

client = Client(config.API_KEY, config.API_SECRET)


raw_server_time = client.get_server_time()
server_time = datetime.fromtimestamp(raw_server_time['serverTime']/1000.0)
print(server_time)

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


def on_open(ws):
    print('opened connection')
    string1 = 'Conexao Aberta'

def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes, in_position
    global qtd_candle_closed
    global qtd_venda, qtd_compra

    print('received message')
    print()
    print(f'Qtd venda: {qtd_venda}')
    print(f'Qtd compra: {qtd_compra}')
    print()
    string1 = 'Mensagem recebida'
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    print(f'Quantidade de vezes que fechou: {qtd_candle_closed}')

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes[-14:])
        qtd_candle_closed += 1

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi[-20:])
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                        qtd_venda += 1
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True
                        qtd_compra += 1


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()


@app.route('/')
def nao_entre_em_panico():
    if request.headers.get('Authorization') == '42':
        return jsonify({"42": "a resposta para a vida, o universo e tudo mais"})
    return jsonify({string1})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)