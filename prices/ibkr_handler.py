import pandas as pd
import asyncio 
from ib_async import *
from datetime import datetime

class IBKR:

    ''' 
        IBKR API Async wrapper for handling missing values
    '''

    def __init__(self, end_date, interval):
        self.end_date = end_date
        self.interval = interval
        self.ib = IB()


    async def connect(self):
        await self.ib.connectAsync('127.0.0.1', port=7497, clientId=0)


    async def fetchContract(self, isin:str, currency:str) -> Contract:

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

        return contract


    async def downloadPrices(self, contract:Contract):

        if not self.ib.isConnected():
            self.connect()

        ib_date = self.ibkr_date_format(self.end_date)

        bars = await self.ib.reqHistoricalDataAsync(
            contract=contract,
            endDateTime=ib_date,
            durationStr=f'{self.interval} D',
            barSizeSetting='1 day',
            whatToShow='TRADES',
            useRTH=False,
            formatDate=1,
            keepUpToDate=False
        )

        prices_df = util.df(bars)
        prices_df['Ticker'] = contract.symbol

        # preprocess dataframe for future concatenation
        prices_df = prices_df.drop(['barCount', 'average'], axis=1)

        prices_df = prices_df.rename({
                'date':'Date',
                'open':'Open',
                'high':'High',
                'low':'Low',
                'close':'Close',
                'volume':'Volume'
            }, axis=1
        )

        return prices_df 


    async def fetchMany(self, instruments:list):
        '''
            Fetch async contracts and their prices
        '''

        try:
            await self.connect()
        except ConnectionError:
            raise ConnectionError('Open TWS or try to connect again')
        
        # request Contact Details by ISIN
        async with asyncio.TaskGroup() as task_group:

            tasks = [
                task_group.create_task(
                    self.fetchContract(isin, curr)
                )
                for isin, curr in instruments
            ]

        result_contracts = [task.result() for task in tasks]

        prices_df = pd.DataFrame([])

        # download Prices based on request of ContractDetails
        async with asyncio.TaskGroup() as task_group:

            prices_tasks = [
                task_group.create_task(
                    self.downloadPrices(contract)
                )
                for contract in result_contracts
            ]

        for price_task in prices_tasks:
            if len(prices_df) <= 0:
                prices_df = price_task.result()
                continue

            prices_df = pd.concat([prices_df, price_task.result()])


        self.disconect()

        return prices_df


    def ibkr_date_format(self, date:str):
        dt = datetime.strptime(date, "%Y-%m-%d")
        return dt.strftime("%Y%m%d-23:59:59")

    
    def disconect(self):
        self.ib.disconnect()


    