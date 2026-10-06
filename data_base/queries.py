

class PortfolioQueries:

    # Transform transactions and create statement of the brocker IBKR
    ibkr_query_trans = '''
        CREATE OR REPLACE TABLE ibkr_statement AS (
            WITH market_transactions AS (
                SELECT * EXCLUDE(Quantity, Price, Commission),
                    try_cast(Quantity AS DOUBLE) as quantity, 
                    try_cast(Price AS FLOAT) as price, 
                    try_cast(Commission AS FLOAT) as commission,
                    "Price Currency" AS currency
                FROM ibkr_transactions 
                WHERE "Transaction Type" IN ('Buy', 'Sell')
            ), avg_prices AS (
                SELECT 
                    Symbol AS ticker, 
                    Description AS name,
                    round(sum(quantity ), 4) as total_shares,
                    round(sum("Gross Amount" * -1), 4) AS total_gross,
                    round(sum("Net Amount" * -1), 4) AS total_net,
                    round(sum(commission), 4) AS total_fees,
                    round(total_gross / total_shares, 4) AS avg_price,
                    round(total_net / total_shares, 4) AS net_avg_price,
                    currency, 
                    first(Date)::DATE AS appearance_date, 
                    last(Date)::DATE AS last_transaction,
                FROM market_transactions
                GROUP BY ticker, name, currency
            )
            SELECT *
            FROM avg_prices
            WHERE total_shares > 0
        );
    '''

    # Transform transactions and create statement of the brocker Trading 212
    trading_212_query_trans = '''
        CREATE OR REPLACE TABLE trading_212_statement AS (
            WITH market_transactions AS (
                SELECT 
                    "Time (UTC)" AS Date, 
                    Ticker AS ticker, "Name" as name,
                    "No. of shares" AS quantity, 'Price / share' AS price,
                    "Currency (Price / share)" as exhange_currency, 
                    if (
                        exhange_currency = 'USD',
                        "Gross Total" * rates, 
                        "Gross Total"
                    ) AS gross_total, 
                    coalesce("Currency conversion fee" * -1, 0) as commission,
                    gross_total - commission, 3 AS net_total
                FROM trading_212_transactions
                WHERE Action LIKE '%buy' OR Action LIKE '%sell'
                ORDER BY Date
            ), avg_prices AS (
                SELECT 
                    ticker, name, 
                    round(sum(quantity), 4) AS total_shares, 
                    round(sum(gross_total), 4) AS total_gross, 
                    round(sum(net_total), 4) AS total_net, 
                    sum(commission) AS total_fees, 
                    round(total_gross / total_shares, 4) AS avg_price, 
                    round(total_net / total_shares, 4) AS net_avg_price, 
                    exhange_currency AS currency,
                    first(Date)::DATE AS appearance_date, 
                    last(Date)::DATE AS last_transaction
                FROM market_transactions
                GROUP BY ticker, name, exhange_currency
            ) 
            SELECT * FROM avg_prices
            WHERE total_shares > 0
        );
    '''

    combine_statements = '''
            WITH opened_pos AS (
                SELECT * FROM trading_212_statement
                UNION ALL BY NAME
                SELECT * FROM ibkr_statement
            ), calc_tbl AS (
                SELECT
                    replace(ticker, '.', ' ') AS l_ticker,
                    sum(total_shares) AS total_shares_g, 
                    sum(total_gross) AS total_gross_g, 
                    sum(total_net) AS total_net_g,
                    sum(total_fees) AS total_fees_g,
                    round(total_gross_g / total_shares_g) AS avg_price, 
                    round(total_net_g / total_shares_g) AS net_avg_price, 
                    currency, 
                    first(appearance_date) AS appearance_date,
                    last(last_transaction) AS last_transaction
                FROM opened_pos
                GROUP BY l_ticker, currency
                ORDER BY total_gross_g DESC
            )
            SELECT * FROM calc_tbl;
    '''