import pandas as pd
import numpy as np
import duckdb
from queries import PortfolioQueries
from extract_data.load_store import LoadStoreData


class IBKRTransactions:

    def __init__(self, con:duckdb.DuckDBPyConnection):
        self.con = con
        self.f_loader = LoadStoreData()


    def __set_key(self, transactions_df:pd.DataFrame, column_name:str):

        # generate own transaction_id 
        ids = transactions_df['Transaction Type'].map(str) + '_' + transactions_df['Date'].map(str) + '_' + transactions_df['Symbol'].map(str)
        transactions_df[column_name] = ids

        return transactions_df



    def load_transactions(self, file_path_csv):
        """
            'ibkr' - Interactive Brockers, 
        """

        try:

            p_path = self.f_loader.load_csv(file_path_csv, 'transactions_ibkr_1')

            transactions_df = self.con.sql(f'''
                SELECT * FROM read_parquet('{p_path}')
            ''').to_df()


            # set primary key
            # transactions_df = self.__set_key(transactions_df, 'ID')

            self.con.sql('''
                CREATE OR REPLACE TABLE ibkr_transactions AS (
                    SELECT * FROM transactions_df
                    ORDER BY Date
                );
            ''')

            # self.con.sql('''
            #     ALTER TABLE ibkr_transactions
            #     ADD PRIMARY KEY ("ID");
            # ''')
                
        except duckdb.InvalidInputException as e:
            print(e)
            raise duckdb.InvalidInputException


    def calculate_statement(self):

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
