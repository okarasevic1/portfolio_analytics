import pandas as pd
import numpy as np
import duckdb
from extract_data.convert_currency import ConvertCurrncies
from queries import PortfolioQueries
from extract_data.load_store import LoadStoreData


class Trading212Transactions:

    def __init__(self, con:duckdb.DuckDBPyConnection):
        self.con = con
        self.convert_curr = ConvertCurrncies()
        self.f_loader = LoadStoreData()


    def __extract_transactions(self, _file_path:str, new_name='transactions_212_1'):

        p_path = self.f_loader.load_csv(_file_path, new_name) 

        temp_transactions_df = self.con.sql(f'''
            SELECT * FROM read_parquet('{p_path}');
        ''').to_df()

        return temp_transactions_df


    def __transform_into_statement(self):

        # check if table exists:
        check_tbl = self.con.sql(f'''
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables
                WHERE table_name = 'trading_212_transactions'
            ) as exist; 
        ''').to_df()['exist'].iloc[0]

        if check_tbl != True:
            self.load_transactions()

        # Transform transactions and create statement of the brocker 
        try: 
            self.con.sql(PortfolioQueries.trading_212_query_trans)

        except Exception as e:
            print(e)
            raise Exception


    def load_transactions(self, file_path):
        """
            load all transactions from brocker into the db:
            'trading_212' - Trading 212
        """

        tbl_name = 'trading_212_transactions'

        try:
            # load transactions from the parquet 
            transactions_df = self.__extract_transactions(file_path)

            self.con.sql(f'''
                CREATE OR REPLACE TABLE "{tbl_name}" AS (
                    SELECT * FROM transactions_df
                );
            ''')

            list_curr = transactions_df['Currency (Gross Total)'].drop_duplicates().tolist()
            start_date = transactions_df['Time (UTC)'].min().date()
            end_date = transactions_df['Time (UTC)'].max().date()
            # fetch exhange rates
            ex_rates_df = self.convert_curr.load_exchange_rates(list_curr, start_date, end_date)

            self.con.sql('''
                CREATE OR REPLACE TABLE ex_rates AS (
                    SELECT * FROM ex_rates_df
                ); 
            ''')

            self.__transform_into_statement()
        
        except duckdb.InvalidInputException as e:
            print(e)
            raise duckdb.InvalidInputException


    def update_transactions(self, csv_transaction_path):

        try: 
            transactions_df = self.__extract_transactions(csv_transaction_path, 'transactions_212_2')

            list_curr = transactions_df['Currency (Gross Total)'].drop_duplicates().tolist()
            
            start_date = transactions_df['Time (UTC)'].min().date()
            end_date = transactions_df['Time (UTC)'].max().date()

            # fetch exhange rates
            ex_rates_df = self.convert_curr.load_exchange_rates(list_curr, start_date, end_date)

            self.con.sql('''
                INSERT INTO ex_rates (
                    SELECT * FROM ex_rates_df
                );
            ''')

            transactions_df['ID'] = np.where(
                transactions_df['ID'].isna() == True, 
                f'{transactions_df['Action']}{transactions_df['Time (UTC)']}{transactions_df['ISIN']}',
                transactions_df['ID']
            )

            self.con.sql('''
                INSERT INTO trading_212_transactions BY NAME (
                    SELECT * FROM transactions_df
                );
            ''')
            
            self.__transform_into_statement()


        except duckdb.InvalidInputException as e:
            print(e)
            raise duckdb.InvalidInputException




