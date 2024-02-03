from dotenv import load_dotenv
import os
load_dotenv()


class ENV:
    ALPACA_OAUTH_TOKEN: str = os.environ.get("ALPACA_OAUTH_TOKEN")
    ALPACA_API_KEY: str = os.environ.get("ALPACA_API_KEY")
    ALPACA_API_SECRET: str = os.environ.get("ALPACA_API_SECRET")
    ALPACA_BASE_URL: str = os.environ.get("ALPACA_BASE_URL")
    ALPACA_PAPER: bool = True if os.environ.get("ALPACA_PAPER") == "True" else False
