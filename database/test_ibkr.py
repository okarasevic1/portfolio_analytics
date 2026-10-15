from ib_async import *
import pandas as pd
import asyncio


async def main(ib:IB):

    contract_quotes = {
        'FUSD' : ['LSEETF', 'USD', '271826693'],
        'TDIV' : ['LSE', 'USD', '350073445']
    }

    df = pd.DataFrame({})

    for sym, spec in contract_quotes.items():

        contract = Stock(
            symbol=sym,
            exchange=spec[0],
            currency=spec[1]
        )

        contract.conId= spec[2]

        await ib.qualifyContractsAsync(contract)

        bars = await ib.reqHistoricalDataAsync(
            contract=contract, 
            endDateTime='',
            durationStr='5 Y',
            barSizeSetting='1 day',
            whatToShow='Trades',
            useRTH=False
        )

        if len(df) < 0:
            df = util.df(bars)

            df = df.rename({
                    'date':'date'.capitalize(),
                    'open':'open'.capitalize(),
                    'high':'high'.capitalize(),
                    'low':'low'.capitalize(),
                    'close':'close'.capitalize(),
                    'volume':'volume'.capitalize(),
                }, axis=1)

            df['Ticker'] = sym
            df.set_index(keys='Date', inplace=True)

        else: 
            prices_df = util.df(bars)
            
            prices_df = prices_df.rename({
                    'date':'date'.capitalize(),
                    'open':'open'.capitalize(),
                    'high':'high'.capitalize(),
                    'low':'low'.capitalize(),
                    'close':'close'.capitalize(),
                    'volume':'volume'.capitalize(),
                }, axis=1)

            prices_df['Ticker'] = sym
            prices_df.set_index(keys='Date', inplace=True)

            df = pd.concat([df, prices_df])

    print(df)

    ib.disconnect()


async def contract_details(ib:IB):

    contract = Contract(
        secType='STK',
        secIdType='ISIN',
        secId='NL0011683594',
        exchange='SMART'
    )

    details = await ib.reqContractDetailsAsync(contract)
    print(details)


async def MAIN():
    ib = IB()
    await ib.connectAsync("127.0.0.1", 7497, clientId=10)

    try:
        details = await contract_details(ib)
        prices = await main(ib)
    finally:
        ib.disconnect()


asyncio.run(MAIN())
