# https://teddykoker.com/2019/04/simulating-historical-performance-of-leveraged-etfs-in-python/

import pandas as pd
import pandas_datareader.data as web
import datetime

from src.utils import returns, drawdown


if __name__ == "__main__":
    # 1. get raw data
    start = datetime.datetime(1970, 1, 1)
    end = datetime.datetime(2019, 1, 1)
    spy = web.DataReader("SPY", "yahoo", start, end)["Adj Close"]

    # 2. 가격변동
    spy_returns = returns(spy).rename("SPY")

    # 3. drawdown : 낙폭
    spy_drawdown = drawdown(spy)

    # 최대낙폭
    print("Max Drawdown")
    print(f"SPY: {spy_drawdown.idxmin()} {spy_drawdown.min():.2f}%")
    print(spy_drawdown.min())

    spy_returns.plot(title="Growth of $1: SPY vs UPRO", legend=True, figsize=(10,6))
    spy_drawdown.plot.area(color="red", title="UPRO drawdown", figsize=(10,6));

    import matplotlib.pyplot as plt
    plt.show()
