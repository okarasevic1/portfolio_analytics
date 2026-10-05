CREATE OR REPLACE TABLE ibkr_transactions AS (
    SELECT * EXCLUDE ("Transaction History", Header, Account)
    FROM read_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /data_base/file_data/U21204420.TRANSACTIONS.1Y(2).csv')
);

CREATE
OR
REPLACE
TABLE ibkr_transactions (
    Date TIMESTAMP,
    Description VARCHAR,
    "Transaction Type" VARCHAR,
    Symbol VARCHAR,
    Quantity FLOAT,
    Price DOUBLE,
    "Price Currency" VARCHAR,
    "Gross Amount" DOUBLE,
    Commission FLOAT,
    "Net Amount" DOUBLE
);


INSERT INTO ibkr_transactions (
    Date,
    Description,
    "Transaction Type",
    Symbol,
    Quantity,
    Price,
    "Price Currency",
    "Gross Amount",
    Commission,
    "Net Amount"
)
VALUES
('2026-01-05', 'APPLE INC', 'Buy', 'AAPL', 0.1500, 248.50, 'USD', -37.275000, -0.372750, -37.647750),
('2026-01-18', 'APPLE INC', 'Buy', 'AAPL', 0.1000, 252.30, 'USD', -25.230000, -0.252300, -25.482300),
('2026-02-03', 'APPLE INC', 'Sell', 'AAPL', -0.0800, 261.75, 'USD', 20.940000, -0.209400, 20.730600),
('2026-02-20', 'APPLE INC', 'Buy', 'AAPL', 0.2000, 267.10, 'USD', -53.420000, -0.534200, -53.954200),

('2026-01-07', 'NVIDIA CORP', 'Buy', 'NVDA', 0.3000, 141.20, 'USD', -42.360000, -0.423600, -42.783600),
('2026-01-22', 'NVIDIA CORP', 'Buy', 'NVDA', 0.1500, 146.80, 'USD', -22.020000, -0.220200, -22.240200),
('2026-02-11', 'NVIDIA CORP', 'Sell', 'NVDA', -0.2000, 153.40, 'USD', 30.680000, -0.306800, 30.373200),
('2026-03-02', 'NVIDIA CORP', 'Buy', 'NVDA', 0.2500, 157.90, 'USD', -39.475000, -0.394750, -39.869750),

('2026-01-10', 'MICROSOFT CORP', 'Buy', 'MSFT', 0.0800, 421.50, 'USD', -33.720000, -0.337200, -34.057200),
('2026-01-29', 'MICROSOFT CORP', 'Buy', 'MSFT', 0.0600, 428.90, 'USD', -25.734000, -0.257340, -25.991340),
('2026-02-17', 'MICROSOFT CORP', 'Sell', 'MSFT', -0.0500, 435.60, 'USD', 21.780000, -0.217800, 21.562200),

('2026-01-14', 'AMAZON.COM INC', 'Buy', 'AMZN', 0.1200, 224.80, 'USD', -26.976000, -0.269760, -27.245760),
('2026-02-01', 'AMAZON.COM INC', 'Buy', 'AMZN', 0.1000, 231.40, 'USD', -23.140000, -0.231400, -23.371400),
('2026-02-25', 'AMAZON.COM INC', 'Sell', 'AMZN', -0.0700, 237.90, 'USD', 16.653000, -0.166530, 16.486470),

('2026-01-20', 'META PLATFORMS INC', 'Buy', 'META', 0.0400, 612.50, 'USD', -24.500000, -0.245000, -24.745000),
('2026-02-05', 'META PLATFORMS INC', 'Buy', 'META', 0.0300, 625.80, 'USD', -18.774000, -0.187740, -18.961740),
('2026-02-19', 'META PLATFORMS INC', 'Sell', 'META', -0.0200, 641.30, 'USD', 12.826000, -0.128260, 12.697740),

('2026-01-25', 'TESLA INC', 'Buy', 'TSLA', 0.2000, 398.20, 'USD', -79.640000, -0.796400, -80.436400),
('2026-02-12', 'TESLA INC', 'Buy', 'TSLA', 0.1000, 371.50, 'USD', -37.150000, -0.371500, -37.521500),
('2026-03-05', 'TESLA INC', 'Sell', 'TSLA', -0.1500, 389.70, 'USD', 58.455000, -0.584550, 57.870450);

CREATE
OR
REPLACE
TABLE ibkr_statement AS (
    WITH
        market_transactions AS (
            SELECT
                * EXCLUDE (Quantity, Price, Commission),
                try_cast (Quantity AS FLOAT) AS quantity,
                try_cast (Price AS DOUBLE) AS price,
                try_cast (Commission AS FLOAT) AS commission,
                "Price Currency" AS currency
            FROM ibkr_transactions
            WHERE
                "Transaction Type" in ('Buy', 'Sell')
        ),
        avg_prices AS (
            SELECT
                Symbol AS ticker,
                sum("Gross Amount" * -1) FILTER ("Gross Amount" < 0) OVER w AS roll_gross,
                sum("Net Amount" * -1) FILTER ("Net Amount" < 0) OVER w AS roll_net,
                sum(quantity) FILTER (quantity > 0) OVER w AS roll_shares,
                round(roll_gross / roll_shares, 3) AS net_avg_price,
                round(roll_net / roll_shares, 3) AS avg_price
            FROM market_transactions
            WINDOW w AS (
                    PARTITION BY
                        ticker
                    ORDER BY Date ROWS BETWEEN UNBOUNDED PRECEDING
                        AND CURRENT ROW
                )
        ),
        ibkr_statement AS (
            SELECT
                mt.Symbol AS ticker,
                sum(quantity) as total_shares,
                sum("Gross Amount" * -1) AS total_gross,
                sum("Net Amount" * -1) AS total_net,
                sum(commission) AS total_fees,
                last (avg_p.net_avg_price) AS net_avg_price,
                last (avg_p.avg_price) AS avg_price,
                currency,
                first (Date) AS appearance_date,
                last (Date) AS last_transaction
            FROM
                market_transactions mt
                JOIN avg_prices avg_p ON mt.Symbol = avg_p.ticker
            GROUP BY
                mt.Symbol,
                mt.currency
        )
    SELECT *
    FROM ibkr_statement
    WHERE
        total_shares > 0
);

CREATE
OR
REPLACE
TABLE trading_212_transactions AS (
    SELECT *
    FROM read_parquet(
            '/Users/okarasevic1/Documents/Portfolio Analyzer /data_base/extract_data/transactions.parquet'
        )
);

CREATE OR REPLACE TABLE trading_212_statement AS (
    WITH market_transactions AS (
        SELECT "Time (UTC)" AS Date, Ticker AS ticker, 
            "No. of shares" AS quantity, 'Price / share' AS price,
            "Currency (Price / share)" as currency, 
            gross_total_usd AS gross_total, coalesce("Currency conversion fee" * -1, 0) as commission,
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
            mt.ticker,
            sum(quantity) as total_shares,
            sum(gross_total) AS total_gross,
            sum(net_total) AS total_net,
            sum(commission) AS total_fees,
            last(avg_p.net_avg_price) AS net_avg_price,
            last(avg_p.avg_price) AS avg_price,
            mt.currency,
            first(Date)::DATE AS appearance_date,
            last(Date)::DATE AS last_transaction
        FROM market_transactions mt
        JOIN avg_prices avg_p
            ON mt.ticker = avg_p.ticker
        GROUP BY mt.ticker, mt.currency
    )
    SELECT * FROM trading_212_stmnt
);

CREATE OR REPLACE VIEW portfolio AS (
    WITH
        combined_stmnts AS (
            SELECT *
            FROM ibkr_statement
            UNION ALL
            BY NAME
            SELECT *
            FROM trading_212_statement
        )
    SELECT
        ticker,
        sum(total_shares) AS holding_shares,
        sum(total_gross) AS total_gross,
        sum(total_net) AS net_position,
        sum(total_fees) AS total_fees,
        round(
            net_position / holding_shares,
            3
        ) as avg_price,
        currency
    FROM combined_stmnts
    GROUP BY
        ticker,
        currency
);