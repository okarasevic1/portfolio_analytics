import pandas as pd
import duckdb 
from prices.stock_prices import PricesManager
from queries import PortfolioQueries


class PricesDB:

    def __init__(self, con:duckdb.DuckDBPyConnection):

        self.con = con


    def quotesStatement(self):

        # Create snapshot (ticker, isin, currency) from statement 
        instruments_df = self.con.sql(PortfolioQueries.snapshot_instruments).to_df()

        instruments_list = []

        for i, row in instruments_df.iterrows():
            instrument = (row['ticker'], row['ISIN'], row['currency'])
            instruments_list.append(instrument)

        return instruments_list


    def loadPrices(self, instruments:list, start_date, end_date):

        price_man = PricesManager()

        try:
            prices_df = price_man.fetch_prices(
                instruments=instruments, start_date=start_date, end_date=end_date
            )
            return prices_df

        except ConnectionError:
            raise ConnectionError('Check connection with Trader Workstation')


    def history2table(self, prices_df:pd.DataFrame):

        if len(prices_df) > 0:
            self.con.sql('''
                CREATE OR REPLACE TABLE history AS (
                    SELECT * FROM prices_df
                );
            ''')

        else:
            raise ValueError
