import pandas as pd
import numpy as np
import duckdb
from helpers.convert_currency import ConvertCurrncies
from queries import PortfolioQueries
from helpers.load_store import LoadStoreData
import os
import errno


class Trading212Transactions:

    def __init__(self, con:duckdb.DuckDBPyConnection):
        self.con = con
        self.convert_curr = ConvertCurrncies()
        self.f_loader = LoadStoreData()
        self.parquet_storage = '/Users/okarasevic1/Documents/PortfolioAnalyzer/database/file_data/transactions_212.parquet'
        self.tbl_transactions = 'trading_212_transactions'


    def __extract_transactions(self, _file_path:str):

        new_name = 'transactions_212_temp'
        p_path = self.f_loader.load_csv(_file_path, new_name) 

        return p_path


    def __transform_into_statement(self):

        # check if table exists:
        check_tbl = self.con.sql(f'''
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables
                WHERE table_name = '{self.tbl_transactions}'
            ) as exist; 
        ''').to_df()['exist'].iloc[0]

        if check_tbl != True:
            raise ValueError

        # Transform transactions and create statement of the brocker 
        try: 
            self.con.sql(PortfolioQueries.trading_212_query_trans)

        except Exception as e:
            print(e)
            raise Exception


    def silentremove(self, filename):
        try:
            os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT: 
                raise e


    def load_transactions(self, file_path):
        """
            load all transactions from brocker into the db:
            'trading_212' - Trading 212
        """

        try:
            # load transactions from the parquet 
            temp_parquet_path = self.__extract_transactions(file_path)

            try:
                self.con.sql(f'''
                    CREATE OR REPLACE TABLE "{self.tbl_transactions}" AS (
                        SELECT * FROM read_parquet('{temp_parquet_path}')
                    );
                ''')

                self.con.table(self.tbl_transactions).to_parquet(self.parquet_storage) # rewrite storage with all transactions 

            except duckdb.ParserException as e:
                print(e)
                raise e
                

            list_curr = self.con.sql(f'''
                SELECT DISTINCT("Currency (Gross Total)") as curr
                FROM "{self.tbl_transactions}"
            ''').to_df()['curr'].to_list()
            start_date = pd.read_parquet(temp_parquet_path)['Time (UTC)'].min().date()
            end_date = pd.read_parquet(temp_parquet_path)['Time (UTC)'].max().date()
            
            self.silentremove(temp_parquet_path) # remove temporary file 

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
            # load transactions from the parquet 
            temp_parquet_path = self.__extract_transactions(csv_transaction_path)


            list_curr = pd.read_parquet(temp_parquet_path)['Currency (Gross Total)']\
                .unique().tolist()
            start_date = pd.read_parquet(temp_parquet_path)['Time (UTC)'].min().date()
            end_date = pd.read_parquet(temp_parquet_path)['Time (UTC)'].max().date()

            # fetch exhange rates
            ex_rates_df = self.convert_curr.load_exchange_rates(list_curr, start_date, end_date)

            self.con.sql('''
                INSERT INTO ex_rates (
                    SELECT * FROM ex_rates_df
                );
            ''')

            self.con.sql(f'''
                INSERT INTO "{self.tbl_transactions}" BY NAME (
                    SELECT * FROM read_parquet('{temp_parquet_path}')
                );
            ''')

            self.silentremove(temp_parquet_path) # remove temporary file 

            self.con.table(self.tbl_transactions).to_parquet(self.parquet_storage)
            self.__transform_into_statement()


        except duckdb.InvalidInputException as e:
            print(e)
            raise duckdb.InvalidInputException




