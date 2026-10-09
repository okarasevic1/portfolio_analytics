import pandas as pd
import numpy as np
import duckdb
from queries import PortfolioQueries
from helpers.load_store import LoadStoreData
import os, errno


class IBKRTransactions:

    def __init__(self, con:duckdb.DuckDBPyConnection):
        self.con = con
        self.f_loader = LoadStoreData()
        self.parquet_storage = '/Users/okarasevic1/Documents/PortfolioAnalyzer/database/file_data/transactions_ibkr.parquet'


    def __extract_transactions(self, _file_path:str):
            new_name = 'transactions_ibkr_temp'
            p_path = self.f_loader.load_csv(_file_path, new_name) 
            return p_path

    
    def __calculate_statement(self):

        # check if table exists:
        check_tbl = self.con.sql('''
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables
                WHERE table_name = 'ibkr_transactions'
            ) as exist; 
        ''').to_df()

        if check_tbl['exist'].iloc[0] != True:
            self.load_transactions()

        # Transform transactions and create statement of the brocker 
        try: 
            self.con.sql(PortfolioQueries.ibkr_query_trans)

        except Exception as e:
            print(e)


    def silentremove(self, filename):
        try:
            os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT: 
                raise e


    def load_transactions(self, file_path_csv):
        """
            'ibkr' - Interactive Brockers, 
        """

        try:

            p_path = self.__extract_transactions(file_path_csv)

            self.con.sql(f'''
                CREATE OR REPLACE TABLE ibkr_transactions AS (
                    SELECT * FROM read_parquet('{p_path}')
                    ORDER BY Date
                );
            ''')

            # save all transactions into parquet
            self.silentremove(p_path)
            self.con.table('ibkr_transactions').to_parquet(self.parquet_storage)

            self.__calculate_statement()
                
                
        except duckdb.InvalidInputException as e:
            print(e)
            raise duckdb.InvalidInputException


    def update_transactions(self, file_path_csv):

        try: 

            p_path = self.__extract_transactions(file_path_csv)

            self.con.sql(f'''
                INSERT INTO ibkr_transactions BY NAME (
                    SELECT * FROM read_parquet('{p_path}')
                    ORDER BY Date
                );
            ''')

            # save all transactions into one file as reserve:
            self.con.table('ibkr_transactions').to_parquet(
                self.parquet_storage
            )

            self.silentremove(p_path)
            self.__calculate_statement()
                            
        except duckdb.InvalidInputException as e:
            print(e)
            raise duckdb.InvalidInputException
            

