# https://teddykoker.com/2019/04/backtesting-portfolios-of-leveraged-etfs-in-python-with-backtrader/
import pandas as pd
import pandas_datareader.data as web
import datetime
import backtrader as bt
import numpy as np
from src.utils import sim_leverage

import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (10, 6) # (w, h)


class BuyAndHold(bt.Strategy):
    def next(self):
        if not self.getposition(self.data).size:
            self.order_target_percent(self.data, target=1.0)


class AssetAllocation(bt.Strategy):
    params = (
        ('equity', 0.6),
    )

    def __init__(self):
        self.UPRO = self.datas[0]
        self.TMF = self.datas[1]
        self.counter = 0

    def next(self):
        if self.counter % 20 == 0:
            self.order_target_percent(self.UPRO, target=self.params.equity)
            self.order_target_percent(self.TMF, target=(1 - self.params.equity))
        self.counter += 1


def backtest(datas, strategy, plot=False, **kwargs):
    cerebro = bt.Cerebro()
    for data in datas:
        cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addstrategy(strategy, **kwargs)
    results = cerebro.run()
    if plot:
        cerebro.plot()
    return (results[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
            results[0].analyzers.returns.get_analysis()['rnorm100'],
            results[0].analyzers.sharperatio.get_analysis()['sharperatio'])


if __name__ == '__main__':
    start = datetime.datetime(1986, 5, 19)
    end = datetime.datetime(2019, 1, 1)

    vfinx = web.DataReader("VFINX", "yahoo", start, end)["Adj Close"]
    vustx = web.DataReader("VUSTX", "yahoo", start, end)["Adj Close"]
    upro_sim = sim_leverage(vfinx, leverage=3.0, expense_ratio=0.0092).to_frame("close")
    tmf_sim = sim_leverage(vustx, leverage=3.0, expense_ratio=0.0109).to_frame("close")

    for column in ["open", "high", "low"]:
        upro_sim[column] = upro_sim["close"]
        tmf_sim[column] = tmf_sim["close"]

    upro_sim["volume"] = 0
    tmf_sim["volume"] = 0

    upro_sim = bt.feeds.PandasData(dataname=upro_sim)
    tmf_sim = bt.feeds.PandasData(dataname=tmf_sim)
    vfinx = bt.feeds.YahooFinanceData(dataname="VFINX", fromdate=start, todate=end)

    dd, cagr, sharpe = backtest([vfinx], BuyAndHold, plot=False)
    print(f"Max Drawdown: {dd:.2f}, CAGR: {cagr:.2f}, Sharpe: {sharpe:.3f}")

    dd, cagr, sharpe = backtest([upro_sim], BuyAndHold)
    print(f"Max Drawdown: {dd:.2f}%, CAGR: {cagr:.2f}%, Sharpe: {sharpe:.3f}")

    dd, cagr, sharpe = backtest([tmf_sim], BuyAndHold)
    print(f"Max Drawdown: {dd:.2f}%, CAGR: {cagr:.2f}%, Sharpe: {sharpe:.3f}")

    dd, cagr, sharpe = backtest([upro_sim, tmf_sim], AssetAllocation, plot=False, equity=0.6)
    print(f"Max Drawdown: {dd:.2f}%, CAGR: {cagr:.2f}%, Sharpe: {sharpe:.3f}")

    # optimization
    sharpes = {}
    for perc_equity in range(0, 101, 5):
        sharpes[perc_equity] = backtest([upro_sim, tmf_sim], AssetAllocation, equity=(perc_equity / 100.0))[2]

    series = pd.Series(sharpes)
    ax = series.plot(title="UPRO/TMF allocation vs Sharpe")
    ax.set_ylabel("Sharpe Ratio")
    ax.set_xlabel("Percent Portfolio UPRO");
    print(f"Max Sharpe of {series.max():.3f} at {series.idxmax()}% UPRO")
    dd, cagr, sharpe = backtest([upro_sim, tmf_sim], AssetAllocation, plot=False, equity=0.4)
    print(f"Max Drawdown: {dd:.2f}%\nCAGR: {cagr:.2f}%\nSharpe: {sharpe:.3f}")

