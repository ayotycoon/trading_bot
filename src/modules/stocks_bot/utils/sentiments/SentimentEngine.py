from datetime import datetime
from typing import Union

import torch

from src.modules.stocks_bot.utils.News import get_alpaca_news
from src.modules.stocks_bot.utils.sentiments.util import estimate_sentiment, get_dates
from src.utils.safe_call import ignore_errors

w = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


class SentimentEngine:

    def news_sentiment(self, symbol: str = None, date: datetime = None, config={}):
        history = config['history']
        # is_first_daily_trade = config['history'][-1]
        is_first_daily_trade = len(history) == 0
        date, prev_date = get_dates(date, config['sleeptime_delta'])
        # if is_first_daily_trade and len(self.priceHistory) >1 and  len(self.priceHistory[-2]) > 0:
        #     prev_date = self.priceHistory[-2][-1]["datetime"]

        news = ignore_errors(lambda: get_alpaca_news(symbol, prev_date, date), [])
        return estimate_sentiment(news)

    def get_sentiment(self, symbol: str = None, date: datetime = None, config={}):
        return self.news_sentiment(symbol, date, config)

    def get_decision(self, date: datetime, symbol: str, last_price: float, cash: float, cash_at_risk: float, config={}):

        sentiment, probability, news = self.get_sentiment(symbol, date, config)
        symbol_cash = cash * cash_at_risk
        quantity = round(symbol_cash / last_price, 5)
        decision = None
        if cash > last_price:
            if sentiment == "positive" and probability > .999:
                decision = "buy"
            elif sentiment == "negative" and probability > .999:
                decision = "sell"
            else:
                quantity = 0

        return decision, cash, quantity, news,sentiment,probability,symbol_cash

    def market_closed(self):
        pass


if __name__ == "__main__":
    tensor, sentiment = estimate_sentiment(['markets responded negatively to the news!', 'traders were displeased!'])
    print(tensor, sentiment)
    print(torch.cuda.is_available())
