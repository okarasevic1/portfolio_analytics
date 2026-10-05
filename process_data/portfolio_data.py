import pandas as pd
from curl_cffi import requests
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

def parse_data(file_path_t212:str, file_path_ibkr:str):
    
    # Process data from Trading212 portfolio
    df_trading212 = pd.read_csv(file_path_t212)

    df_trading212['Time'] = pd.to_datetime(df_trading212['Time'])
    df_trading212 = df_trading212.sort_values('Time')
    df_trading212 = df_trading212.set_index('Time')
    df_trading212['Action'] = df_trading212['Action'].replace({'Limit buy': 'Buy', 'Market buy':'Buy'})

    df_trading212 = df_trading212[['Ticker', 'Name', 'No. of shares', 'Price / share', 'Gross Total', 'Exchange rate']]
    df_trading212['Gross Total'] = df_trading212['Gross Total'] * df_trading212['Exchange rate']
    
    df_trading212 = (df_trading212.groupby('Ticker').agg({
          'Name': 'first',
          'No. of shares': 'sum',
          'Gross Total': 'sum'
          }))
    
    df_trading212['Price / share'] = (df_trading212['Gross Total']/ df_trading212['No. of shares'])

    # Process data from IBKR portfolio
    df_ibkr = pd.read_csv(file_path_ibkr, index_col='ticker')
    df_ibkr.index.name = 'Ticker'
    df_ibkr = df_ibkr.rename({'shares' : 'No. of shares', 'avg_price' : 'Price / share'}, axis=1)

    df_ibkr['Gross Total'] = df_ibkr['No. of shares'] * df_ibkr['Price / share']
    
    df_ibkr['Name'] = '-'

    df_ibkr = df_ibkr.iloc[:, [3, 0, 2, 1]]

    # Concatenate two portfolio in one
    df_portfolio = pd.concat([df_trading212, df_ibkr])

    df_portfolio = (df_portfolio.groupby('Ticker').agg({
        'Name':'first',
        'No. of shares':'sum',
        'Gross Total':'sum'
    }))

    df_portfolio['Price/share'] = df_portfolio['Gross Total'] / df_portfolio['No. of shares']
    df_portfolio.to_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /overall_portfolio.csv', sep=',')

    return df_portfolio


def create_profile(path):
    session = requests.Session(impersonate="chrome")
    portfolio = pd.read_csv(path)
    portfolio[['No. of shares', 'Gross Total', 'Price/share']] = portfolio[['No. of shares', 'Gross Total', 'Price/share']].astype(float)

    final_statement = []

    print("\nFetching live market data...")
    for idx, row in portfolio.iterrows():

        ticker = row['Ticker']
        
        if row['No. of shares'] <= 0:
            continue
        
        ticker_info = yf.Ticker(ticker, session=session).info

        # Process all asset types in a single, clean loop
        asset_type = ticker_info.get('typeDisp', 'Unknown')

        # Extract metrics safely using .get() with fallback defaults
        live_price = ticker_info.get('regularMarketPrice', row['Price/share'])
                
        total_value = row['No. of shares'] * live_price
        gross_profit = total_value - (row['Price/share'] * row['No. of shares'])

        pe_ratio = ticker_info.get('trailingPE', 0.0)

        final_statement.append({
            'Ticker': ticker,
            'Name': ticker_info.get('longName', '-'), 
            'Sector': ticker_info.get('sector', 'ETF' if asset_type == 'ETF' else 'N/A'),
            'Industry': ticker_info.get('industry', 'ETF' if asset_type == 'ETF' else 'N/A'),
            'Type': asset_type if asset_type != 'Unknown' else 'N/A',
            'No. of shares': round(row['No. of shares'], 4),
            'Avg. Price': round(row['Price/share'], 4),
            'Gross Total': round(total_value, 3),
            'Gross P/L': gross_profit,
            'Exchange': ticker_info.get('exchange', '-'),
            'PE': pe_ratio if pe_ratio is not None else 0.0
        })
        
    # 4. Display clean statement
    statement_df = pd.DataFrame(final_statement)
    portfolio_value = statement_df['Gross Total'].sum()

    print('Portfolio Value in USD: ', portfolio_value)

    statement_df['weightInPortfolio'] = round(statement_df['Gross Total']/portfolio_value, 3) * 100
    statement_df.to_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /portfolio_stmnt.csv')

    return statement_df


def fetch_prices_hisotry(tickers:list, years, benchmark:str='SPY'): 
    session = requests.Session(impersonate='chrome')

    # end = datetime(year=2025, month=7, day=24)
    end = datetime.today()
    start = end - timedelta(days=(365*years))

    download_list = tickers + [benchmark] 
    
    data_history = yf.download(download_list, start=start, end=end, session=session)['Close']

    data_history.to_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/prices_history.csv', sep=',')

    return data_history


def portfolio_prices(data_df, shares, benchmark): 
    
    asset_prices_only = data_df.drop(labels=benchmark, axis=1)
    asset_prices_only = asset_prices_only.ffill()

    portfolio_history = asset_prices_only.mul(shares, axis=1).sum(axis=1)

    portfolio_prices_history = pd.DataFrame({
        'Portfolio': pd.Series(data=portfolio_history, index=data_df.index)
    })

    portfolio_prices_history.to_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/portfolio_prices_history.csv')