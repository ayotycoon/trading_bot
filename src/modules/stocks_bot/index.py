from zoneinfo import ZoneInfo

from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from datetime import datetime

from lumibot.traders import Trader

from src.modules.stocks_bot.utils.sentiments.SentimentEngine import SentimentEngine
from src.modules.stocks_bot.utils.traders.MLTrader import MLTrader
from env import ENV
from src.utils.logger import customLogger


def get_strategy(parameters={}):
    broker = Alpaca({
        "API_KEY": ENV.ALPACA_API_KEY,
        "API_SECRET": ENV.ALPACA_API_SECRET,
        "PAPER": ENV.ALPACA_PAPER
    })
    return MLTrader(
        name='mlstrat',
        broker=broker,
        parameters=parameters
    )


def backtest(start_date: datetime = None, end_date: datetime = None, benchmark_asset="SPY",
             parameters={}):
    strategy = get_strategy(parameters)
    f = strategy.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
        benchmark_asset=benchmark_asset,
        parameters=parameters
    )
    d = 1


def trade(parameters={}):
    strategy = get_strategy(parameters)
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()


if __name__ == "__main__":

    symbols = [
        {'symbol': 'AAPL', 'weight': 0.20281566212054558},
        {'symbol': 'MSFT', 'weight': 0.18939727232732073},
        {'symbol': 'AMZN', 'weight': 0.10624725032996042},
        {'symbol': 'AVGO', 'weight': 0.09128904531456228},
        {'symbol': 'META', 'weight': 0.08468983721953367},
        {'symbol': 'NVDA', 'weight': 0.08293004839419271},
        {'symbol': 'TSLA', 'weight': 0.08095028596568413},
        {'symbol': 'GOOGL', 'weight': 0.056093268807743075},
        {'symbol': 'GOOG', 'weight': 0.05455345358556974},
        {'symbol': 'COST', 'weight': 0.05103387593488782}
    ]
    parameters = {
        "symbols": symbols,
        "cash_at_risk": .5,
        "sleeptime": "30M",
        "sentiment_engine":
            SentimentEngine()
    }
    # trade(
    #     symbol="SPY",
    # parameters=parameters)

    backtest(
        start_date=datetime(2023, 12, 1, tzinfo=ZoneInfo("America/New_York")),
        end_date=datetime(2023, 12, 31, tzinfo=ZoneInfo("America/New_York")),
        parameters=parameters)

    t = 0
    for g in symbols:
        t = t + g['weight']

    for g in symbols:
        g['weight'] = g['weight']/t

    t =  100
