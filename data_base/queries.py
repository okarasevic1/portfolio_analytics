

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
                    sum("Gross Amount") FILTER ("Gross Amount" < 0) OVER w AS roll_gross,
                    sum("Net Amount") FILTER ("Net Amount" < 0) OVER w AS roll_net,
                    sum(quantity) FILTER(quantity > 0) OVER w AS roll_shares,
                    round(roll_gross / roll_shares, 3) AS net_avg_price,
                    round(roll_net / roll_shares, 3) AS avg_price
                FROM market_transactions
                WINDOW w AS (
                    PARTITION BY ticker
                    ORDER BY Date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )
            ), ibkr_statement AS (
                SELECT 
                    mt.Symbol AS ticker,
                    mt.Description AS name,
                    sum(quantity) as total_shares,
                    sum("Gross Amount" * -1) AS total_gross,
                    sum("Net Amount" * -1) AS total_net,
                    sum(commission) AS total_fees,
                    last(avg_p.net_avg_price) AS net_avg_price,
                    last(avg_p.avg_price) AS avg_price,
                    currency,
                    first(Date) AS appearance_date,
                    last(Date) AS last_transaction
                FROM market_transactions mt
                JOIN avg_prices avg_p
                    ON mt.Symbol = avg_p.ticker
                GROUP BY mt.Symbol, name, currency
            )
            SELECT *
            FROM ibkr_statement
            WHERE total_shares > 0
        );
    '''

    # Transform transactions and create statement of the brocker Trading 212
    trading_212_query_trans = '''
        CREATE OR REPLACE TABLE trading_212_statement AS (
            WITH market_transactions AS (
                SELECT "Time (UTC)" AS Date, Ticker AS ticker, Name as name,
                    "No. of shares" AS quantity, 'Price / share' AS price,
                    "Currency (Price / share)" as exhange_currency, 
                    round(
                        if("Currency (Gross Total)" = 'USD',
                            "Gross Total",
                            "Gross Total" * rates) 
                    ) AS gross_total,
                    coalesce("Currency conversion fee" * -1, 0) as commission,
                    round(gross_total - commission, 3) AS net_total
                FROM trading_212_transactions
                WHERE Action LIKE '%buy' OR Action LIKE '%sell'
                ORDER BY Date
            ), avg_prices AS (
                SELECT 
                    ticker, 
                    sum(quantity) FILTER(quantity > 0) OVER w AS roll_shares, 
                    sum(gross_total) FILTER(gross_total > 0) OVER w AS roll_gross, 
                    sum(net_total) FILTER(net_total > 0) OVER w AS roll_net,
                    round(roll_gross / roll_shares, 3) as net_avg_price, 
                    round(roll_net / roll_shares, 3) as avg_price
                FROM market_transactions
                WINDOW w AS (
                    PARTITION BY ticker
                    ORDER BY Date 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )
            ), trading_212_stmnt AS (
                SELECT 
                    mt.ticker, name,
                    sum(quantity) as total_shares,
                    sum(gross_total) AS total_gross,
                    sum(net_total) AS total_net,
                    sum(commission) AS total_fees,
                    last(avg_p.net_avg_price) AS net_avg_price,
                    last(avg_p.avg_price) AS avg_price,
                    mt.exhange_currency,
                    first(Date)::DATE AS appearance_date,
                    last(Date)::DATE AS last_transaction
                FROM market_transactions mt
                JOIN avg_prices avg_p
                    ON mt.ticker = avg_p.ticker
                GROUP BY mt.ticker, name, mt.exhange_currency
            )
            SELECT * FROM trading_212_stmnt
    );
    '''