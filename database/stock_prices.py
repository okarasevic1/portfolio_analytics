import pandas as pd 
import numpy as np
import yfinance as yf 
from yfinance.lookup import Lookup
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import time

class Prices:


    def fetch_prices(self, tickers:list[str], queries:list[str], start_date=None, end_date=None, interval=182):
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
        self.check_nulls(tickers, prices_df, queries)

        prices_df_long = prices_df.stack(level=1, future_stack=True).reset_index()

        return prices_df


    
    def check_nulls(self, tickers:list[str], prices_df:pd.DataFrame, names:list[str]):
        '''
            It receives the data frame with values and ticker-list. 
            And checks whether fetcher found the right symbol
        '''

        start_date = prices_df.index.min()
        end_date = prices_df.index.max()


        for ticker, name in zip(tickers, names):

            if prices_df['Close', ticker].notna().all() == False:
                print(ticker)
                right_ticker = self.qeury4search(ticker, name)

                ticker_prices = yf.download(right_ticker, start_date, end_date)
                time.sleep(1)
                ticker_prices.columns = pd.MultiIndex.from_tuples(
                    [(price, ticker) for price, _ in ticker_prices.columns],
                    names=prices_df.columns.names
                )

                prices_df.update(ticker_prices)


    def qeury4search(self, ticker:str, name:str):

        # query for searching the ticket
        response_df = Lookup(f'{ticker}').get_all(10)
        name = name.lower()
        # sort by score 

        response_df = response_df.assign(
            match_rate = lambda x: 
                x['shortName'].apply(
                    lambda value: SequenceMatcher(None, name.lower(), str(value).lower()).ratio()
                )
        )

        response_df['is_foreign'] = np.where(
            response_df.index.str.contains('.'), 
            True, 
            False
        )

        sorted_df = response_df.sort_values(by=['match_rate', 'rank'], ascending=False)

        if ticker == 'FUSD':
            print(sorted_df)

        # return the ticker of the first row: best-match
        right_ticekr = str(sorted_df.iloc[0].index)

        return right_ticekr

