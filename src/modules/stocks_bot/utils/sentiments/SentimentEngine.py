from datetime import datetime

import torch
from alpaca.data.historical.news import NewsClient
from alpaca.data.models.news import NewsSet
from alpaca.data.requests import NewsRequest
from timedelta import Timedelta
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from env import ENV
from src.modules.stocks_bot.utils.News import get_alpaca_news

device = "cuda:0" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]


def estimate_sentiment(news: list[str]):
    if news and len(news):
        tokens = tokenizer(news, return_tensors="pt", padding=True).to(device)

        result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])[
            "logits"
        ]
        result = torch.nn.functional.softmax(torch.sum(result, 0), dim=-1)
        probability = result[torch.argmax(result)]
        sentiment = labels[torch.argmax(result)]
        return sentiment, probability
    else:
        return labels[-1], 0


class SentimentEngine:
    date: datetime
    symbol: str

    def __init__(self, date: datetime, symbol: str, last_price: float, cash: float, cash_at_risk: float, config={}):
        self.date = date
        self.config = config
        self.symbol = symbol
        self.cash = cash
        self.cash_at_risk = cash_at_risk
        self.last_price = last_price

    def get_dates(self):
        delta: Timedelta = self.config['sleeptime_delta']
        prev_date = self.date - delta
        return self.date.strftime('%Y-%m-%dT%H:%M:%S'), prev_date.strftime('%Y-%m-%dT%H:%M:%S')

    def news_sentiment(self):
        date, prev_date = self.get_dates()
        news = get_alpaca_news(self.symbol, prev_date, date)
        return estimate_sentiment(news)

    def get_sentiment(self):
        return self.news_sentiment()

    def position_sizing(self):
        quantity = round(self.cash * self.cash_at_risk / self.last_price, 0)
        return self.cash, self.last_price, quantity

    def get_decision(self):
        sentiment, probability = self.get_sentiment()
        if self.cash > self.last_price:
            if sentiment == "positive" and probability > .999:
                return "buy"
            elif sentiment == "negative" and probability > .999:
                return "sell"

        return None


if __name__ == "__main__":
    tensor, sentiment = estimate_sentiment(['markets responded negatively to the news!', 'traders were displeased!'])
    print(tensor, sentiment)
    print(torch.cuda.is_available())
