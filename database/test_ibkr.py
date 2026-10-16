from ib_async import IB, Contract, util
import asyncio


async def contract_details(ib, isin):
    contract = Contract(
        secType="STK",
        secIdType="ISIN",
        secId=isin,
        exchange="SMART"
    )

    details = await ib.reqContractDetailsAsync(contract)

    if not details:
        raise ValueError(f"No contract found for ISIN: {isin}")

    print(f"Found {len(details)} contracts:")

    for d in details:
        c = d.contract
        print(
            f"Symbol: {c.symbol}, "
            f"ConId: {c.conId}, "
            f"Exchange: {c.primaryExchange}, "
            f"Currency: {c.currency}"
        )

    return details



async def main(ib, details):

    contract = details[0].contract

    bars = await ib.reqHistoricalDataAsync(
        contract,
        endDateTime="",
        durationStr="1 Y",
        barSizeSetting="1 day",
        whatToShow="TRADES",
        useRTH=True,
        formatDate=1
    )

    if not bars:
        print(f"No historical prices found for {contract.symbol}")
        return None

    df = util.df(bars)

    df["symbol"] = contract.symbol
    df["conId"] = contract.conId
    df["currency"] = contract.currency

    return df


async def MAIN():
    ib = IB()

    await ib.connectAsync(
        "127.0.0.1",
        7497,
        clientId=10,
        readonly=True
    )

    try:
        details = await contract_details(
            ib,
            "US91324P1021"
        )

        prices = await main(ib, details)

        if prices is not None:
            print(prices)

    finally:
        ib.disconnect()


if __name__ == "__main__":
    asyncio.run(MAIN())