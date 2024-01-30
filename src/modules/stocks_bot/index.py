from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from datetime import datetime
from src.modules.stocks_bot.utils.MLTrader import MLTrader
from src.utils.env import ENV
from src.utils.logger import customLogger


def start():
    customLogger.info("starting bot")
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    broker = Alpaca({
        "API_KEY": ENV.ALPACA_API_KEY,
        "API_SECRET": ENV.ALPACA_API_SECRET,
        "PAPER": ENV.ALPACA_PAPER
    })
    strategy = MLTrader(name='mlstrat', broker=broker,
                        parameters={"symbol": "SPY",
                                    "cash_at_risk": .5})
    strategy.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
        parameters={"symbol": "SPY", "cash_at_risk": .5}
    )
    # trader = Trader()
    # trader.add_strategy(strategy)
    # trader.run_all()
