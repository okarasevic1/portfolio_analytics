import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


portfolio_stmnt = pd.read_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /portfolio_stmnt.csv', index_col='Ticker')

portfolio_by_sectors = portfolio_stmnt.groupby('Sector').agg({
    'Gross Total':'sum',
    'Gross P/L':'sum'
})

print(portfolio_by_sectors)

f, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.pie(x=portfolio_by_sectors['Gross Total'], labels=portfolio_by_sectors.index.values, autopct='%1.1f%%', labeldistance=1)
ax2.bar(x=portfolio_by_sectors.index.values, height=portfolio_by_sectors['Gross P/L'], width=0.7, color='orange', label='Unrealized PnL by Sectors')

ax1.set_title('Value of each Sector')
ax2.set_xlabel('Sector Name')
ax2.set_ylabel('P&L')

plt.legend()
plt.tight_layout()
plt.show()


