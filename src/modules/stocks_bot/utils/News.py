from datetime import datetime

import yfinance as yf
from alpaca.data import NewsRequest
from alpaca.data.historical.news import NewsClient
from alpaca.data.models.news import NewsSet

from env import ENV

alpaca_news_api = NewsClient(api_key=ENV.ALPACA_API_KEY, secret_key=ENV.ALPACA_API_SECRET,
                              use_basic_auth=False)


def get_yahoo_news(symbol: str, start: datetime = None, end: datetime = None):
    ticker = yf.Ticker(symbol)
    return [ev["title"] for ev in ticker.news]


def get_alpaca_news(symbol: str, start: datetime = None, end: datetime = None):
    news_set: NewsSet = alpaca_news_api.get_news(NewsRequest(symbols=symbol,
                                                              start=start,
                                                              end=end))
    news = news_set.news
    return [ev.__dict__["headline"] for ev in news]


if __name__ == "__main__":
    print(get_yahoo_news("TSLA"))
