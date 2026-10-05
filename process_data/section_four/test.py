import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta

ticker = 'NVO'
end = datetime.today()
start = end - timedelta(days=365)

ticker_history = yf.download([ticker, 'SPY'], start, end)['Close']
ticker_history = ticker_history.ffill()

ticker_returns = ticker_history[ticker].pct_change().dropna()
market_returns = ticker_history['SPY'].pct_change().dropna()

ones = np.ones_like(market_returns)

# x = np.column_stack([ones, market_returns])
x = np.array(market_returns).reshape(-1, 1)
y = np.array(ticker_returns.values)

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# Calculate R^2 by hands
SS_resid = np.sum((y_test - y_pred) ** 2) / len(y_test)
SS_total = np.sum((y_test - y_test.mean()) ** 2) / len(y_test)

R_2_hand = 1 - (SS_resid/SS_total)
print('R2 score calculated by hands: ', R_2_hand)
print('Standard R2 score: ', r2_score(y_test, y_pred))

print('Idiosyncratic Risk: ', (1 - R_2_hand) * 100)
