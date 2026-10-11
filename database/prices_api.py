from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import ContractDetails,Contract
import time 
import threading
from ibapi.ticktype import TickTypeEnum



class TestApp(EClient, EWrapper):

    def __init__(self):
        EClient.__init__(self, self)


    def nextValidId(self, orderId):
        self.orderId = orderId


    def nextId(self):
        self.orderId += 1 
        return self.orderId


    def error(self, reqId, errorTime, errorCode, errorString, advancedOrderRejectJson=""):
        print(f'reqId: {reqId} - errorCode: {errorCode} - errorString {errorString}, {advancedOrderRejectJson}')
    


    def historicalData(self, reqId, bar):
        print(reqId, bar.close)


    def historicalDataEnd(self, reqId, start, end):
        print(f'{reqId}')
        print(f'Start date: {start};\nEnd date: {end}')



app = TestApp()
app.connect('127.0.0.1', port=7497, clientId=0)


threading.Thread(target=app.run).start()
time.sleep(1)

my_contract = Contract()
my_contract.symbol = 'AAPL'
my_contract.currency = 'USD'
my_contract.secType = 'STK'
my_contract.exchange = 'SMART'

app.reqHistoricalData(
    app.nextId(),
    my_contract,
    "",          # Latest available date
    "1 Y",       # One week
    "1 day",     # Daily candles
    "BID",       # Forex bid prices
    0,           # Include all available trading hours
    1,           # Human-readable dates
    False,
    []
)

time.sleep(3)


app.disconnect()