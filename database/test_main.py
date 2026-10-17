from transactions import MainDB
import duckdb
from pricesDB import PricesDB

with duckdb.connect() as connector:

    cl_db = MainDB(con=connector)
    price_db = PricesDB(con=connector)

    cl_db.load_transactions('/Users/okarasevic1/Documents/PortfolioAnalyzer/database/file_data/U21204420.TRANSACTIONS*.csv', 'ibkr')
    cl_db.load_transactions('/Users/okarasevic1/Documents/PortfolioAnalyzer/database/file_data/transactions_212_*.csv', 'trading_212')
    cl_db.create_statements_views()
    portfolio_df = cl_db.pull_data(brocker='both', as_df=True)

    print(portfolio_df.head())

    connector.sql('SHOW TABLES').show()
    connector.sql('SELECT * FROM portfolio_statement LIMIT 5').show()


    instruments = price_db.quotesStatement()

    prices = price_db.loadPrices(instruments, '2026-01-01', '2026-10-01')
    price_db.history2table(prices_df=prices)

    connector.sql('SHOW TABLES;').show()

    connector.sql('''
        SELECT * FROM history
        USING SAMPLE 5;
    ''').show()

    connector.close()