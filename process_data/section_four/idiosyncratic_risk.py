import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

def idiosyncratic_risk_calculation(history_path, portfolio_path, benchmark, window=252):

    history = pd.read_csv(history_path, index_col='Date', parse_dates=True)
    history = history.tail(window)
    history = history.ffill()
    portfolio = pd.read_csv(portfolio_path, index_col='Ticker')

    # prepare data for linear regression with shape (-1, 1)
    X = np.array(history[benchmark]).reshape(-1, 1)
    history.drop(labels=benchmark, axis=1, inplace=True)

    tickers = portfolio.index.values.tolist()

    array_idiosyncratic_risk = []
    
    for ticker in tickers:
        y = np.array(history[ticker].values)

        ticker_idiosyncratic_risk = idiosyncratic_risk(X, y)
        array_idiosyncratic_risk.append(ticker_idiosyncratic_risk)

    portfolio_modified = portfolio.copy()
    portfolio_modified['Idiosyncratic Risk'] = np.array(array_idiosyncratic_risk)

    print(portfolio_modified)

    portfolio_modified.to_csv('/Users/okarasevic1/Documents/Portfolio Analyzer /process_data/section_four/final_stmnt.csv')




def idiosyncratic_risk(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)

    return 1 - r2