import os
from dotenv import load_dotenv
from datetime import datetime

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

load_dotenv()


today = datetime.today()

client = StockHistoricalDataClient(
    api_key=os.environ['ALPACA_API_KEY'],
    secret_key=os.environ['ALPACA_SECRET_KEY']
)

request_stock = StockBarsRequest(
    symbol_or_symbols=['VOO'],
    start='2026-01-01',
    end=today,
    timeframe=TimeFrame.Day,
    feed=DataFeed.IEX
)

btc_bars = client.get_stock_bars(request_stock)
print(btc_bars.df)

