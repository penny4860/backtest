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
        if self.counter % 120 == 0:
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

    spy = bt.feeds.YahooFinanceData(dataname="spy", fromdate=start, todate=end)
    tlt = bt.feeds.YahooFinanceData(dataname="tlt", fromdate=start, todate=end)

    dd, cagr, sharpe = backtest([spy], BuyAndHold)
    print(f"Max Drawdown: {dd:.2f}%, CAGR: {cagr:.2f}%, Sharpe: {sharpe:.3f}")

    dd, cagr, sharpe = backtest([tlt], BuyAndHold)
    print(f"Max Drawdown: {dd:.2f}%, CAGR: {cagr:.2f}%, Sharpe: {sharpe:.3f}")

    dd, cagr, sharpe = backtest([spy, tlt], AssetAllocation)
    print(f"Max Drawdown: {dd:.2f}%, CAGR: {cagr:.2f}%, Sharpe: {sharpe:.3f}")
