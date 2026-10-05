import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def corr_matrix(history_path, portfolio_path): 

    history = pd.read_csv(history_path, index_col='Date', parse_dates=True)
    portfolio = pd.read_csv(portfolio_path, index_col='Ticker')
    

    stock_filter = portfolio['Sector'] != 'ETF'
    stocks = portfolio[stock_filter].index.tolist()

    history = history[stocks].resample('W').last()
    returns = history.pct_change().dropna()

    corr_m = returns.corr().round(2)

    filter_corr = corr_m.where(corr_m > 0.6)

    mean_corr = corr_m.mean()
    print(mean_corr)

    heatmap = sns.heatmap(filter_corr, annot=True, cmap='coolwarm')
    heatmap.set_title('Correlation Heatmap', fontdict={'fontsize':12}, pad=12)

    plt.tight_layout()
    plt.show()


