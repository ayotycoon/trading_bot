from lumibot.strategies.strategy import Strategy
from alpaca.common.rest import RESTClient
from timedelta import Timedelta
from src.modules.stocks_bot.finbert_utils import estimate_sentiment
from src.utils.env import ENV
from alpaca.data.requests import NewsRequest
from alpaca.data.historical.news import NewsClient
from alpaca.data.models.news import NewsSet


class MLTrader(Strategy):

    def initialize(self, symbol: str = "SPY", cash_at_risk: float = .5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = NewsClient(api_key=ENV.ALPACA_API_KEY, secret_key=ENV.ALPACA_API_SECRET,
                              use_basic_auth=False, )

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%dT%H:%M:%S'), three_days_prior.strftime('%Y-%m-%dT%H:%M:%S')

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news_set: NewsSet = self.api.get_news(NewsRequest(symbol=self.symbol,
                                             start=three_days_prior,
                                             end=today))
        news = news_set.news
        headlines = [ev.__dict__["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(headlines)
        return probability, sentiment

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()

        if cash > last_price:
            if sentiment == "positive" and probability > .999:
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
            elif sentiment == "negative" and probability > .999:
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
