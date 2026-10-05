import pandas as pd
import numpy as np
from portfolio_data import parse_data, create_profile, fetch_prices_hisotry, portfolio_prices
from section_one.cum_ret_11 import cumulative_return
from section_one.section_1_1 import alpha_beta_calculation
from section_2 import annualized_volatility, max_drawdown
from section_three.sharpe_ratio import sharpe_ratio
from section_three.sortino_ratio import sortino_ratio
from section_four.corr_matrix import corr_matrix
from section_four.idiosyncratic_risk import idiosyncratic_risk_calculation

fetch_data = False
symbol_benchmark = 'SPY'

if fetch_data: 
    portfolio = parse_data(
        '/Users/okarasevic1/Documents/Portfolio Analyzer /from_2025-09-30_to_2026-05-31_MTc4MDIyMjY1OTY1Nw.csv',
        '/Users/okarasevic1/Documents/Portfolio Analyzer /ibkr.csv')

    statement_df = create_profile('/Users/okarasevic1/Documents/Portfolio Analyzer /overall_portfolio.csv')
    print(statement_df.head())

    tickers = statement_df['Ticker'].tolist()
    shares = statement_df['No. of shares'].tolist()
    data_df = fetch_prices_hisotry(tickers, 5, benchmark=symbol_benchmark)

    portfolio_prices(data_df, shares, symbol_benchmark)


# Section 1
annual_rf_rate = 0.04475
monthly_rf_rate = annual_rf_rate/12

history_path = '/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/prices_history.csv'
portfolio_path = '/Users/okarasevic1/Documents/Portfolio Analyzer /portfolio_stmnt.csv'
portfolio_histoy_path = '/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/portfolio_prices_history.csv'

cumulative_return(history_path, portfolio_histoy_path, symbol_benchmark, days=252)

beta = alpha_beta_calculation(history_path, portfolio_path, symbol_benchmark, monthly_rf_rate)
print('General Beta of the portfolio: ', beta)

# portfolio path after section 1
portfolio_sectio1_path = '/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/portfolio_section_1.csv'
portfolio_2_1 = annualized_volatility(history_path, portfolio_sectio1_path, symbol_benchmark)

# max_drawdown(history_path, portfolio_sectio1_path, symbol_benchmark, window=252/2)

portfolio_2_1_path = '/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/portfolio_section_2_1.csv'
sharpe_ratio(history_path, portfolio_histoy_path, portfolio_2_1_path, window=252/2, avg_rf_rate=monthly_rf_rate)

portfolio_3_path = '/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/section_three/portfolio_3.csv'
sortino_ratio(history_path, portfolio_histoy_path, portfolio_3_path, window=252/2, avg_rf_rate=monthly_rf_rate)

portfolio_3_path = '/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/section_three/portfolio_3.csv'
corr_matrix(history_path, '/Users/okarasevic1/Documents/Portfolio Analyzer /portfolio_stmnt.csv')
idiosyncratic_risk_calculation(history_path, portfolio_3_path, symbol_benchmark)