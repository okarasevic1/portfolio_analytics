import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def sharpe_ratio(history_prices_path, portfolio_history_path, portfolio_path, window=252, avg_rf_rate=0.0):
    '''The function for Sharpe Ration Calculation'''

    # process the data
    history_prices = pd.read_csv(history_prices_path)
    history_prices['Date'] = pd.to_datetime(history_prices['Date'])
    history_prices.set_index('Date', inplace=True)

    portfolio_history = pd.read_csv(portfolio_history_path)
    portfolio_history['Date'] = pd.to_datetime(portfolio_history['Date'])
    portfolio_history.set_index('Date', inplace=True)

    # get the list of the tickers
    portfolio_df = pd.read_csv(portfolio_path, index_col='Ticker')
    tickers = portfolio_df.index.values.tolist()
    modified_portfolio = portfolio_df.copy()

    # take the data from specific range, by default is 252
    history_prices = history_prices.tail(window)
    portfolio_history = portfolio_history.tail(window)

    # resample df's from daily to monthly
    history_prices = history_prices.resample('ME').last()
    portfolio_history = portfolio_history.resample('ME').last()

    # changes in df's overtime 
    tickers_return = history_prices[tickers].pct_change().dropna()
    portfolio_return = portfolio_history.pct_change().dropna()

    # average return for each ticker and portfolio
    avg_tickers_return = tickers_return[tickers].mean()
    avg_portfolio_return = portfolio_return.mean()

    std_tickers = tickers_return[tickers].std()
    std_portfolio = portfolio_return.std()

    # Calculate annual sharpe ration for stocks
    tickers_sharpe_ratio = ((avg_tickers_return[tickers] - avg_rf_rate) / std_tickers) * np.sqrt(12)
    modified_portfolio['Sharpe Ratio'] = tickers_sharpe_ratio
    print(modified_portfolio)
    modified_portfolio.to_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/section_three/portfolio_3.csv')

    # For Portfolio
    portfolio_sharpe_ratio = ((avg_portfolio_return - avg_rf_rate) / std_portfolio) * np.sqrt(12)
    print('General Sharpe Ratio for Portfolio: ', portfolio_sharpe_ratio)


