from transactions import MainDB
import duckdb

with duckdb.connect() as connector:

    cl_db = MainDB(con=connector)
    cl_db.load_transactions('/Users/okarasevic1/Documents/PortfolioAnalyzer/database/file_data/U21204420.TRANSACTIONS*.csv', 'ibkr')
    cl_db.load_transactions('/Users/okarasevic1/Documents/PortfolioAnalyzer/database/file_data/transactions_212_*.csv', 'trading_212')
    cl_db.create_statements_views()

    connector.sql('SHOW TABLES').show()
    connector.sql('SELECT * FROM portfolio_statement LIMIT 5').show()

    connector.close()