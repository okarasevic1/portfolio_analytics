import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from curl_cffi import requests

plt.rcParams.update({'font.size': 10})
plt.rcParams.update({'xtick.labelsize': 8})

def annualized_volatility(history_prices_path, portfolio_path, benchmark):

    # Load dataFrame of prices 
    history_prices = pd.read_csv(history_prices_path)
    history_prices['Date'] = pd.to_datetime(history_prices['Date'])
    history_prices = history_prices.set_index('Date')

    # Get only last year 
    last_1y = history_prices.tail(252)
    last_1y.ffill()

    # returns of each stock
    df_returns = last_1y.pct_change().dropna()

    # load portfolio to get Tickers 
    portfolio = pd.read_csv(portfolio_path, index_col='Ticker')
    tickers = portfolio.index.values.tolist()

    # Calculate the Stardard Devaition and Annuilized Volatility for each stock
    daily_std = df_returns[tickers].std()
    annualized_volatility = (daily_std * np.sqrt(252)) * 100
    
    # update DataFrame 
    portfolio_modified = portfolio.copy()
    portfolio_modified['Volatility (1y)'] = annualized_volatility

    print(portfolio_modified)

    # Calculate for benchmark and compare 
    benchmark_df = last_1y[benchmark]
    benchmark_returns = benchmark_df.pct_change().dropna()
    benchmark_daily_devaition = benchmark_returns.std()
    benchmark_volatility = (benchmark_daily_devaition * np.sqrt(252)) * 100

    print(f'Annulized Volatility of benchmark {benchmark}: ', benchmark_volatility)

    figure = plt.figure(figsize=(14, 8))

    plt.scatter(tickers, portfolio_modified['Volatility (1y)'], color='blue', label='Annulized Volatility')
    plt.axhline(y=benchmark_volatility, color='red', linestyle='--', label=benchmark)
    plt.legend()
    plt.show()
    
    print(portfolio_modified.head())
    portfolio_modified.to_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/portfolio_section_2_1.csv')

    return portfolio_modified


def max_drawdown(history_prices_path, portfolio_path, benchmark, window=252):
    
    history = pd.read_csv(history_prices_path)
    history['Date'] = pd.to_datetime(history['Date'])
    history = history.set_index('Date')

    history_prices = history.tail(window)

    portfolio = pd.read_csv(portfolio_path, index_col='Ticker')
    tickers = portfolio.index.values.tolist()

    Roll_max = history_prices[tickers].rolling(window=window, min_periods=1).max()
    Daily_Drawdown = history_prices[tickers]/Roll_max - 1.0

    MDD = Daily_Drawdown.rolling(window=window, min_periods=1).min()

    portfolio_drawdown = Daily_Drawdown.mean(axis=1)
    portfolio_mdd = MDD.mean(axis=1)

    fig, ax = plt.subplots(figsize=(14, 8))

    # Plotting the average portfolio performance
    ax.plot(portfolio_drawdown, color='red', alpha=0.6, label='Portfolio Daily Drawdown')
    ax.plot(portfolio_mdd, color='blue', linestyle='--', label='Portfolio Max Drawdown')

    ax.set_title('Portfolio Drawdown Analysis')
    ax.set_xlabel('Date')
    ax.set_ylabel('Drawdown (%)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()
    

