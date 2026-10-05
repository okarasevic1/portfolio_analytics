import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')

def cumulative_return(history_prices_path, portfolio_history_path, benchmark, days=252): 

    history_prices = pd.read_csv(history_prices_path)
    history_prices['Date'] = pd.to_datetime(history_prices['Date'])
    history_prices = history_prices.set_index('Date')
    

    # Get the history prices of Index
    benchmark_df = pd.DataFrame({
        'SPY': pd.Series(history_prices[benchmark], index=history_prices.index)
    })

    range_benchmark = benchmark_df.tail(days).copy()

    # the history prices of Portfolio
    portfolio_history = pd.read_csv(portfolio_history_path)
    portfolio_history['Date'] = pd.to_datetime(portfolio_history['Date'])
    portfolio_history = portfolio_history.set_index('Date')

    range_portfolio_history = portfolio_history.tail(days).copy()
    range_portfolio_history = range_portfolio_history.ffill()

    # Daily changes in Price (%)
    portfolio_daily_returns = range_portfolio_history.pct_change().dropna()
    benchmark_daily_returns = range_benchmark.pct_change().dropna()

    # Get the Cummulative return of the Prices changes
    portfolio_cum_return = ((1 + portfolio_daily_returns).cumprod() - 1) * 100
    benchmark_cum_return = ((1 + benchmark_daily_returns).cumprod() - 1) * 100

    # Plot
    plt.figure(figsize=(14, 8))
    plt.plot(portfolio_cum_return, color='orange', linewidth=2, label='Portfolio Performance')
    plt.plot(benchmark_cum_return, color='green', linewidth=2, label='SPY Performance')

    plt.title('Portfolio vs Benchmark Performance', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Return', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    print(f'Index {benchmark} total return in last {days} days: {benchmark_cum_return.tail(1)}%')
    print(f'Portfolio total return in last {days} days: {portfolio_cum_return.tail(1)}')

    # return portfolio_beta, portolio_return, expected_rm