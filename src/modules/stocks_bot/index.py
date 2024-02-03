from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from datetime import datetime

from lumibot.traders import Trader

from src.modules.stocks_bot.utils.sentiments.SentimentEngine import SentimentEngine
from src.modules.stocks_bot.utils.traders.MLTrader import MLTrader
from env import ENV
from src.utils.logger import customLogger


def get_strategy(symbol="SPY"):
    broker = Alpaca({
        "API_KEY": ENV.ALPACA_API_KEY,
        "API_SECRET": ENV.ALPACA_API_SECRET,
        "PAPER": ENV.ALPACA_PAPER
    })
    return MLTrader(
        name='mlstrat',
        broker=broker,
        options={
            "symbol": symbol,
            "cash_at_risk": .5,
            "sleeptime": "6H",
            "sentiment_engine":
                lambda date, symbol, last_price, cash, cash_at_risk, config:
                SentimentEngine(
                    date,
                    symbol,
                    last_price,
                    cash,
                    cash_at_risk,
                    config
                )
        }
    )


def backtest(symbol="SPY", start_date: datetime = None, end_date: datetime = None):
    strategy = get_strategy(symbol)
    strategy.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
        parameters={"symbol": symbol, "cash_at_risk": .5}
    )


def trade(symbol="SPY"):
    strategy = get_strategy(symbol)
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()


if __name__ == "__main__":
    backtest(
        symbol="SPY",
        start_date=datetime(2023, 12, 1),
        end_date=datetime(2023, 12, 31))
