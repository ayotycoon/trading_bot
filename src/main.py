from flask import Flask
from src.modules.stocks_bot.main import start as stocks_start
from dotenv import load_dotenv

load_dotenv()
stocks_start()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


