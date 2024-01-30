from flask import Flask
from src.modules.stocks_bot.index import start
from dotenv import load_dotenv

load_dotenv()
start()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


