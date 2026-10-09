import duckdb
import os
os.path.join('/Users/okarasevic1/Documents/PortfolioAnalyzer/database/')

from trading_212_transactions import Trading212Transactions
from ibkr_transactions import IBKRTransactions

os.path.join('/Users/okarasevic1/Documents/PortfolioAnalyzer/database/extract_data/')
from queries import PortfolioQueries



class MainDB:

    def __init__(self, con:duckdb.DuckDBPyConnection):
        self.con = con
        self.ibkr = IBKRTransactions(con)
        self.tr212 = Trading212Transactions(con)

    
    def load_transactions(self, reg_pattern:str, brocker:str):
        '''
            The statement will be generated automaticaly after the transactions were loaded, 
            and in the end it will update or create view with info from two brockers
        '''

        tbl_name = 'ibkr_transactions' if brocker == 'ibkr' else 'trading_212_transactions'
        
        # checking the existance of the table
        bool_tbl = self.con.sql(f'''
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = '{tbl_name}'
            ) as exist;
        ''').to_df()['exist'].iloc[0]

        # if it exists -> then we need to update it
        if bool_tbl:
            print('The table already exists!')
            return None
        
        if brocker == 'ibkr':
            self.ibkr.load_transactions(reg_pattern)

        elif brocker == 'trading_212':
            self.tr212.load_transactions(reg_pattern)

        elif brocker == 'both':
            # split the pathes: ibkr is first and trading 212 is second
            bs_pathes = reg_pattern.split() 
            self.ibkr.load_transactions(bs_pathes[0])
            self.tr212.load_transactions(bs_pathes[1])


    def update_transactions(self, file_path, brocker:str):
            '''
                Insert new transactions from the file into corresponding brocker account;
                It automaticaly updates the current statement table with corresponding brocker
            '''
            
            tbl_name = 'ibkr_transactions' if brocker == 'ibkr' else 'trading_212_transactions'

            # checking the existance of the table
            bool_tbl = self.con.sql(f'''
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = '{tbl_name}'
                ) as exist;
            ''').to_df()['exist'].iloc[0]

            if bool_tbl:
                if brocker == 'ibkr':
                    self.ibkr.update_transactions(file_path_csv=file_path)
        
                elif brocker == 'trading_212':
                    self.tr212.update_transactions(csv_transaction_path=file_path)

    
    def create_statements_views(self):

        try:
            self.con.sql(PortfolioQueries.combine_statements)
        except Exception as e:
            raise e





