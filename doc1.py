import websocket, json, pprint, talib, numpy
from werkzeug.utils import redirect

import config
from binance.client import Client
from binance.enums import *
from flask import Flask, render_template, request, url_for
from datetime import datetime
import threading


app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        todo = request.form.get("api_key")
        api_password = request.form.get("api_secret")
        moeda = request.form.get("moeda")
        print(todo)
        print(api_password)
        print(moeda)
        return render_template('principal.html')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)