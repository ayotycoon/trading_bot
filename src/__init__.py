from datetime import datetime

from flask import Flask
from src.modules.stocks_bot.index import backtest

backtest(
    symbol="SPY",
    start_date=datetime(2023, 12, 1),
    end_date=datetime(2023, 12, 31))

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


