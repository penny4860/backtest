
import pandas as pd
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt

from src.utils import returns, drawdown, cagr, sim_leverage


if __name__ == "__main__":
    start = datetime.datetime(2009, 6, 23)
    end = datetime.datetime(2019, 1, 1)

    vfinx = web.DataReader("VFINX", "yahoo", start, end)["Adj Close"]
    upro_sim = sim_leverage(vfinx, leverage=3.0, expense_ratio=0.0092).rename("UPRO Sim")
    upro_sim.plot(title="Growth of $1: UPRO vs UPRO Sim", legend=True, figsize=(10, 6))
    plt.show()
