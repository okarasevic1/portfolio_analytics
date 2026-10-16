import pandas as pd
import asyncio 
from ib_async import *


class IBKR:

    ''' 
        IBKR API Async wrapper for handling missing values
    '''

    def __init__(self):
        self.ib = IB()

    async def connect(self):
        await self.ib.connectAsync('127.0.0.1', port=7497, clientId=0)


    async def fetchContracts(self, isins:list[str], currencies:list[str]) -> list[Contract]:

        result_list = []

        for isin, currency in zip(isins, currencies):

            contract = Contract(
                secType='STK',
                secIdType='ISIN',
                secId=isin,
                exchange='SMART',
                currency=currency
            )

            details = await self.ib.reqContractDetailsAsync(contract=contract)
            contract = details[0].contract

            print(
                f"Symbol: {contract.symbol}, "
                f"ConId: {contract.conId}, "
                f"Exchange: {contract.primaryExchange}, "
                f"Currency: {contract.currency}"
            )

            result_list.append(contract)

        return result_list


    async def downloadPrices(self, contracts:list[Contract]):

        if not self.ib.isConnected():
            self.connect()

        prices_df = pd.DataFrame([])

        for contract in contracts:

            bars = await self.ib.reqHistoricalDataAsync(
                contract=contract,
                endDateTime='',
                durationStr='365 D',
                barSizeSetting='1 day',
                whatToShow='TRADES',
                useRTH=False,
                formatDate=1,
                keepUpToDate=False
            )

            if len(prices_df) < 0:
                prices_df = util.df(bars)
                prices_df['Ticker'] = contract.symbol

            else:

                temp_df = util.df(bars)
                temp_df['Ticker'] = contract.symbol
                prices_df = pd.concat([prices_df, temp_df])

        prices_df = prices_df.sort_values(by=['date', 'Ticker'])

        return prices_df 


    def disconect(self):
        self.ib.disconnect()

    