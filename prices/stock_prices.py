import pandas as pd 
import numpy as np
import yfinance as yf 
from datetime import datetime, timedelta
from .ibkr_handler import IBKR
import asyncio


class PricesManager:

    def fetch_prices(self, instruments:list, 
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

        tickers = []
        isins = []
        currencies = []

        for instrument in instruments:

            tickers.append(instrument[0])
            isins.append(instrument[1])
            currencies.append(instrument[2])


        prices_df = yf.download(tickers, start_date, end_date)
        handle, missed_instruments = self.check_nulls(tickers, prices_df, isins, currencies)
        # drop columns with null values and transform it into long-table
        prices_df = prices_df.dropna(axis=1)
        prices_df_long = prices_df.stack(level=1, future_stack=True).reset_index()

        if handle:
            # calculate the interval for ibkr
            interval = datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)
            interval = interval.days
            handled_df = self.handle_missing_equities(missed_instruments, end_date, interval)

            prices_df_long = pd.concat([prices_df_long, handled_df]).reset_index()
            prices_df_long = prices_df_long.drop(['index'], axis=1)

        # preprocess data before DB
        prices_df_long['Date'] = pd.to_datetime(prices_df_long['Date']).dt.date
        prices_df_long = prices_df_long.sort_values(by='Date', ascending=False)

        return prices_df_long

    
    def check_nulls(self, tickers:list[str], prices_df:pd.DataFrame, isins:list[str], currencies:list[str]):
        '''
            It receives the data frame with values and ticker-list. 
            And checks whether fetcher found the right symbol
        '''

        handle = False

        result_instruments = []

        for ticker, isin, currency  in zip(tickers, isins, currencies):

            if not prices_df['Close', ticker].notna().all():
                result_instruments.append((isin, currency))
                handle = True

        return handle, result_instruments


    def handle_missing_equities(self, instruments:list, end_date, interval):

        ib = IBKR(end_date, interval)

        try:
            handled_prices_df = asyncio.run(ib.fetchMany(instruments))
            return handled_prices_df
        except Exception as e:
            print(e)
            raise e    

