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


    def __extract_transactions(self, _file_path:str):

        p_path = self.f_loader.load_csv(_file_path, 'transactions_212_1') 

        temp_transactions_df = self.con.sql(f'''
            SELECT * FROM read_parquet('{p_path}');
        ''').to_df()

        return temp_transactions_df


    def __append_exch_rates(self, temp_tr:pd.DataFrame, curr:list):

        curr_str = ''.join(f'{c},' for c in curr)
        curr_str = curr_str[:-1]

        # temp_tr -> pd.DataFrame type and get values directly  
        self.con.execute(f'''
            CREATE OR REPLACE TABLE trading_212_transactions AS (
                WITH ex_r AS (
                    SELECT * FROM ex_rates
                ), added_rates AS (
                    SELECT 
                        tr.*, ex.rates as rates
                    FROM temp_tr AS tr
                    JOIN ex_r AS ex
                        ON tr."Time (UTC)"::DATE = ex.Date
                            AND tr."Currency (Gross Total)" = ex.currency
                ) SELECT * FROM added_rates
            );
        ''').commit()

    def __set_key(self, table_name:str, column_name:str): 

            # check whether column contains null-values
            values_df = self.con.sql(f'''
                SELECT "{column_name}" as p_key FROM "{table_name}"
            ''').to_df()

            # create own ID where it is empty
            if values_df['p_key'].isnull().any():
                self.con.sql(f'''
                    UPDATE "{table_name}"
                    SET "{column_name}" = concat("Action", "Time (UTC)"::DATE, "ISIN")
                    WHERE "{column_name}" IS NULL;
                ''')

            # alter table: set primary key
            self.con.sql(f'''
                ALTER TABLE "{table_name}"
                ADD PRIMARY KEY ("{column_name}")
            ''')


    def load_transactions(self, file_path):
        """
            load all transactions from brocker into the db:
            'trading_212' - Trading 212
        """

        try:

            # load transactions from the parquet 
            temp_transactions = self.__extract_transactions(file_path)

            list_curr = temp_transactions['Currency (Gross Total)'].drop_duplicates().tolist()
            
            start_date = temp_transactions['Time (UTC)'].min().date()
            end_date = temp_transactions['Time (UTC)'].max().date()

            # fetch exhange rates
            ex_rates_df = self.convert_curr.load_exchange_rates(list_curr, start_date, end_date)

            self.con.sql('''
                CREATE OR REPLACE TABLE ex_rates AS (
                    SELECT * FROM ex_rates_df
                ); 
            ''')

            # transform transactions table 
            self.__append_exch_rates(temp_tr=temp_transactions, curr=list_curr)

            tbl_name = 'trading_212_transactions'
            cl_key = 'ID'

            self.__set_key(tbl_name, cl_key)

            
                
        except duckdb.InvalidInputException as e:
            print(e)
            raise duckdb.InvalidInputException


    def transform_into_statement(self):

        tbl_name = 'trading_212_transactions'

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


    # def append_transactions(self, brocker, transaction_path):

    #     if brocker == 'ibkr':
    #         pass
    #     elif brocker == 'trading_212':

    #         convert_curr = ConvertCurrncies(
    #             con=self.con,
    #             file_path=transaction_path
    #         )

    #         convert_curr.insert_new_transactions()
            
    #         # update statement after adding new transactions 
    #         self.transform_into_statement('trading_212')

    #     else:
    #         raise ValueError