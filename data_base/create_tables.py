import pandas as pd
import numpy as np
import duckdb

def create_portfolio_table(con:duckdb.DuckDBPyConnection, table_name):

    con.execute('''
        CREATE TABLE IF NOT EXISTS (?) (
        ticker VARCHAR, 
        name VARCHAR, 
        n_shares FLOAT, 
        gross_total DOUBLE,
        price_p_share FLOAT,
        PRIMARY KEY (ticker);
        )
    ''', parameters=[table_name])

def insert_into(con:duckdb.DuckDBPyConnection, table_name, values):

    con.execute('''
        INSERT INTO (?)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT DO NOTHING; 
    ''', parameters=[table_name, values])


with duckdb.connect('general_porfolio') as con:

    create_portfolio_table