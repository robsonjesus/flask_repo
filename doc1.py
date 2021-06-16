import os
import websocket, json, pprint, talib, numpy
from werkzeug.utils import redirect

import config
from binance.client import Client
from binance.enums import *
from flask import Flask, render_template, request, url_for
from datetime import datetime
import threading
from flask import Flask



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
valor_fechamento = 0
moeda =''
rsi_upper = 0
rsi_lower = 0
qtd_trade = 0.0
last_rsi = 0


client = Client(config.API_KEY, config.API_SECRET)


raw_server_time = client.get_server_time()
server_time = datetime.fromtimestamp(raw_server_time['serverTime']/1000.0)
print(server_time)



###### Inicio WebSocket ############

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


def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes, in_position, valor_fechamento
    global qtd_candle_closed
    global qtd_venda, qtd_compra
    global moeda
    global rsi_upper, rsi_lower, qtd_trade, last_rsi



    print('received message')
    print()
    print(f'Qtd venda: {qtd_venda}')
    print(f'Qtd compra: {qtd_compra}')
    print()
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    valor_fechamento = close

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

            if last_rsi > rsi_upper:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, qtd_trade, moeda)
                    if order_succeeded:
                        in_position = False
                        qtd_venda += 1
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")

            if last_rsi < rsi_lower:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, qtd_trade, moeda)
                    if order_succeeded:
                        in_position = True
                        qtd_compra += 1



@app.route('/intex_antigo')
def index():
    return render_template('index.html')



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)


api_key = ''
api_password = ''
@app.route("/", methods=["POST", "GET"])
def home():
    global api_key
    global api_password
    global client
    global moeda , rsi_upper, rsi_lower, qtd_trade

    if request.method == "POST":
        api_key = request.form.get("api_key")
        api_password = request.form.get("api_secret")
        moeda = request.form.get("moeda")
        rsi_upper = request.form.get("rsi_upper")
        rsi_lower = request.form.get("rsi_lower")
        qtd_trade = float(request.form.get("qtd_trade"))
        print(api_key)
        print(api_password)
        print(moeda)
        print(rsi_upper)
        print(rsi_lower)
        print(qtd_trade)
        client = Client(api_key, api_password)
        return redirect(url_for('principal'))

    return render_template('index.html')


def funcaoSocket():
    ws.run_forever()

trava = False
email = '123'
@app.route('/principal')
def principal():
    global trava
    global email
    dt = str(datetime.now())
    # os = platform.system()
    # pyver = sys.version


    print('Estou rodando')
    if trava == False:
        t2 = threading.Thread(name="Hello", target=funcaoSocket)
        t2.start()
        trava = True
    return render_template('principal.html',
                           moeda=moeda,
                           rsi_upper=rsi_upper,
                           rsi_lower=rsi_lower,
                           qtd_trade=qtd_trade, fechamento=qtd_candle_closed, valor=valor_fechamento,
                           api_chave=api_key, api_senha=api_password, closes=closes[-14:], last_rsi=last_rsi)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)