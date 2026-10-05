import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Визначаємо часовий проміжок
end = datetime.today()
start = end - timedelta(days=(365*5))

# Завантажуємо дані для обох тікерів одночасно
# yfinance поверне зручну таблицю, де колонками будуть 'GOOG' та 'QQQ'
data = yf.download(['FISV', '^GSPC'], start=start, end=end)['Close']

# --- РОЗРАХУНОК ЩОДЕННОЇ БЕТИ ---
daily_returns = data.pct_change().dropna()

daily_covariance = daily_returns['FISV'].cov(daily_returns['^GSPC'])
daily_variance = daily_returns['^GSPC'].var()
daily_beta = daily_covariance / daily_variance

# --- РОЗРАХУНОК МІСЯЧНОЇ БЕТИ ---
# Ресемплуємо ціни за кінець місяця, а вже потім рахуємо відсоткову зміну
monthly_data = data.resample('ME').last()
monthly_returns = monthly_data.pct_change().dropna()

monthly_covariance = monthly_returns['FISV'].cov(monthly_returns['^GSPC'])
monthly_variance = monthly_returns['^GSPC'].var()
monthly_beta = monthly_covariance / monthly_variance

# --- ВИВЕДЕННЯ РЕЗУЛЬТАТІВ ---
print(f'FISV Daily Beta:   {daily_beta:.6f}')
print(f'FISV Monthly Beta: {monthly_beta:.6f}')