from datetime import datetime

import yfinance as yf
from alpaca.data import NewsRequest
from alpaca.data.historical.news import NewsClient
from alpaca.data.models.news import NewsSet
import requests
from urllib.parse import urlencode

from env import ENV
from src.modules.stocks_bot.utils.sentiments.util import estimate_sentiment

alpaca_news_api = NewsClient(api_key=ENV.ALPACA_API_KEY, secret_key=ENV.ALPACA_API_SECRET,
                             use_basic_auth=False)


def get_yahoo_news(symbol: str, start: str = None, end: str = None):
    ticker = yf.Ticker(symbol)
    return [ev["title"] for ev in ticker.news]


def get_alpaca_news(symbol: str, start: str = None, end: str = None):
    news_set: NewsSet = (
        alpaca_news_api.get_news(
            NewsRequest(
                symbolsg=symbol,
                start=start,
                end=end)))
    news = news_set.news
    return [ev.__dict__["headline"] for ev in news]


def get_marketaux_news(symbol: str, start: str = None, end: str = None):
    api_url = "https://api.marketaux.com/v1/news/all"
    query = {'api_token': ENV.MARKETAUX_TOKEN, 'symbols': symbol, "published_after": start, "published_before": end,
             "limit": 10, "page": 1}

    response = requests.get(api_url + "?" + urlencode(query))
    return [ev['description'] for ev in response.json()["data"]]


if __name__ == "__main__":
    print(estimate_sentiment(get_marketaux_news("INTU", "2024-01-04T07:56", "2024-01-20T07:56")))
