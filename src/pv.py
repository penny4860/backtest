import pandas as pd
from pandas_datareader import data
import yfinance
yfinance.pdr_override()

TICKERS = ['TLT', "SPY"]


def common_dates(assets):
    for i, asset in enumerate(assets):
        if i == 0:
            dates = asset.df.index.copy()
        else:
            dates = dates[dates.isin(asset.df.index)]
    return dates


class Asset(object):
    def __init__(self, df, ticker):
        self.df = df
        self.ticker = ticker
        self.n_stocks = 0

    @classmethod
    def from_yahoo(cls, ticker):
        df = data.get_data_yahoo(ticker)[["Adj Close"]]
        return Asset(df, ticker)

    def get_price(self, d):
        return float(self.df.loc[str(d)])

    def get_value(self, d):
        return self.n_stocks * self.get_price(d)

    # Todo: 거래세, 세금 추가
    def set_value(self, d, value):
        self.n_stocks = int(value / self.get_price(d))
        remain_value = value - self.n_stocks * self.get_price(d)
        return remain_value

    def get_ticker(self):
        return self.ticker


class Agent(object):
    def __init__(self, assets, ratios=[0.5, 0.5], init_value=10000):
        self.cash = init_value
        self.dates = common_dates(assets)
        self.assets = assets
        self.ratios = ratios

    def _get_value(self, d):
        value = self.cash
        for asset in self.assets:
            value += asset.get_value(d)
        return value

    def _rebalance(self, d):
        value = self._get_value(d)

        self.cash = 0
        for asset, ratio in zip(self.assets, self.ratios):
            target_value = value * ratio
            balance = asset.set_value(d, target_value)
            self.cash += balance

    def run(self, rebalance=60):
        # Todo : 주기를 1달단위로
        for asset in self.assets:
            asset.n_stocks = 0
        self._rebalance(self.dates[0])

        values = []
        for i, d in enumerate(self.dates):
            if rebalance is not None:
                if i % rebalance == 0:
                    self._rebalance(d)
            values.append(self._get_value(d))
        return pd.DataFrame(values, index=self.dates)


if __name__ == "__main__":
    spy = Asset.from_yahoo("SPY")
    tlt = Asset.from_yahoo("TLT")
    agent = Agent(assets=[spy, tlt], ratios=[0.5, 0.5])
    values = agent.run(60)
    print(values)
    # 2020-07-29  49157.654274
