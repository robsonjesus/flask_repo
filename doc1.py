import websocket, json, pprint, talib, numpy
from werkzeug.utils import redirect

import config
from binance.client import Client
from binance.enums import *
from flask import Flask, render_template, request, url_for
from datetime import datetime
import threading


app = Flask(__name__)


@app.route("/")
def home():
 
    return 'Server Rodando'


const PORT = process.env.PORT || '8080'

app = express();

app.set("port", PORT)

if __name__ == '__main__':
    app.run(debug=True)