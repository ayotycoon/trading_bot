from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask
from src.modules.stocks_bot.index import backtest
from src.modules.stocks_bot.utils.sentiments.SentimentEngine import SentimentEngine


symbol = "SPY"
parameters={
    "symbol": symbol,
    "cash_at_risk": .5,
    "sleeptime": "3H",
    "sentiment_engine":
        SentimentEngine()
}

backtest(
    symbol="SPY",
    start_date=datetime(2023, 12, 1, tzinfo=ZoneInfo("America/New_York")),
    end_date=datetime(2023, 12, 31, tzinfo=ZoneInfo("America/New_York"))
)

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
