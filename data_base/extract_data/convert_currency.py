import pandas as pd
import duckdb
import yfinance as yf


class ConvertCurrncies:

    def load_exchange_rates(self, currencies:list, start:str, end:str):

        symbols = [] # normalized ticker for yahho finance
        for ticker in currencies:
            symbol = f'{ticker}USD=X'
            symbols.append(symbol)

        exhange_rates = yf.download(symbols, start=start, end=end)['Close']
        
        # convert into 1D columns and rename
        exhange_rates.columns = currencies

        exhange_rates = exhange_rates.reset_index()
        exhange_rates['Date'] = exhange_rates['Date'].dt.date

        # unpivot dataFrame 
        exhange_rates = pd.melt(
            exhange_rates, 
            id_vars=['Date'],
            value_vars=currencies,
            var_name='currency',
            value_name='rates'
        )

        return exhange_rates
