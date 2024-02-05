from datetime import datetime

import torch
from timedelta import Timedelta
from transformers import AutoTokenizer, AutoModelForSequenceClassification

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
        return sentiment, float(probability), news
    else:
        return labels[-1], 0, []


def get_dates(date: datetime = None, delta: Timedelta = None):
    prev_date = date - delta
    return date.strftime('%Y-%m-%dT%H:%M:%S'), prev_date.strftime('%Y-%m-%dT%H:%M:%S')
