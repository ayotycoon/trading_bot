from itertools import chain
from typing import Union

from lumibot.strategies.strategy import Strategy
from timedelta import Timedelta

from src.modules.stocks_bot.utils.sentiments import SentimentEngine


class MLTrader(Strategy):
    symbols: list[dict[str, float]] = []
    last_iteration = {'global': {}}
    first_daily_iteration = None
    last_trade = None
    sleeptime = "1M"
    cash_at_risk = 0
    sentiment_engine: SentimentEngine = None

    def initialize(self, ):
        self.symbols = self.get_parameters()["symbols"]
        self.cash_at_risk = self.get_parameters()["cash_at_risk"]
        self.sleeptime = self.get_parameters()["sleeptime"]
        self.get_parameters()["sleeptime_delta"] = self.get_sleeptime_delta()
        self.sentiment_engine = self.get_parameters()["sentiment_engine"]

        self.last_trade = None
        self._executor._trace_stats = lambda context, snapshot_before: self.trace_stats(context,
                                                                                        snapshot_before)

    def on_trading_iteration(self):
        temp_cash = self.get_cash()
        config = self.get_parameters()
        config['history'] = self._stats_list
        config['first_daily_iteration'] = self.first_daily_iteration
        self.last_iteration['global'] = {'count': 0}

        global_itr = self.last_iteration['global']

        for symbolObj in self.symbols:
            symbol = symbolObj['symbol']
            weight = symbolObj['weight']
            if symbol not in self.last_iteration:
                self.last_iteration[symbol] = {}
            symbol_last_iteration = self.last_iteration[symbol]
            symbol_last_iteration['last_price'] = self.get_last_price(symbol)
            global_itr['count'] = global_itr['count'] + 1
            last_price = self.get_last_price(symbol)

            decision, cash, quantity, news, sentiment, probability,symbol_cash = (
                self.sentiment_engine.get_decision(
                    self.get_datetime(),
                    symbol,
                    self.get_last_price(symbol),
                    temp_cash,
                    self.cash_at_risk*weight,
                    config,
                ))

            symbol_last_iteration['trade_qty'] = quantity
            symbol_last_iteration['news'] = news
            if decision == "buy":
                if self.last_trade == "sell":
                    self.sell_all()
                if cash <= temp_cash:
                    order = self.create_order(
                        symbol,
                        quantity,
                        "buy",
                        type="bracket",
                        take_profit_price=last_price * 1.20,
                        stop_loss_price=last_price * .95
                    )
                    self.submit_order(order)
                    temp_cash = temp_cash - symbol_cash
                self.last_trade = "buy"
            elif decision == "sell":
                if self.last_trade == "buy":
                    self.sell_all()
                if self.get_position(symbol) is not None and quantity <= self.get_position(symbol).quantity:
                    order = self.create_order(
                        symbol,
                        quantity,
                        "sell",
                        type="bracket",
                        take_profit_price=last_price * .8,
                        stop_loss_price=last_price * 1.05
                    )
                    self.submit_order(order)
                self.last_trade = "sell"
            else:
                symbol_last_iteration['trade_qty'] = 0

            symbol_last_iteration['decision'] = decision
            symbol_last_iteration['sentiment'] = sentiment
            symbol_last_iteration['probability'] = probability

            global_itr['first_iteration'] = self.first_iteration
            global_itr['first_daily_iteration'] = self.first_daily_iteration

        self.first_daily_iteration = False

    def trace_stats(self, context, snapshot_before):
        self.log_message("Trace stats")
        self.log_message(f"Context: {context}")
        self.log_message(f"Snapshot before: {snapshot_before}")

        result = {
            "count": self.last_iteration['global']['count'],
            "datetime": self.get_datetime(),
            "portfolio_value": round(self.portfolio_value, 2),
            "cash": round(self.cash, 2),
            "first_daily_iteration": self.last_iteration['global']['first_daily_iteration'],

            # "news": ' | '.join(x for x in self.last_iteration['news']),
            "last_price": [],
            "decision": [],
            # "probability": self.last_iteration['probability'],
            # "sentiment": self.last_iteration['sentiment'],

        }

        for symbolObj in self.symbols:
            symbol = symbolObj['symbol']
            result["last_price"].append({'k': symbol, 'v': round(self.last_iteration[symbol]['last_price'], 2)})
            result["decision"].append({'k': symbol, 'v': self.last_iteration[symbol]['decision']})

        result["last_price"] = ' | '.join((x['k'] + "=" + str(x['v'])) for x in result["last_price"])
        result["decision"] = ' | '.join(
            (x['k'] + "=" + ('none' if x['v'] is None else x['v'])) for x in result["decision"])

        self._append_row(result)
        return result

    def on_strategy_end(self):
        pass

    def before_market_opens(self):
        pass

    def before_starting_trading(self):
        self.first_daily_iteration = True
        pass

    def after_market_closes(self):
        pass

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
