import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

def alpha_beta_calculation(history_prices_path, portfolio_path, benchmark, monthly_rfr): 

    # Get general information Ticker, Shares, Total Value
    portfolio = pd.read_csv(portfolio_path, index_col='Ticker')
    tickers = portfolio.index.values.tolist()
    shares = portfolio['No. of shares'].values
    portfolio_total_value = portfolio['Gross Total'].sum()

    # Load Data Set 
    history_prices = pd.read_csv(history_prices_path)
    history_prices['Date'] = pd.to_datetime(history_prices['Date'])
    history_prices = history_prices.set_index('Date')

    # Resample Data into Monthly for Alpha and Beta calculation. (5Y data for Monthly Period)
    history_prices = history_prices.ffill()
    history_prices = history_prices.resample('ME').last()

    # Returns DataFrame
    monthly_returns = history_prices.pct_change().dropna()
    benchmark_return = monthly_returns[benchmark].copy()
    monthly_returns.drop(labels=benchmark, axis=1, inplace=True)
    
    # portfolio_return = history_prices.mul(shares, axis=1).sum(axis=1).mean()

    # Calculate Alpha and Beta for each individual stock
    portfolio_modified = portfolio.copy()

    # Beta Calculation 
    market_variance = benchmark_return.var()
    betas = monthly_returns[tickers].apply(lambda x: x.cov(benchmark_return) / market_variance)

    avg_tickers_return = monthly_returns[tickers].mean()
    avg_market_return = benchmark_return.mean()
    alphas = avg_tickers_return - (monthly_rfr + betas * (avg_market_return - monthly_rfr))

    portfolio_modified['Beta'] = betas
    portfolio_modified['Alpha'] = alphas

    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5)) # Added figsize for better readability

    # Plotting Beta
    ax1.bar(tickers, betas, width=0.5, color='blue', label='Beta')
    ax1.set_title('Beta of each stock')
    ax1.set_xlabel('Ticker')
    ax1.set_ylabel('Beta')
    ax1.tick_params(axis='x', rotation=45, labelsize=8)
    ax1.legend()

    # Plotting Alpha
    ax2.bar(tickers, alphas, width=0.5, color='red', label='Alpha')
    ax2.set_title('Alpha of each stock')
    ax2.set_xlabel('Ticker')
    ax2.set_ylabel('Alpha')
    ax2.tick_params(axis='x', rotation=45, labelsize=8)
    ax2.legend()

    plt.tight_layout()
    plt.show()

    # calculate general beta of the portfolio
    weights = portfolio_modified['Gross Total'] / portfolio_total_value
    beta = np.dot(betas, weights)

    print(portfolio_modified)
    portfolio_modified.to_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/portfolio_section_1.csv')

    return beta
