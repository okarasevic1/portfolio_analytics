import numbers as np
import pandas as pd
import duckdb

import os
os.path.join('/Users/okarasevic1/Documents/PortfolioAnalyzer/data_base/')

from trading_212_transactions import Trading212Transactions
from ibkr_transactions import IBKRTransactions
os.path.join('/Users/okarasevic1/Documents/PortfolioAnalyzer/data_base/extract_data/')
from queries import PortfolioQueries

with duckdb.connect() as con:

    ibkr_path_1_csv= '/Users/okarasevic1/Documents/PortfolioAnalyzer/data_base/file_data/U21204420.TRANSACTIONS.1Y(2).csv'
    trading_212_path_1_csv = '/Users/okarasevic1/Documents/PortfolioAnalyzer/data_base/file_data/transactions_212_*.csv'

    # create or connect database
    transactions_212 = Trading212Transactions(con)
    transactions_ibkr = IBKRTransactions(con)

    transactions_212.load_transactions(trading_212_path_1_csv)
    transactions_212.transform_into_statement()

    transactions_ibkr.load_transactions(ibkr_path_1_csv)

    con.sql('''
        SELECT * FROM ibkr_statement;
    ''').show()

    con.sql(PortfolioQueries.combine_statements).show(max_rows=50)
