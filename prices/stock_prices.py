import pandas as pd 
import numpy as np
import yfinance as yf 
from yfinance.lookup import Lookup
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import time
from ibkr_handler import IBKR
import asyncio

class Prices:

    async def fetch_prices(self, tickers:list[str], isins:list[str], 
                     currencies:list[str], 
                     start_date=None, end_date=None, 
                     interval=182
                    ):
        '''
            tickers: what prices does it to fetch
            start_date: can bee none, from what date do we need prices 
            end_date: by what date do the prices need to provided 
            interval (in days): if end_date or start_date are not given then define it

            Returns: 
                dataframe (time-series data); the method returns daily prices of stocks for given time.
                The dataFrame will be returned as long-table inseted of wide-table. (Unpivoted/melted) 
        '''
        # calculate the start_date and end_date if it wasn't given directly
        t_date = datetime.today()

        if (start_date is None) and (end_date is None) and (interval is not None):
            end_date = t_date
            start_date = end_date - timedelta(interval)

        if (start_date is None) & (not end_date is None) & (not interval is None):
            start_date = end_date - timedelta(interval)

        if (not start_date is None) & (end_date is None) & (not interval is None):
            end_date = start_date + timedelta(interval)
            
            if end_date > t_date:
                end_date = t_date


        prices_df = yf.download(tickers, start_date, end_date)
        handle, m_isins, m_currenicies = self.check_nulls(tickers, prices_df, isins, currencies)

        if handle:
            handled_df = await self.handle_missing_equities(m_isins, m_currenicies)
            print(handled_df)

        prices_df_long = prices_df.stack(level=1, future_stack=True).reset_index()

        return prices_df


    async def handle_missing_equities(self, m_isins:list[str], m_currencies:list[str]):

        ib = IBKR()
        await ib.connect()

        if ib.ib.isConnected():
            print('Connection established!')


            try:
                contracts = await ib.fetchContracts(m_isins, m_currencies)
                handled_prices_df = await ib.downloadPrices(contracts) # hardcoded time range, to test the functionality
            finally:
                ib.disconect()

        return handled_prices_df

    
    def check_nulls(self, tickers:list[str], prices_df:pd.DataFrame, isins:list[str], currencies:list[str]):
        '''
            It receives the data frame with values and ticker-list. 
            And checks whether fetcher found the right symbol
        '''

        handle = False

        start_date = prices_df.index.min()
        end_date = prices_df.index.max()

        result_isins = []
        result_currencies = []

        for ticker, isin, currency  in zip(tickers, isins, currencies):

            if not prices_df['Close', ticker].notna().all():
                result_isins.append(isin)
                result_currencies.append(result_currencies)
                handle = True

        return handle, result_currencies, result_isins

