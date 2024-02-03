from itertools import chain

from lumibot.entities import Asset
from lumibot.strategies.strategy import Strategy
from timedelta import Timedelta

from src.modules.stocks_bot.utils.sentiments import SentimentEngine

dictArgs: {str: dict} = {}


class MLTrader(Strategy):

    def __init__(
            self,
            broker=None,
            minutes_before_closing=1,
            minutes_before_opening=60,
            sleeptime="1M",
            stats_file=None,
            risk_free_rate=None,
            benchmark_asset="SPY",
            backtesting_start=None,
            backtesting_end=None,
            quote_asset=Asset(symbol="USD", asset_type="forex"),
            starting_positions=None,
            filled_order_callback=None,
            name=None,
            budget=None,
            parameters={},
            buy_trading_fees=[],
            sell_trading_fees=[],
            force_start_immediately=False,
            options={},
            **kwargs,
    ):
        super().__init__(
            broker=broker,
            minutes_before_closing=minutes_before_closing,
            minutes_before_opening=minutes_before_opening,
            sleeptime=sleeptime,
            stats_file=stats_file,
            risk_free_rate=risk_free_rate,
            benchmark_asset=benchmark_asset,
            backtesting_start=backtesting_start,
            backtesting_end=backtesting_end,
            quote_asset=quote_asset,
            starting_positions=starting_positions,
            filled_order_callback=filled_order_callback,
            name=name,
            budget=budget,
            parameters=parameters,
            buy_trading_fees=buy_trading_fees,
            sell_trading_fees=sell_trading_fees,
            force_start_immediately=force_start_immediately,
            kwargs=kwargs)
        self.last_trade = None
        self.cash_at_risk = None
        self.symbol = None
        self.sentiment_engine = None

        if "symbol" in options:
            symbol = options["symbol"]
        else:
            symbol = parameters["symbol"]

        if symbol not in dictArgs:
            dictArgs[symbol] = {}

        if len(options) > 0:
            dictArgs[symbol] = dict(chain.from_iterable(d.items() for d in (dictArgs[symbol], options)))

    def initialize(self, symbol: str):
        self.symbol = dictArgs[symbol]["symbol"]
        self.cash_at_risk = dictArgs[symbol]["cash_at_risk"]
        self.sleeptime = dictArgs[symbol]["sleeptime"]
        dictArgs[symbol]["sleeptime_delta"] = self.get_sleeptime_delta()
        self.sentiment_engine = dictArgs[symbol]["sentiment_engine"]

        self.last_trade = None

    def on_trading_iteration(self):
        sentiment_engine: SentimentEngine = self.sentiment_engine(
            self.get_datetime(),
            self.symbol,
            self.get_last_price(self.symbol),
            self.get_cash(),
            self.cash_at_risk,
            dictArgs[self.symbol])

        cash, last_price, quantity = sentiment_engine.position_sizing()
        decision = sentiment_engine.get_decision()
        if decision == "buy":
            if self.last_trade == "sell":
                self.sell_all()
            order = self.create_order(
                self.symbol,
                quantity,
                "buy",
                type="bracket",
                take_profit_price=last_price * 1.20,
                stop_loss_price=last_price * .95
            )
            self.submit_order(order)
            self.last_trade = "buy"
        elif decision == "sell":
            if self.last_trade == "buy":
                self.sell_all()
            order = self.create_order(
                self.symbol,
                quantity,
                "sell",
                type="bracket",
                take_profit_price=last_price * .8,
                stop_loss_price=last_price * 1.05
            )
            self.submit_order(order)
            self.last_trade = "sell"

    def get_sleeptime_delta(self):
        i = 0
        for c in self.sleeptime:
            if not c.isnumeric():
                break
            else:
                i = i + 1
        intStr = self.sleeptime[0:i]
        num = int("0" if intStr == "" else intStr)
        duration = self.sleeptime[i:]

        if duration == "H":
            delta = Timedelta(hours=num)
        elif duration == "S":
            delta = Timedelta(seconds=num)
        else:
            delta = Timedelta(minutes=num)

        return delta;
